#include "skin_annuli.hpp"
#include "anthroforge/skin_annuli.h"
#include <set>
namespace af::skin_annuli {
static void validate(const AFSkinAnnulusInput& input) {
    if(input.loop_count<0||input.loop_count>2048||input.pair_count<0||input.pair_count>input.loop_count/2)
        throw std::runtime_error("Invalid annulus loop or pair count.");
    if((input.loop_count&&(!input.samples||!input.symmetric))||(input.pair_count&&!input.pairs))
        throw std::runtime_error("Missing annulus guide data.");
    std::set<int> used;
    for(int i=0;i<2*input.pair_count;++i)
        if(input.pairs[i]<0||input.pairs[i]>=input.loop_count||!used.insert(input.pairs[i]).second)
            throw std::runtime_error("Annulus pairs require distinct valid source loops.");
}
static Loop capture(const AFSkinAnnulusInput& input,int index) {
    Loop out; out.source=index; out.symmetric=input.symmetric[index]!=0;
    out.points.resize(skin_loops::sample_count,3); out.normals.resize(skin_loops::sample_count,3);
    for(int i=0;i<skin_loops::sample_count;++i) {
        const double* sample=input.samples+(index*skin_loops::sample_count+i)*6;
        out.points.row(i)=V3(sample); out.normals.row(i)=V3(sample+3);
    }
    if(!out.points.allFinite()||!out.normals.allFinite()) throw std::runtime_error("Nonfinite annulus guide input.");
    out.perimeter=skin_loops::perimeter(out.points); out.center=out.points.colwise().mean();
    if(out.perimeter<1e-12||!std::isfinite(out.perimeter)) throw std::runtime_error("Annulus loop has invalid perimeter.");
    return out;
}
static Patches build(Context& context,const AFSkinAnnulusInput& input) {
    Patches result; result.reserve(input.pair_count);
    for(int i=0;i<input.pair_count;++i) {
        check_cancel(context.cancel); const int first=input.pairs[2*i],second=input.pairs[2*i+1];
        auto patch=choose(context,capture(input,first),capture(input,second));
        patch.first=first; patch.second=patch.mode==2?-1:second; result.push_back(std::move(patch));
    }
    mirror_pairs(context,result); return result;
}
}
uint64_t af_skin_annuli(uint64_t mesh,const AFSkinAnnulusInput* input,uint64_t cancel) {
    try {
        if(!input) throw std::runtime_error("Missing annulus request.");
        af::skin_annuli::validate(*input); af::check_cancel(cancel);
        const auto source=af::mesh(mesh); af::skin_loops::Context context(*source,input->plane,cancel);
        return af::skin_annuli::retain(af::skin_annuli::build(context,*input));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
