// Captures owned SCP inputs and applies the addon's unchanged attachment kernel.
#include "mesh_internal.hpp"
#include "anthroforge/attachments.h"
#include <chrono>
#include <cstring>
struct Vec { double x,y,z; };
static Vec add(Vec a,Vec b) { return {a.x+b.x,a.y+b.y,a.z+b.z}; }
static Vec sub(Vec a,Vec b) { return {a.x-b.x,a.y-b.y,a.z-b.z}; }
static Vec mul(Vec a,double s) { return {a.x*s,a.y*s,a.z*s}; }
static double dot(Vec a,Vec b) { return a.x*b.x+a.y*b.y+a.z*b.z; }
static double norm(Vec a) { return std::sqrt(dot(a,a)); }
static Vec cross(Vec a,Vec b) { return {a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x}; }
static constexpr int af_requested_workers=1;
#define AF_EXPORT extern "C" AF_API
// Keep compiler accommodations inside the unchanged migration-kernel boundary.
#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wlogical-op-parentheses"
#pragma clang diagnostic ignored "-Wunknown-pragmas"
#elif defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wparentheses"
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#pragma GCC diagnostic ignored "-Wunknown-pragmas"
#elif defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable:4068)
#endif
#include "../migration/attachment_wave_reference.hpp"
#if defined(__clang__)
#pragma clang diagnostic pop
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif

