#include "skin_stitch.hpp"
#include "anthroforge/skin_stitch.h"
namespace af::skin_stitch {
static Vertices capture(const double* values,int count) {
    if(!values||count<3||count>4096) throw std::runtime_error("Skin transition requires 3–4096 points per boundary.");
    Vertices points=Eigen::Map<const Vertices>(values,count,3);
    if(!points.allFinite()||skin_loops::perimeter(points)<1e-12) throw std::runtime_error("Skin transition requires finite nonzero rings.");
    return points;
}
static void write(const Transition& value,double* out) {
    const std::array<double,9> values{double(value.mode),double(value.reason),double(value.shift),double(value.candidates),
        double(value.intersections),double(value.boundary),double(value.annulus),value.p95,value.maximum};
    std::copy(values.begin(),values.end(),out);
}
}
uint64_t af_skin_transition(const AFSkinTransitionInput* input,double* diagnostics,uint64_t cancel) {
    try {
        if(!input||!diagnostics||!std::isfinite(input->diagonal)||input->diagonal<=0)
            throw std::runtime_error("Missing skin transition inputs or positive diagonal.");
        af::check_cancel(cancel); const auto plane=af::skin_loops::plane(input->plane);
        auto result=af::skin_stitch::transition(af::skin_stitch::capture(input->first,input->first_count),
            af::skin_stitch::capture(input->second,input->second_count),plane,input->diagonal,cancel);
        af::skin_stitch::write(result,diagnostics);
        return af::skin_quads::retain(af::skin_quads::complete(std::move(result.mesh),cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
