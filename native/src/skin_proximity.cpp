#include "skin_ownership.hpp"
#include "skin_density.hpp"
#include "anthroforge/skin_topology.h"
#include <numeric>
namespace af::skin_ownership {
static std::vector<int> selected_vertices(const AFSkinOwnershipInput& in,const uint8_t* enabled) {
    std::vector<int> result;
    for(int source=0;source<in.source_count;++source) if(enabled[source])
        for(int i=in.vertex_offsets[source];i<in.vertex_offsets[source+1];++i) result.push_back(i);
    return result;
}
static double weight(double distance,double diagonal) {
    const double value=std::clamp((distance-.01*diagonal)/std::max(.04*diagonal,1e-12),0.,1.);
    return 1-value*value*(3-2*value);
}
static void proximity(const Mesh& mesh,const Samples& points,const std::vector<int>& selected,
                      const double* lengths,double* output,double* weights,double* stats,uint64_t cancel) {
    const PointIndex index(points.points,selected,cancel); int active=0;
    const double diagonal=std::max((mesh.vertices.colwise().maxCoeff()-mesh.vertices.colwise().minCoeff()).norm(),1e-12);
    for(int i=0;i<mesh.vertices.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        if(!std::isfinite(lengths[i])||lengths[i]<0) throw std::runtime_error("Invalid proximity input length.");
        const auto hit=index.nearest(points.points,mesh.vertices.row(i));
        weights[i]=hit.first<0?0:weight(std::sqrt(hit.second),diagonal);
        output[i]=lengths[i]/std::sqrt(1+.5*weights[i]); active+=weights[i]>.01;
    }
    stats[0]=double(selected.size()); stats[1]=active; stats[2]=.01*diagonal; stats[3]=.05*diagonal; stats[4]=1.5;
}
}
int af_skin_proximity(uint64_t handle,const AFSkinOwnershipInput* input,const uint8_t* enabled,const double* lengths,
                     double* output,double* weights,double* statistics,uint64_t cancel) {
    try {
        if(!input||!enabled||!lengths||!output||!weights||!statistics) throw std::runtime_error("Missing proximity buffers.");
        const auto points=af::skin_ownership::samples(*input,cancel);
        const auto selected=af::skin_ownership::selected_vertices(*input,enabled);
        af::skin_ownership::proximity(*af::mesh(handle),points,selected,lengths,output,weights,statistics,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_base_target(uint64_t handle,const double* lengths,int target,int reserved,int* result,uint64_t cancel) {
    try {
        if(!lengths||!result||target<1||target>500000||reserved<0) throw std::runtime_error("Invalid base topology target.");
        const auto mesh=af::mesh(handle); std::vector<double> areas(mesh->vertices.rows());
        af::skin_density::areas(*mesh,areas.data(),cancel); double edge=0;
        for(int i=0;i<mesh->vertices.rows();++i) {
            if(!std::isfinite(lengths[i])||lengths[i]<0) throw std::runtime_error("Invalid topology target lengths.");
            edge=std::max(edge,lengths[i]);
        }
        const double predicted=std::nearbyint(std::accumulate(areas.begin(),areas.end(),0.)/std::max(edge*edge,1e-20))+reserved;
        *result=int(std::min(double(target),std::max(1000.,predicted))); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
