#include "anthroforge/painting.h"
#include "painting_internal.hpp"
#include <Eigen/LU>
namespace af::painting {
Prepared& prepared(uint64_t handle) {
    if(!handle) throw std::runtime_error("Missing prepared paint surface.");
    return *reinterpret_cast<Prepared*>(handle);
}
static Occluder occluder(uint64_t handle,const M4& frame) {
    const M4 inverse=frame.inverse();
    if(!frame.allFinite()||!inverse.allFinite()) throw std::runtime_error("Invalid paint surface transform.");
    return {mesh(handle),inverse};
}
static std::vector<Occluder> obstacles(uint64_t target,const M4& frame,const uint64_t* handles,const double* frames,int count) {
    if(count<0||count>10000) throw std::runtime_error("Invalid paint visibility scene.");
    std::vector<Occluder> result{occluder(target,frame)};
    for(int i=0;i<count;++i) result.push_back(occluder(handles[i],M4(frames+16*i)));
    return result;
}
}
uint64_t af_paint_prepare(uint64_t target,uint64_t reference,int source,int count,const double* frame,const double* view,
    const uint64_t* others,const double* frames,int other_count,uint64_t cancel) {
    try {
        auto result=std::make_unique<af::painting::Prepared>(); result->target=af::mesh(target); result->count=count;
        result->reference=reference?af::mesh(reference):nullptr;
        result->mapping=af::painting::correspondence(*result->target,result->reference.get(),source!=0,count,cancel);
        const auto camera=af::painting::view(view);
        const auto occluders=af::painting::obstacles(target,af::M4(frame),others,frames,other_count);
        af::painting::project(*result,af::M4(frame),camera,occluders,cancel);
        return reinterpret_cast<uint64_t>(result.release());
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_paint_release(uint64_t handle) { delete reinterpret_cast<af::painting::Prepared*>(handle); }
uint64_t af_paint_bytes(uint64_t handle) {
    try {
        const auto& data=af::painting::prepared(handle);
        uint64_t size=sizeof(data)+data.projected.size()*sizeof(double)+data.visible.capacity();
        for(const auto& row:data.mapping) size+=sizeof(row)+row.size()*(sizeof(std::pair<int64_t,double>)+4*sizeof(void*));
        return size;
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_paint_stroke(uint64_t handle,const double* baseline,const double* samples,int count,const double* settings,double* values,uint64_t cancel) {
    try { return reinterpret_cast<uint64_t>(af::painting::stroke(af::painting::prepared(handle),baseline,samples,count,settings,values,cancel).release()); }
    catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