namespace af {
struct Capture {
    std::shared_ptr<Mesh> child,parent;
    M4 child_world,parent_world,child_geometry,parent_geometry;
    std::shared_ptr<Surface> surface;
    int parent_mode,child_mode,locked,flow,index=-1;
    V3 anchor=V3::Zero(); Hit hit;
    double* output;
};
static M3 basis(const V3& tangent,const V3& normal) {
    const auto value=af_basis({tangent.x(),tangent.y(),tangent.z()},{normal.x(),normal.y(),normal.z()});
    double raw[9]; af_basis_matrix(value,raw);
    return Eigen::Map<Eigen::Matrix<double,3,3,Eigen::RowMajor>>(raw);
}
static V3 child_candidate(const Capture& capture,int index) {
    if(capture.child_mode==2) return capture.child_world.block<3,1>(0,3);
    if(capture.child_mode==1) return point(capture.child_geometry,capture.child->vertices.row(index));
    V3 local=V3::Zero();
    const auto first=capture.child->offsets.at(index),last=capture.child->offsets.at(index+1);
    for(auto i=first;i<last;++i) local+=capture.child->vertices.row(capture.child->corners[i]).transpose();
    return point(capture.child_geometry,local/double(last-first));
}
static void consider(Capture& capture,int index,double& best) {
    const V3 anchor=child_candidate(capture,index);
    Hit hit;
    if(capture.surface) hit=nearest(*capture.surface,anchor);
    else { hit.point=capture.parent_world.block<3,1>(0,3); hit.distance=(anchor-hit.point).squaredNorm(); }
    if(hit.distance>=best) return;
    best=hit.distance; capture.hit=hit; capture.anchor=anchor; capture.index=index;
}
static void select_anchor(Capture& capture) {
    double best=std::numeric_limits<double>::infinity();
    if(capture.child_mode==2) { consider(capture,-1,best); return; }
    if(!capture.child) throw std::runtime_error("Child has no geometry; use Object Origin.");
    const int count=capture.child_mode==1?int(capture.child->vertices.rows()):int(capture.child->offsets.size())-1;
    if(capture.locked>=count) throw std::runtime_error("Locked anchor is invalid; clear or replace it.");
    if(capture.locked>=0) { consider(capture,capture.locked,best); return; }
    for(int i=0;i<count;++i) consider(capture,i,best);
}
static void store_vector(double* output,const V3& value) {
    Eigen::Map<V3> target(output); target=value;
}
static V3 binding_point(const Mesh& mesh,const double* binding) {
    V3 result=V3::Zero();
    for(int i=0;i<3;++i) {
        const double index=binding[i];
        if(index<0||index>=mesh.vertices.rows()||std::floor(index)!=index)
            throw std::runtime_error("Invalid attachment vertex index.");
        result+=mesh.vertices.row(int(index)).transpose()*binding[3+i];
    }
    return result;
}
static void store_hit(double* output,const Mesh& mesh,const Hit& hit) {
    for(int i=0;i<3;++i) output[i]=mesh.triangles(hit.triangle,i);
    store_vector(output+3,hit.weights);
}
static M3 initial_basis(const Capture& capture) {
    if(!capture.surface) return rotation(capture.parent_world);
    const auto tri=capture.parent->triangles.row(capture.hit.triangle);
    const V3 a=capture.surface->vertices.row(tri[0]),b=capture.surface->vertices.row(tri[1]);
    const V3 c=capture.surface->vertices.row(tri[2]);
    return basis(b-a,(b-a).cross(c-a));
}
static M3 capture_flow(Capture& capture,const M3& stable) {
    if(!capture.flow||!capture.surface) return stable;
    const V3 normal=stable.col(2), axis=rotation(capture.parent_world).col(0);
    V3 tangent=axis-normal*normal.dot(axis);
    tangent=tangent.norm()>1e-6?V3(tangent.normalized()):V3(stable.col(0));
    const double size=(capture.surface->vertices.colwise().maxCoeff()-capture.surface->vertices.colwise().minCoeff()).maxCoeff();
    for(double factor:{0.02,0.05,0.1}) {
        const Hit probe=nearest(*capture.surface,capture.hit.point+tangent*size*factor);
        if((probe.point-capture.hit.point).norm()<=1e-6) continue;
        store_hit(capture.output+6,*capture.parent,probe);
        V3 delta=probe.point-capture.hit.point; delta-=normal*delta.dot(normal);
        return basis(delta,normal);
    }
    return stable;
}
static void write_capture(Capture& capture) {
    std::fill(capture.output,capture.output+28,0.);
    std::fill(capture.output,capture.output+3,-1.); std::fill(capture.output+6,capture.output+9,-1.);
    const M3 stable=initial_basis(capture);
    const V3 hint=rotation(capture.parent_world).transpose()*stable.col(0);
    if(capture.surface) store_hit(capture.output,*capture.parent,capture.hit);
    const M3 frame=capture_flow(capture,stable), child_rotation=rotation(capture.child_world);
    store_vector(capture.output+12,hint);
    store_vector(capture.output+15,frame.transpose()*(capture.anchor-capture.hit.point));
    store_vector(capture.output+18,point(capture.child_world.inverse(),capture.anchor));
    store_vector(capture.output+21,child_rotation.transpose()*frame.col(0));
    store_vector(capture.output+24,child_rotation.transpose()*frame.col(2));
    capture.output[27]=capture.index;
}
static void initialize_surface(Capture& capture) {
    if(!capture.parent_mode) return;
    if(!capture.parent) throw std::runtime_error("Parent has no geometry; use Object Origin.");
    capture.surface=std::make_shared<Surface>(*capture.parent,capture.parent_geometry);
}
static AfAttachmentScpOp operation(const double* binding,const M4& child,int mode,int follows,int flow) {
    AfAttachmentScpOp op{}; op.parent=0; op.child=1; op.surface=mode?0:-1;
    op.follow=follows; op.mode=flow;
    for(int i=0;i<3;++i) { op.tri[i]=int64_t(binding[i]); op.flow_tri[i]=int64_t(binding[6+i]); }
    std::copy(binding+3,binding+6,op.weights); std::copy(binding+9,binding+12,op.flow_weights);
    std::copy(binding+12,binding+15,op.hint); std::copy(binding+15,binding+18,op.offset);
    std::copy(binding+18,binding+21,op.origin); std::copy(binding+21,binding+24,op.child_tangent);
    std::copy(binding+24,binding+27,op.child_normal);
    const V3 scale=scales(child); std::copy(scale.data(),scale.data()+3,op.scale);
    return op;
}
static AfAttachmentSurface parent_surface(const std::shared_ptr<Mesh>& mesh,const double* offset) {
    AfAttachmentSurface surface{}; surface.owner=0; surface.vertex_count=mesh?int(mesh->vertices.rows()):0;
    const M4 identity=M4::Identity(); std::copy(identity.data(),identity.data()+16,surface.relative);
    surface.relative[3]=offset[0]; surface.relative[7]=offset[1]; surface.relative[11]=offset[2];
    surface.rotation[0]=surface.rotation[4]=surface.rotation[8]=1.; return surface;
}
static bool apply_one(const Mesh* parent,const AfAttachmentSurface& surface,const AfAttachmentScpOp& op,
                       const M4& parent_world,double* child_world) {
    double matrices[32], rotations[18]; const int status[2]{0,0};
    std::copy(parent_world.data(),parent_world.data()+16,matrices);
    std::copy(child_world,child_world+16,matrices+16);
    Eigen::Map<Eigen::Matrix<double,3,3,Eigen::RowMajor>> rp(rotations),rc(rotations+9);
    rp=rotation(parent_world); rc=rotation(Eigen::Map<const M4>(child_world));
    const bool ok=af_run_scp(op,&surface,parent?parent->vertices.data():nullptr,matrices,rotations,status);
    if(ok) std::copy(matrices+16,matrices+32,child_world);
    return ok;
}
}
int af_capture(uint64_t child,uint64_t parent,const double* cw,const double* pw,const double* co,
               const double* po,int parent_mode,int child_mode,int locked,int flow,double* binding) {
    try {
        af::Capture capture;
        capture.child=child?af::mesh(child):nullptr; capture.parent=parent?af::mesh(parent):nullptr;
        capture.child_world=Eigen::Map<const af::M4>(cw); capture.parent_world=Eigen::Map<const af::M4>(pw);
        capture.child_geometry=af::geometry_matrix(cw,co); capture.parent_geometry=af::geometry_matrix(pw,po);
        capture.parent_mode=parent_mode; capture.child_mode=child_mode; capture.locked=locked;
        capture.flow=flow; capture.output=binding;
        af::initialize_surface(capture); af::select_anchor(capture); af::write_capture(capture); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_anchor_points(uint64_t parent,const double* cw,const double* pw,const double* po,
                     const double* binding,double* output) {
    try {
        af::V3 target=af::V3::Zero();
        if(binding[0]>=0) {
            auto mesh=af::mesh(parent);
            target=af::binding_point(*mesh,binding);
            target+=Eigen::Map<const af::V3>(po);
        }
        af::store_vector(output,af::point(Eigen::Map<const af::M4>(cw),Eigen::Map<const af::V3>(binding+18)));
        af::store_vector(output+3,af::point(Eigen::Map<const af::M4>(pw),target));
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_propagate(int count,const uint64_t* meshes,const int* parents,double* matrices,const double* offsets,
    const double* bindings,const int* modes,const int* follows,const int* flows,const int* active,int* status,uint64_t cancel) {
    try {
        for(int i=0;i<count;++i) {
            af::check_cancel(cancel); const int p=parents[i];
            if(p<0||!active[i]) continue;
            if(p>=i||status[p]) { status[i]=1; continue; }
            auto mesh=meshes[p]?af::mesh(meshes[p]):nullptr;
            auto op=af::operation(bindings+28*i,Eigen::Map<const af::M4>(matrices+16*i),modes[i],follows[i],flows[i]);
            if(modes[i]&&!mesh) { status[i]=1; continue; }
            const auto surface=af::parent_surface(mesh,offsets+3*p);
            status[i]=!af::apply_one(mesh.get(),surface,op,Eigen::Map<const af::M4>(matrices+16*p),matrices+16*i);
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}

namespace af {
static Capture point_surface(uint64_t handle,const double* frame,bool prepare) {
    Capture value;
    value.parent=mesh(handle); value.parent_world=Eigen::Map<const M4>(frame);
    if(!value.parent_world.allFinite()||!value.parent_world.fullPivLu().isInvertible())
        throw std::runtime_error("Invalid anatomical surface transform.");
    value.parent_geometry=value.parent_world; value.parent_mode=1; value.child_mode=2;
    value.child_world=M4::Identity(); value.flow=0; value.locked=-1;
    if(prepare) initialize_surface(value);
    return value;
}
static std::vector<Capture> point_surfaces(int count,const uint64_t* meshes,const double* frames,bool prepare,uint64_t cancel) {
    if(count<1||count>100000||!meshes||!frames) throw std::runtime_error("Point attachments need anatomical surfaces.");
    std::vector<Capture> result; result.reserve(count);
    for(int i=0;i<count;++i) { check_cancel(cancel); result.push_back(point_surface(meshes[i],frames+16*i,prepare)); }
    return result;
}
static int capture_point(std::vector<Capture>& surfaces,const V3& point,int forced,double* binding) {
    if(!point.allFinite()||forced<-1||forced>=int(surfaces.size())) throw std::runtime_error("Invalid point capture input.");
    double best=std::numeric_limits<double>::infinity(); int owner=-1;
    for(int i=0;i<int(surfaces.size());++i) {
        if(forced>=0&&forced!=i) continue;
        auto& value=surfaces[i]; value.child_world.block<3,1>(0,3)=point;
        const double previous=best; consider(value,-1,best);
        if(best<previous) owner=i;
    }
    if(owner<0) throw std::runtime_error("No valid anatomical attachment surface.");
    surfaces[owner].output=binding; write_capture(surfaces[owner]); return owner;
}
static void require_point_binding(const Mesh& mesh,const double* binding) {
    for(int i=0;i<28;++i) if(!std::isfinite(binding[i])) throw std::runtime_error("Nonfinite point binding.");
    binding_point(mesh,binding);
    if(std::abs(binding[3]+binding[4]+binding[5]-1)>1e-6)
        throw std::runtime_error("Point binding weights must sum to one.");
    for(int i=3;i<6;++i) if(binding[i]<-1e-6||binding[i]>1+1e-6)
        throw std::runtime_error("Point binding weights are outside the surface triangle.");
}
static M4 resolve_point(const Capture& value,const double* binding) {
    require_point_binding(*value.parent,binding); int64_t triangle[3];
    for(int i=0;i<3;++i) triangle[i]=int64_t(binding[i]);
    const double zero[3]{0,0,0}; const auto surface=parent_surface(value.parent,zero);
    Eigen::Matrix<double,3,3,Eigen::RowMajor> rotation_matrix=rotation(value.parent_world);
    AfBasis resolved; Vec location;
    if(!af_surface_frame(surface,value.parent->vertices.data(),value.parent_world.data(),
        rotation_matrix.data(),triangle,binding+3,resolved,location)) throw std::runtime_error("Point attachment no longer resolves.");
    double raw[9]; af_basis_matrix(resolved,raw); M4 result=M4::Identity();
    result.block<3,3>(0,0)=Eigen::Map<Eigen::Matrix<double,3,3,Eigen::RowMajor>>(raw);
    result.block<3,1>(0,3)=V3(location.x,location.y,location.z)+result.block<3,3>(0,0)*V3(binding+15);
    return result;
}
}
int af_point_attachment_capture(int surface_count,const uint64_t* meshes,const double* frames,int count,
    const double* points,const int* forced,int* targets,double* bindings,uint64_t cancel) {
    try {
        if(count<1||count>1000000||!points||!forced||!targets||!bindings) throw std::runtime_error("Invalid point capture buffers.");
        auto surfaces=af::point_surfaces(surface_count,meshes,frames,true,cancel);
        for(int i=0;i<count;++i) {
            af::check_cancel(cancel);
            targets[i]=af::capture_point(surfaces,af::V3(points+3*i),forced[i],bindings+28*i);
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_point_attachment_resolve(int surface_count,const uint64_t* meshes,const double* frames,int count,
    const int* targets,const double* bindings,double* output,uint64_t cancel) {
    try {
        if(count<1||count>1000000||!targets||!bindings||!output) throw std::runtime_error("Invalid point resolution buffers.");
        const auto surfaces=af::point_surfaces(surface_count,meshes,frames,false,cancel);
        for(int i=0;i<count;++i) {
            af::check_cancel(cancel);
            if(targets[i]<0||targets[i]>=surface_count) throw std::runtime_error("Point binding target is missing.");
            Eigen::Map<af::M4> frame(output+16*i); frame=af::resolve_point(surfaces[targets[i]],bindings+28*i);
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}

#include "path_internal.hpp"
int af_attachment_goal_points(const double* frames,int count,const double* local_frame,
    double offset,double* output,uint64_t cancel) {
    try {
        if(!frames||!local_frame||!output||count<1||count>262144||!std::isfinite(offset))
            throw std::runtime_error("Invalid attachment goal frame batch.");
        const af::M4 local=Eigen::Map<const af::M4>(local_frame);
        if(!local.allFinite()||!local.fullPivLu().isInvertible()) throw std::runtime_error("Singular goal frame.");
        const af::M4 inverse=local.inverse();
        for(int i=0;i<count;++i) {
            af::check_cancel(cancel); const af::M4 frame=Eigen::Map<const af::M4>(frames+16*i);
            af::store_vector(output+3*i,af::point(inverse,af::point(frame,af::V3(0,0,offset))));
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
namespace af {
struct CurveCapture {
    std::shared_ptr<Path> source;
    std::vector<V3> points;
    std::vector<int> knots,pins,forced;
    int nodes=0;
};
static int knot_sample(const Path& path,int knot) {
    const auto it=std::lower_bound(path.parameters.begin(),path.parameters.end(),double(knot));
    if(it==path.parameters.end()||std::abs(*it-knot)>1e-8)
        throw std::runtime_error("Attachment path must retain every authored knot.");
    return int(it-path.parameters.begin());
}
static CurveCapture curve_capture(uint64_t handle,const double* records,int count,const double* frame) {
    if(!records||!frame||count<2) throw std::runtime_error("Invalid curve attachment inputs.");
    CurveCapture result; result.source=path(handle); result.nodes=int(result.source->parameters.size());
    const M4 world=Eigen::Map<const M4>(frame);
    if(!world.allFinite()||!world.fullPivLu().isInvertible()) throw std::runtime_error("Invalid curve transform.");
    result.forced.resize(result.nodes,-1); result.points.reserve(result.nodes+3*count);
    for(int i=0;i<result.nodes;++i) result.points.push_back(point(world,V3(result.source->samples.data()+11*i)));
    for(int i=0;i<count;++i) {
        result.knots.push_back(knot_sample(*result.source,i));
        for(int offset:{0,3,6}) result.points.push_back(point(world,V3(records+13*i+offset)));
    }
    return result;
}
static void curve_pins(CurveCapture& value,const int* pins,const int* parents,int count,int surfaces) {
    if(count<1||count>int(value.knots.size())||!pins||!parents) throw std::runtime_error("Invalid fiber anchors.");
    for(int i=0;i<count;++i) {
        if(pins[i]<0||pins[i]>=int(value.knots.size())||parents[i]<-1||parents[i]>=surfaces)
            throw std::runtime_error("Fiber anchor requires an authored knot and anatomical surface.");
        const int index=value.knots[pins[i]];
        if(value.forced[index]>=0) throw std::runtime_error("Duplicate fiber anchor.");
        value.pins.push_back(index); value.forced[index]=parents[i];
    }
}
static void curve_owner_weights(CurveCapture& value,std::vector<Capture>& surfaces,int* owners,double* weights,uint64_t cancel) {
    std::vector<int> nearest(value.nodes); std::vector<double> positions(3*value.nodes); double binding[28];
    for(int i=0;i<value.nodes;++i) {
        check_cancel(cancel); store_vector(positions.data()+3*i,value.points[i]);
        nearest[i]=capture_point(surfaces,value.points[i],value.forced[i],binding);
    }
    if(af_attachment_weights(positions.data(),nearest.data(),value.nodes,value.pins.data(),int(value.pins.size()),
        value.source->closed,owners,weights,cancel)) throw std::runtime_error(af_last_error());
    for(size_t i=0;i<value.knots.size()*3;++i) {
        const int sample=value.knots[i/3],row=value.nodes+int(i);
        std::copy_n(owners+2*sample,2,owners+2*row); std::copy_n(weights+2*sample,2,weights+2*row);
    }
}
static void capture_influences(const CurveCapture& value,std::vector<Capture>& surfaces,const int* owners,double* output,uint64_t cancel) {
    for(size_t row=0;row<value.points.size();++row) {
        check_cancel(cancel);
        for(int slot=0;slot<2;++slot) {
            double* binding=output+(2*row+slot)*28; std::fill_n(binding,28,0.0);
            if(owners[2*row+slot]>=0) capture_point(surfaces,value.points[row],owners[2*row+slot],binding);
        }
    }
}
static void retain_pins(const CurveCapture& value,const int* knots,const double* retained,int count,double* bindings) {
    if(!retained) return;
    for(int i=0;i<count;++i) {
        const double* record=retained+28*i;
        if(record[0]<0) continue;
        std::copy_n(record,28,bindings+56*value.knots[knots[i]]);
        std::copy_n(record,28,bindings+56*(value.nodes+knots[i]*3));
    }
}
static V3 blended_point(const std::vector<Capture>& surfaces,const int* owners,const double* weights,const double* bindings) {
    V3 result=V3::Zero(); double total=0;
    for(int slot=0;slot<2;++slot) {
        if(!std::isfinite(weights[slot])||weights[slot]<0||weights[slot]>1) throw std::runtime_error("Invalid attachment influence.");
        if(!weights[slot]) continue;
        if(owners[slot]<0||owners[slot]>=int(surfaces.size())) throw std::runtime_error("Missing attachment influence surface.");
        result+=weights[slot]*resolve_point(surfaces[owners[slot]],bindings+28*slot).block<3,1>(0,3);
        total+=weights[slot];
    }
    if(std::abs(total-1)>1e-9) throw std::runtime_error("Attachment influences must sum to one.");
    return result;
}
static void retain_field_pin(int row,int target,const double* record,int* owners,double* weights,double* bindings) {
    owners[2*row]=target; owners[2*row+1]=-1;
    weights[2*row]=1; weights[2*row+1]=0;
    std::copy_n(record,28,bindings+56*row);
    std::fill_n(bindings+56*row+28,28,0.0);
}
static void attached_tangents(Samples& samples,bool closed) {
    for(size_t i=0;i<samples.size();++i) {
        const size_t next=i+1<samples.size()?i+1:(closed?0:i);
        const size_t before=i?i-1:(closed?samples.size()-1:i);
        const V3 difference=samples[next].position-samples[before].position;
        if(difference.norm()>1e-20) samples[i].tangent=difference.normalized();
    }
}
static bool attached_positions(Samples& samples,const double* points,const M4& inverse,uint64_t cancel) {
    V3 first=V3::Zero(); bool varied=false;
    for(size_t i=0;i<samples.size();++i) {
        check_cancel(cancel); const V3 position=point(inverse,V3(points+3*i));
        const V3 delta=position-samples[i].position;
        if(i==0) first=delta;
        varied=varied||(delta-first).squaredNorm()>1e-28;
        samples[i].position=position;
    }
    return varied;
}
}
int af_curve_attachment_capture(int count,const uint64_t* meshes,const double* frames,uint64_t path,
    const double* records,int knots,const double* world,const int* pins,const int* parents,int pin_count,const double* retained,
    int* owners,double* weights,double* bindings,uint64_t cancel) {
    try {
        if(!owners||!weights||!bindings) throw std::runtime_error("Missing curve attachment outputs.");
        auto value=af::curve_capture(path,records,knots,world);
        auto surfaces=af::point_surfaces(count,meshes,frames,true,cancel);
        af::curve_pins(value,pins,parents,pin_count,count);
        af::curve_owner_weights(value,surfaces,owners,weights,cancel);
        af::capture_influences(value,surfaces,owners,bindings,cancel);
        af::retain_pins(value,pins,retained,pin_count,bindings); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_blended_attachment_resolve(int surfaces,const uint64_t* meshes,const double* frames,int count,
    const int* owners,const double* weights,const double* bindings,double* points,uint64_t cancel) {
    try {
        if(count<1||count>1000000||!owners||!weights||!bindings||!points) throw std::runtime_error("Invalid blended binding buffers.");
        const auto prepared=af::point_surfaces(surfaces,meshes,frames,false,cancel);
        for(int i=0;i<count;++i) {
            af::check_cancel(cancel);
            af::store_vector(points+3*i,af::blended_point(prepared,owners+2*i,weights+2*i,bindings+56*i));
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_attachment_retain_pins(uint64_t handle,int knots,const int* pins,const int* targets,const double* records,
    int count,int* owners,double* weights,double* bindings) {
    try {
        if(count<1||knots<2||!pins||!targets||!records||!owners||!weights||!bindings)
            throw std::runtime_error("Invalid retained fiber anchors.");
        const auto path=af::path(handle); const int nodes=int(path->parameters.size());
        for(int i=0;i<count;++i) {
            if(pins[i]<0||pins[i]>=knots||targets[i]<0) throw std::runtime_error("Invalid retained fiber anchor target.");
            af::retain_field_pin(af::knot_sample(*path,pins[i]),targets[i],records+28*i,owners,weights,bindings);
            af::retain_field_pin(nodes+3*pins[i],targets[i],records+28*i,owners,weights,bindings);
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
uint64_t af_attached_path(uint64_t handle,const double* points,const double* world,uint64_t cancel) {
    try {
        const auto source=af::path(handle); const af::M4 inverse=Eigen::Map<const af::M4>(world).inverse();
        af::EvaluatedPath value{af::read_samples(source->samples.data(),int(source->parameters.size())),source->parameters};
        if(af::attached_positions(value.samples,points,inverse,cancel)) {
            af::attached_tangents(value.samples,source->closed); af::curve_frames(value.samples,source->closed,cancel,true);
        }
        return af::retain_path(af::make_path(value,source->closed,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
int af_attached_controls(const double* records,int count,const double* points,const double* world,double* output) {
    try {
        if(count<2||!records||!points||!world||!output) throw std::runtime_error("Invalid attached control buffers.");
        const af::M4 inverse=Eigen::Map<const af::M4>(world).inverse();
        std::copy_n(records,count*13,output);
        for(int i=0;i<count;++i) {
            for(int slot=0;slot<3;++slot) af::store_vector(output+13*i+3*slot,af::point(inverse,af::V3(points+9*i+3*slot)));
            output[13*i+11]=int(output[13*i+11])%4; output[13*i+12]=int(output[13*i+12])%4;
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
