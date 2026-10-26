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
static skin_quads::Quads capture(const Mesh& mesh,uint64_t cancel) {
    const size_t count=mesh.offsets.size()-1; std::vector<int> regions(count,0),guides(count,-1);
    return skin_quads::capture(mesh,regions.data(),guides.data(),cancel);
}
static void report(const Assembly& result,AFSkinStitchOutput& out) {
    if(out.capacity<int(result.transitions.size())||(out.capacity&&!out.transitions)||!out.warning||out.warning_capacity<4096)
        throw std::runtime_error("Missing skin stitch report buffers.");
    out.count=int(result.transitions.size());
    for(size_t i=0;i<result.transitions.size();++i) write(result.transitions[i],out.transitions+i*9);
    const auto size=std::min(result.warning.size(),size_t(out.warning_capacity-1));
    std::copy(result.warning.begin(),result.warning.begin()+size,out.warning); out.warning[size]='\0';
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
uint64_t af_skin_stitch(uint64_t mesh,uint64_t annuli,const double* plane,int allow_unstitched,AFSkinStitchOutput* output,uint64_t cancel) {
    try {
        if(!output||(allow_unstitched!=0&&allow_unstitched!=1)) throw std::runtime_error("Invalid skin stitch request.");
        const auto patches=af::skin_annuli::get(annuli); const auto source=af::mesh(mesh);
        auto result=af::skin_stitch::assemble(af::skin_stitch::capture(*source,cancel),*patches,
            af::skin_loops::plane(plane),allow_unstitched!=0,cancel);
        af::skin_stitch::report(result,*output);
        return af::skin_quads::retain(af::skin_quads::complete(std::move(result.mesh),cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
