#include "skin_fields.hpp"
#include "mesh_internal.hpp"
#include <algorithm>
#include <cmath>

namespace af::skin {
struct Levels { std::vector<int8_t> cells; std::array<bool,16> present{}; };
static Levels quantize(const Grid& g,const std::vector<float>& seeds) {
    Levels result; result.cells.assign(g.count,-1);
    for(uint64_t i=0;i<g.count;++i) {
        if((i&8191)==0) check_cancel(g.cancel);
        if(!std::isfinite(seeds[i])) continue;
        const auto level=int8_t(std::nearbyint(std::clamp(seeds[i],0.0f,1.0f)*15.0f));
        result.cells[i]=level; result.present[level]=true;
    }
    return result;
}
static void merge(const Grid& g,Values& result,const Values& distances,double inner,double width,double minimum) {
    for(uint64_t i=0;i<g.count;++i) {
        if((i&8191)==0) check_cancel(g.cancel);
        double f=width<=0?double(distances[i]>inner):std::clamp((distances[i]-inner)/width,0.0,1.0);
        f=f*f*(3.0-2.0*f); result[i]=std::min(result[i],minimum+(1.0-minimum)*f);
    }
}
Values collagen(const Grid& g,const std::vector<float>& seeds,double inner,double width) {
    const auto levels=quantize(g,seeds); Values result(g.count,1.0); Mask mask;
    for(int level=0;level<15;++level) {
        check_cancel(g.cancel);
        if(!levels.present[level]) continue;
        mask.resize(g.count);
        for(uint64_t i=0;i<g.count;++i) {
            if((i&8191)==0) check_cancel(g.cancel);
            mask[i]=levels.cells[i]==level;
        }
        const auto distances=distance(g,dilate(g,mask));
        merge(g,result,distances,inner,width,double(float(level)/15.0f));
    }
    return result;
}
}
