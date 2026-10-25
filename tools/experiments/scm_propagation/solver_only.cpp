// Isolated experiment: exact production SQP stage, no planner or warm-start remapping.
#include "../../../native/src/routing_solve.cpp"
#include <Eigen/LU>

namespace af {
void check_cancel(uint64_t token) {
    if(token) throw std::runtime_error("This isolated adapter accepts synchronous uncancelled input only.");
}
}
namespace af::routing {
void configure_piqp(kernel::AfV3SqpJob&,uint64_t) {
    throw std::runtime_error("Solver-only experiment currently uses the Custom backend.");
}
void trace_begin(Trace*,const std::vector<Span>&) {}
void trace_step(Trace*,const kernel::AfV3SqpCoordinator&) {}
}

namespace {
using namespace af;
using namespace af::routing;
thread_local std::string failure;

kernel::Bounds bounds(const double* vertices,int count,const M4& matrix) {
    auto result=kernel::empty_bounds();
    for(int i=0;i<count;++i) {
        const V3 value=(matrix*V3(vertices+3*i).homogeneous()).head<3>();
        for(int axis=0;axis<3;++axis) {
            result.lo[axis]=std::min(result.lo[axis],value[axis]);
            result.hi[axis]=std::max(result.hi[axis],value[axis]);
        }
    }
    return result;
}
void add(World& world,const double* vertices,int count,const int64_t* faces,int triangles,
         const double* frame,int owner) {
    const M4 matrix=Eigen::Map<const M4>(frame);
    if(!matrix.allFinite()||!matrix.fullPivLu().isInvertible()) throw std::runtime_error("Invalid surface frame.");
    const M4 inverse=matrix.inverse(); int closed=0;
    if(!kernel::af_batch_add(*world.collision,vertices,count,faces,triangles,owner,
                             matrix.data(),inverse.data(),closed)) throw std::runtime_error("Invalid surface.");
    world.collision->items.back().collider=owner;
    world.collision->items.back().bounds=bounds(vertices,count,matrix);
}
void snapshot(World& world) {
    std::vector<double> vertices; std::vector<int64_t> triangles;
    for(const auto& item:world.collision->items) {
        const int64_t offset=int64_t(vertices.size()/3);
        for(const auto& vertex:item.mesh->vertices) {
            const Vec p=kernel::af_transform(item.matrix,vertex);
            vertices.insert(vertices.end(),{p.x,p.y,p.z});
        }
        for(const auto index:item.mesh->triangles) triangles.push_back(offset+index);
        world.owners.insert(world.owners.end(),item.mesh->triangles.size()/3,item.owner);
    }
    if(!triangles.empty()) world.snapshot.reset(kernel::create_snapshot(vertices.data(),triangles.data(),int(triangles.size()/3)));
}
void scales(World& world,double radius) {
    auto total=kernel::empty_bounds(); double squared=0,coordinate=1;
    for(const auto& item:world.collision->items) total=kernel::merge_bounds(total,item.bounds);
    if(!world.collision->items.empty()) for(int i=0;i<3;++i) {
        squared+=std::pow(total.hi[i]-total.lo[i],2);
        coordinate=std::max({coordinate,std::abs(total.lo[i]),std::abs(total.hi[i])});
    }
    world.radius=radius; world.length=std::max({std::sqrt(squared),radius,1e-6});
    world.coordinate=std::max(coordinate,world.length);
    world.floor=std::max(1e-9*world.length,8*double(std::numeric_limits<float>::epsilon())*world.coordinate);
    world.slack=std::max(world.floor,0.01*radius);
}
Reference reference(const double* points,int count,bool seed_reference) {
    Reference result; result.pins={0,count-1};
    const V3 a(points),b(points+3*(count-1));
    for(int i=0;i<count;++i) {
        const double t=double(i)/(count-1);
        const V3 p=seed_reference?V3(points+3*i):(V3(a*(1-t)+b*t));
        result.points.push_back({p.x(),p.y(),p.z()}); result.parameters.push_back(t);
    }
    return result;
}
int run(World& world,const double* points,int count,int first,int last,int cap,bool seed_reference,
        double* output,int64_t* counters,double* measures) {
    if(count<3||count>4096||cap<1||cap>1000) throw std::runtime_error("Invalid solver budget.");
    if(first<0||last<0||size_t(std::max(first,last))>world.collision->items.size()) throw std::runtime_error("Invalid owners.");
    double records[26]{};
    Input input{records,2,M4::Identity(),M4::Identity(),{first,last},{count,cap,0,world.radius},0};
    const auto ref=reference(points,count,seed_reference); auto prepared=spans(input,world,ref);
    auto& seed=prepared.front().seed; seed.clear();
    for(int i=0;i<count;++i) seed.push_back({points[3*i],points[3*i+1],points[3*i+2]});
    const bool accepted=solve(prepared,input,counters,measures);
    for(int i=0;i<count;++i) {
        const auto p=prepared.front().output[i]; output[3*i]=p.x; output[3*i+1]=p.y; output[3*i+2]=p.z;
    }
    return int(accepted);
}
}

extern "C" __declspec(dllexport) void* scm_solver_scene(const double* const* vertices,const int* counts,
    const int64_t* const* faces,const int* triangles,const double* matrices,int count,double radius) {
    try {
        if(count<0||radius<0) throw std::runtime_error("Invalid scene.");
        auto world=std::make_unique<af::routing::World>();
        for(int i=0;i<count;++i) add(*world,vertices[i],counts[i],faces[i],triangles[i],matrices+16*i,i+1);
        af::routing::kernel::af_world_commit(world->collision.get()); scales(*world,radius); snapshot(*world);
        return world.release();
    } catch(const std::exception& error) { failure=error.what(); return nullptr; }
}
extern "C" __declspec(dllexport) int scm_solver_run(void* handle,const double* points,int count,
    int first,int last,int cap,int seed_reference,double* output,int64_t* counters,double* measures) {
    try { return run(*static_cast<af::routing::World*>(handle),points,count,first,last,cap,seed_reference!=0,output,counters,measures); }
    catch(const std::exception& error) { failure=error.what(); return -1; }
}
extern "C" __declspec(dllexport) void scm_solver_release(void* handle) {
    delete static_cast<af::routing::World*>(handle);
}
extern "C" __declspec(dllexport) const char* scm_solver_error() { return failure.c_str(); }

// Diagnostic only: enumerate every intersecting segment, without an SQP/planner call.
extern "C" __declspec(dllexport) int scm_surface_contacts(void* handle,const double* points,
    int count,int* output) {
    try {
        const auto& world=*static_cast<af::routing::World*>(handle);
        const double tolerance=std::max(1e-9,1e-9*world.length);
        const auto& surfaces=world.collision->items;
        for(int i=0;i<count-1;++i) for(size_t j=0;j<surfaces.size();++j) {
            const af::routing::Vec a{points[3*i],points[3*i+1],points[3*i+2]};
            const af::routing::Vec b{points[3*i+3],points[3*i+4],points[3*i+5]};
            output[size_t(i)*surfaces.size()+j]=!af::routing::kernel::af_instance_validation_row(surfaces[j],a,b,0,0,0,tolerance).clear;
        }
        return 0;
    } catch(const std::exception& error) { failure=error.what(); return 1; }
}
