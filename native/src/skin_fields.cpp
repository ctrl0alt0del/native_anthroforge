#include "skin_fields.hpp"
#include "mesh_internal.hpp"
#include <algorithm>

namespace af::skin {
static void blend(Fields& fields) {
    const auto& g=fields.grid; const double radius=g.length*.951539268851356/220;
    auto& full=fields.values[1]; fields.values[3].resize(g.count);
    for(uint64_t i=0;i<g.count;++i) {
        if((i&8191)==0) check_cancel(g.cancel);
        const double required=fields.values[0][i],w=std::clamp(.5+.5*(full[i]-required)/radius,0.0,1.0);
        full[i]=required*(1-w)+full[i]*w+radius*w*(1-w);
        fields.values[3][i]=required+fields.values[2][i]*(full[i]-required);
    }
}
Fields prepare(const Source& source,const double* settings,int resolution,uint64_t budget,uint64_t cancel) {
    Fields result; result.grid=grid(source,settings,resolution,budget,cancel);
    std::copy(settings,settings+4,result.ratios.begin());
    const auto& g=result.grid; const auto sampled=raster(g,source);
    result.values[0]=exterior(g,sampled.all,g.length*4.75769634425678/220,g.length*settings[0]);
    result.values[1]=exterior(g,sampled.skeletal,g.length*9.51539268851356/220,g.length*(settings[0]+settings[1]));
    result.values[2]=collagen(g,sampled.seeds,g.length*settings[2],g.length*settings[3]);
    blend(result); result.grid.cancel=0; return result;
}
}
