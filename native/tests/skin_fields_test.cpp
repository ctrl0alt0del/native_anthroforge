#include "skin_buffers_test.hpp"
#include <algorithm>
#include <cmath>
#include <limits>

using namespace af;
using namespace af::skin;
static Grid fixture(std::array<int,3> shape={7,9,5}) {
    Grid g; g.shape=shape; g.count=uint64_t(shape[0])*shape[1]*shape[2]; g.voxel=0.25;
    return g;
}
static Values brute_distance(const Grid& g,const Mask& seeds) {
    Values result(g.count,INFINITY);
    for(uint64_t i=0;i<g.count;++i) for(uint64_t j=0;j<g.count;++j) if(seeds[j]) {
        const auto a=coordinates(g,i),b=coordinates(g,j);
        const double dx=a[0]-b[0],dy=a[1]-b[1],dz=a[2]-b[2];
        result[i]=std::min(result[i],dx*dx+dy*dy+dz*dz);
    }
    for(auto& v:result) v=std::sqrt(v)*g.voxel;
    return result;
}
static void independent_lines_and_ties() {
    for(const auto shape:{std::array<int,3>{7,9,5},{1,17,3},{11,1,7},{4,8,1}}) {
        const auto g=fixture(shape); Mask seeds(g.count);
        for(uint64_t i=0;i<g.count;i+=13) seeds[i]=1;
        const auto expected=brute_distance(g,seeds);
        require_skin(distance(g,seeds)==expected);
        require_skin(distance(g,seeds)==expected);
    }
}
static void empty_and_full_seeds() {
    const auto g=fixture(); Mask seeds(g.count);
    const auto empty=distance(g,seeds);
    for(uint64_t i=0;i<g.count;++i) {
        const auto c=coordinates(g,i);
        const double d=double(c[0]+1)*(c[0]+1)+double(c[1])*c[1]+double(c[2])*c[2];
        require_skin(empty[i]==g.voxel*std::sqrt(d));
    }
    std::fill(seeds.begin(),seeds.end(),1);
    require_skin(distance(g,seeds)==Values(g.count,0));
}
static void diagonal_exterior_and_blocked_corner() {
    const auto g=fixture({5,5,5}); Mask surface(g.count,1),outside(g.count);
    for(int a=0;a<5;++a) { surface[index(g,a,a,a)]=0; outside[index(g,a,a,a)]=1; }
    require_skin(exterior(g,surface,0,0)==brute_distance(g,outside));
    surface[0]=1;
    require_skin(exterior(g,surface,0,0)==brute_distance(g,surface));
}
static void six_neighbor_dilation() {
    const auto g=fixture({5,5,5}); Mask seeds(g.count);
    seeds[index(g,2,2,2)]=1; const auto actual=dilate(g,seeds);
    for(uint64_t i=0;i<g.count;++i) {
        const auto c=coordinates(g,i);
        const bool near=std::abs(c[0]-2)+std::abs(c[1]-2)+std::abs(c[2]-2)<=1;
        require_skin(actual[i]==near);
    }
}
static void sparse_collagen_and_rounding() {
    const auto g=fixture({5,5,5}); Mask expanded(g.count); expanded[index(g,2,2,2)]=1;
    std::vector<float> seeds(g.count,std::numeric_limits<float>::quiet_NaN());
    seeds[index(g,2,2,2)]=0.5f; // 7.5 rounds to even: level 8, not level 7.
    const auto distances=brute_distance(g,dilate(g,expanded));
    const auto actual=collagen(g,seeds,0.125,0.5); const double minimum=double(8.0f/15.0f);
    for(uint64_t i=0;i<g.count;++i) {
        double f=std::clamp((distances[i]-0.125)/0.5,0.0,1.0); f=f*f*(3.0-2.0*f);
        require_skin(actual[i]==minimum+(1-minimum)*f);
    }
}
static void collagen_empty_and_unit_levels() {
    const auto g=fixture(); std::vector<float> seeds(g.count,INFINITY);
    require_skin(collagen(g,seeds,1,2)==Values(g.count,1));
    std::fill(seeds.begin(),seeds.end(),1.0f);
    require_skin(collagen(g,seeds,1,2)==Values(g.count,1));
    std::fill(seeds.begin(),seeds.end(),0.0f);
    require_skin(collagen(g,seeds,0,0)==Values(g.count,0));
}
static void cancelled_distance() {
    Cancellation token; auto g=fixture(); g.cancel=reinterpret_cast<uint64_t>(&token);
    Mask seeds(g.count); seeds[0]=1; token.cancelled.store(true); bool cancelled=false;
    try { (void)distance(g,seeds); } catch(const std::runtime_error&) { cancelled=true; }
    require_skin(cancelled); token.cancelled.store(false);
    require_skin(distance(g,seeds)==brute_distance(g,seeds));
}
void test_skin_fields() {
    independent_lines_and_ties(); empty_and_full_seeds(); diagonal_exterior_and_blocked_corner();
    six_neighbor_dilation(); sparse_collagen_and_rounding(); collagen_empty_and_unit_levels();
    cancelled_distance();
}
