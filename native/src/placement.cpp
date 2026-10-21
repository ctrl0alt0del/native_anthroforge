#include "mesh_internal.hpp"
#include "anthroforge/drawing.h"

namespace af::placement {
struct Target { std::shared_ptr<Mesh> mesh; M4 frame; };
static std::vector<Target> targets(int count,const uint64_t* handles,const double* frames) {
    if(count<0||(count&&(!handles||!frames))) throw std::runtime_error("Invalid placement surfaces.");
    std::vector<Target> result;
    for(int i=0;i<count;++i) result.push_back({mesh(handles[i]),Eigen::Map<const M4>(frames+i*16)});
    return result;
}
static V3 position(const std::vector<Target>& targets,const double* query,uint64_t cancel) {
    const V3 origin(query),direction(query+3); double nearest=std::numeric_limits<double>::infinity(); V3 result;
    if(!origin.allFinite()||!direction.allFinite()||direction.norm()<1e-15||!std::isfinite(query[6]))
        throw std::runtime_error("Invalid confirmed placement ray or offset.");
    for(const auto& target:targets) {
        check_cancel(cancel); double hit[10];
        if(!pick_surface(*target.mesh,target.frame,origin,direction,hit)||hit[0]>=nearest) continue;
        nearest=hit[0]; result=surface_snap(*target.mesh,target.frame,int(hit[2]),V3(hit+4),query[6]);
    }
    if(!std::isfinite(nearest)) throw std::runtime_error("No exterior surface under the confirmed placement ray.");
    return result;
}
}
int af_confirm_samples(int count,const uint64_t* meshes,const double* matrices,int samples,
    const double* points,const double* placements,double* output,uint64_t cancel) {
    try {
        if(samples<0||samples>100000||(samples&&(!points||!placements||!output))) throw std::runtime_error("Invalid placement samples.");
        const auto targets=af::placement::targets(count,meshes,matrices);
        for(int i=0;i<samples;++i) {
            af::check_cancel(cancel); std::copy(points+i*4,points+i*4+4,output+i*4);
            if(placements[i*8+7]!=0) { Eigen::Map<af::V3> result(output+i*4); result=af::placement::position(targets,placements+i*8,cancel); }
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
