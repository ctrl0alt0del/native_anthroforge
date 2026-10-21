#include "stacking_internal.hpp"

namespace af::stacking {
struct Footprint { double* lines; int capacity,count=0; int64_t polygons=0; bool truncated=false; };
static kernel::Vec on_surface(const pair::Side& side,int face,kernel::Vec bary) {
    kernel::Vec triangle[3];
    for(int j=0;j<3;++j) triangle[j]=side.own[size_t(side.faces[size_t(3*face+j)])];
    return pair::weighted(triangle,bary);
}
static void append_footprint(Footprint& out,const pair::Side& side,const layer::Mask& mask) {
    ++out.polygons;
    for(size_t i=0;i<mask.barycentrics.size();++i) {
        if(out.count+2>out.capacity) { out.truncated=true; return; }
        const auto a=on_surface(side,mask.face,mask.barycentrics[i]);
        const auto b=on_surface(side,mask.face,mask.barycentrics[(i+1)%mask.barycentrics.size()]);
        std::memcpy(out.lines+3*out.count,&a,sizeof(a)); ++out.count;
        std::memcpy(out.lines+3*out.count,&b,sizeof(b)); ++out.count;
    }
}
static void footprint(const Engine& engine,uint64_t cover,uint64_t provider,Footprint& out,std::atomic<bool>& cancel) {
    const auto& state=engine.state;
    const auto& side=state.bases.sides.at(state.bases.indices.at(cover));
    for(const auto& mask:layer::material_masks(state,cover,cancel)) {
        pair::require(!cancel,"PAIR_CANCELLED");
        if(mask.provider==provider) append_footprint(out,side,mask);
        if(out.truncated) break;
    }
}
}
int af_stack_footprint(uint64_t handle,uint64_t cover,uint64_t provider,double* lines,
    int capacity,int64_t* summary,uint64_t cancel) {
    try {
        if(!handle||!lines||!summary||capacity<2||capacity>32768) throw std::runtime_error("Invalid footprint storage.");
        auto& engine=*reinterpret_cast<af::stacking::Engine*>(handle); std::lock_guard<std::mutex> lock(engine.mutex);
        std::atomic<bool> idle{false}; auto& cancelled=cancel?reinterpret_cast<af::Cancellation*>(cancel)->cancelled:idle;
        af::stacking::Footprint out{lines,capacity}; af::stacking::footprint(engine,cover,provider,out,cancelled);
        summary[0]=out.count; summary[1]=out.polygons; summary[2]=out.truncated; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
