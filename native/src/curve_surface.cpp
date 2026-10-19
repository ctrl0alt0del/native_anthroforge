#include "curve_surface_internal.hpp"

int af_curve_surface_layout(const AfSurfaceRow* data,int count,int exact,int strips,double* alignment,int* across,uint64_t cancel) {
    try {
        if(!alignment||(count>1&&!across)||strips<0||strips>256) throw std::runtime_error("Invalid surface layout buffers.");
        auto rows=af::curve_surface::inputs(data,count,exact!=0,cancel);
        af::curve_surface::align(rows,alignment,cancel);
        const auto prepared=exact?af::curve_surface::common_stations(rows,cancel):rows;
        const auto counts=af::curve_surface::density(prepared,strips,exact!=0);
        std::copy(counts.begin(),counts.end(),across); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
uint64_t af_curve_surface_geometry(const AfSurfaceRow* data,int count,int exact,const int* across,int kind,int resolution,int close_across,int flip,uint64_t cancel) {
    try {
        const auto rows=af::curve_surface::inputs(data,count,exact!=0,cancel);
        if(kind==1&&count==1) return af::retain(af::curve_surface::patch(rows.front(),resolution,flip!=0,cancel));
        if(kind!=0) throw std::runtime_error("Invalid surface construction mode.");
        return af::retain(af::curve_surface::loft(exact?af::curve_surface::common_stations(rows,cancel):rows,across,close_across!=0,flip!=0,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
