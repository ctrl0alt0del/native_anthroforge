#include "skin_reconstruction.hpp"

namespace af::skin {
static std::array<int,6> occupied(const Fields& fields,uint64_t cancel) {
    const auto& g=fields.grid; std::array<int,6> result{g.shape[0],g.shape[1],g.shape[2],-1,-1,-1};
    for(uint64_t i=0;i<g.count;++i) {
        if((i&8191)==0) check_cancel(cancel);
        if(fields.values[3][i]<0) continue;
        const auto c=coordinates(g,i);
        for(int a=0;a<3;++a) { result[a]=std::min(result[a],c[a]-2); result[a+3]=std::max(result[a+3],c[a]+2); }
    }
    if(result[3]<0) throw std::runtime_error("Skin has no occupied envelope.");
    return result;
}
static double precision(Scene& scene,const Fields& fields,const std::vector<float>& coarse) {
    const auto& g=fields.grid; const double reach=g.length*3*9.51539268851356/220;
    const double transform[]{g.origin[0],g.origin[1],g.origin[2],g.voxel}; double result[2]{};
    if(kernel::af_skin_gap_precision_field(&scene,coarse.data(),g.shape.data(),transform,reach,result))
        throw std::runtime_error("Cannot determine precision needed to preserve exterior skin gaps.");
    return result[1]?std::min(g.voxel,result[0]/5.5):g.voxel;
}
Grid protected_grid(Scene& scene,const Fields& fields,const std::vector<float>& coarse,uint64_t cancel) {
    Grid grid; grid.cancel=cancel; grid.voxel=precision(scene,fields,coarse);
    const auto bounds=occupied(fields,cancel); grid.count=1;
    for(int a=0;a<3;++a) {
        grid.origin[a]=fields.grid.origin[a]+bounds[a]*fields.grid.voxel;
        const double n=std::ceil((bounds[a+3]-bounds[a])*fields.grid.voxel/grid.voxel)+1;
        if(!std::isfinite(n)||n<1||n>1048576) throw std::runtime_error("Required gap lattice exceeds supported dimensions.");
        grid.shape[a]=int(n); grid.count*=grid.shape[a];
    }
    return grid;
}
std::unique_ptr<Tiles> prepare_tiles(Scene& scene,const Fields& fields,uint64_t budget,uint64_t cancel) {
    const auto& g=fields.grid; std::vector<float> coarse(fields.values[3].begin(),fields.values[3].end());
    const auto fine=protected_grid(scene,fields,coarse,cancel);
    const double ct[]{g.origin[0],g.origin[1],g.origin[2],g.voxel};
    const double ft[]{fine.origin[0],fine.origin[1],fine.origin[2],fine.voxel};
    const double reach=g.length*3*9.51539268851356/220,offset=g.length*(fields.ratios[0]+fields.ratios[1]);
    auto tiles=std::make_unique<Tiles>();
    kernel::af_skin::init_skin_tiles(*tiles,&scene,coarse.data(),g.shape.data(),ct,fine.shape.data(),ft,reach,offset,budget);
    check_cancel(cancel); return tiles;
}
}
