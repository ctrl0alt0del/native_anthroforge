#include "skin_gap_internal.hpp"
#include "anthroforge/skin_validation.h"

namespace af::skin {
static std::vector<int64_t> diagnostic_faces(const Mesh& mesh) {
    const auto count=int(mesh.offsets.size())-1;
    bool quads=true;
    for(int i=0;i<count;++i) quads&=mesh.offsets[i+1]-mesh.offsets[i]==4;
    if(!quads) return {mesh.triangles.data(),mesh.triangles.data()+mesh.triangles.size()};
    std::vector<int64_t> result; result.reserve(size_t(count)*6);
    for(int half=0;half<2;++half) for(int i=0;i<count;++i) {
        const auto* q=mesh.corners.data()+mesh.offsets[i];
        result.insert(result.end(),{q[0],q[half?2:1],q[half?3:2]});
    }
    return result;
}
static void intersections(const Mesh& mesh,uint64_t budget,int64_t* pairs,int capacity,int64_t* stats,uint64_t cancel) {
    check_cancel(cancel); const auto faces=diagnostic_faces(mesh); kernel::af_diag::Task task;
    task.cancelled.external=cancel?&reinterpret_cast<Cancellation*>(cancel)->cancelled:nullptr;
    const int code=kernel::af_diag::run(task,mesh.vertices.data(),int(mesh.vertices.rows()),
        faces.data(),int(faces.size()/3),int64_t(budget),pairs,capacity);
    check_cancel(cancel);
    if(code) throw std::runtime_error("Intersection diagnostic memory limit; quality unknown.");
    stats[0]=task.crossings; stats[1]=task.contacts; stats[2]=task.tests;
}
struct Clearance { std::vector<double> signed_distance,distance; };
static Clearance clearance(const Mesh& mesh,const double* samples,int count,uint64_t cancel) {
    const auto faces=diagnostic_faces(mesh); const M4 frame=M4::Identity();
    std::unique_ptr<kernel::AfWorld,decltype(&kernel::af_world_destroy)> world(new kernel::AfWorld(),kernel::af_world_destroy);
    kernel::af_world_add_collider(world.get(),mesh.vertices.data(),faces.data(),int(faces.size()/3),0,0,0,frame.data(),frame.data());
    kernel::af_world_commit(world.get()); Clearance result; result.signed_distance.resize(count); result.distance.resize(count);
    for(int i=0;i<count;++i) {
        check_cancel(cancel); double closest[3],normal[3]; int blocker,contained;
        kernel::af_world_nearest_points(world.get(),samples+3*i,1,closest,normal,&result.distance[i],&blocker,&contained);
        result.signed_distance[i]=(V3(closest)-V3(samples+3*i)).dot(V3(normal));
    }
    return result;
}
static void clearance_summary(const Mesh& rest,const Clearance& before,const Clearance& after,double* output) {
    const double scale=(rest.vertices.colwise().maxCoeff()-rest.vertices.colwise().minCoeff()).maxCoeff();
    std::fill(output,output+6,0); output[0]=double(after.distance.size()); output[3]=INFINITY;
    for(size_t i=0;i<after.distance.size();++i) {
        output[1]+=after.signed_distance[i]<-scale*1e-6; output[2]+=before.signed_distance[i]<-scale*1e-6;
        output[3]=std::min(output[3],after.signed_distance[i]);
        output[4]=std::max(output[4],before.signed_distance[i]-after.signed_distance[i]);
    }
    auto sorted=after.distance; std::sort(sorted.begin(),sorted.end());
    const double index=.95*double(sorted.size()-1); const auto low=size_t(index),high=std::min(low+1,sorted.size()-1);
    output[5]=sorted[low]+(sorted[high]-sorted[low])*(index-double(low));
}
}
int af_skin_intersections(uint64_t handle,uint64_t budget,int64_t* witnesses,int capacity,int64_t* stats,uint64_t cancel) {
    try {
        if(!witnesses||!stats||capacity<0||capacity>4096||budget>INT64_MAX) throw std::runtime_error("Invalid intersection buffers.");
        af::skin::intersections(*af::mesh(handle),budget,witnesses,capacity,stats,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_anatomy_clearance(uint64_t reference,uint64_t current,const double* rest_samples,
    const double* samples,int count,double* statistics,uint64_t cancel) {
    try {
        if(!rest_samples||!samples||!statistics||count<1) throw std::runtime_error("Missing skin clearance samples.");
        if(!Eigen::Map<const af::Vertices>(rest_samples,count,3).allFinite()||!Eigen::Map<const af::Vertices>(samples,count,3).allFinite())
            throw std::runtime_error("Nonfinite skin clearance samples.");
        af::check_cancel(cancel); const auto rest=af::mesh(reference),updated=af::mesh(current);
        const auto before=af::skin::clearance(*rest,rest_samples,count,cancel),after=af::skin::clearance(*updated,samples,count,cancel);
        af::skin::clearance_summary(*rest,before,after,statistics); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
