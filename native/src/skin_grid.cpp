#include "skin_fields.hpp"
#include "mesh_internal.hpp"
#include <algorithm>
#include <cmath>
#include <limits>

namespace af::skin {
uint64_t index(const Grid& g,int x,int y,int z) {
    return (uint64_t(x)*g.shape[1]+y)*g.shape[2]+z;
}
std::array<int,3> coordinates(const Grid& g,uint64_t n) {
    const int z=int(n%g.shape[2]); n/=g.shape[2];
    return {int(n/g.shape[1]),int(n%g.shape[1]),z};
}
static std::array<double,6> bounds(const Source& s) {
    if(!s.vertices||!s.faces||!s.skeletal||!s.collagen||s.count<3||s.triangles<1)
        throw std::runtime_error("Skin has no usable source geometry.");
    std::array<double,6> b{INFINITY,INFINITY,INFINITY,-INFINITY,-INFINITY,-INFINITY};
    for(int i=0;i<s.count;++i) for(int a=0;a<3;++a) {
        const double v=s.vertices[3LL*i+a];
        if(!std::isfinite(v)) throw std::runtime_error("Nonfinite skin source position.");
        b[a]=std::min(b[a],v); b[a+3]=std::max(b[a+3],v);
    }
    for(int64_t i=0;i<3LL*s.triangles;++i) if(s.faces[i]<0||s.faces[i]>=s.count)
        throw std::runtime_error("Invalid skin triangle index.");
    return b;
}
static double padding(const double* s) {
    if(!s) throw std::runtime_error("Missing skin field settings.");
    for(int i=0;i<4;++i) if(!std::isfinite(s[i])||s[i]<0)
        throw std::runtime_error("Skin field settings must be finite and nonnegative.");
    return std::max({4.75769634425678/220+s[0],9.51539268851356/220+s[0]+s[1],s[2]+s[3]})
        +(18.27308903277034-13.480139642060877)/220;
}
static Grid dimensions(const std::array<double,6>& b,double pad,int n,uint64_t cancel) {
    Grid g; g.resolution=n; g.cancel=cancel;
    g.length=std::max({b[3]-b[0],b[4]-b[1],b[5]-b[2]});
    if(!std::isfinite(g.length)||g.length<=0) throw std::runtime_error("Skin source has zero extent.");
    g.voxel=g.length/n; g.count=1;
    for(int a=0;a<3;++a) {
        g.origin[a]=b[a]-pad*g.length;
        const double count=std::ceil((b[a+3]-b[a]+2*pad*g.length)/g.voxel)+1;
        if(count<1||count>1048576) throw std::runtime_error("Skin grid dimension exceeds supported range.");
        g.shape[a]=int(count); g.count*=g.shape[a];
    }
    return g;
}
Grid grid(const Source& source,const double* settings,int resolution,uint64_t budget,uint64_t cancel) {
    check_cancel(cancel); const auto b=bounds(source); const double pad=padding(settings);
    if(resolution<16||resolution>1048576) throw std::runtime_error("Invalid skin field resolution.");
    const int minimum=std::min(160,resolution);
    while(resolution>minimum) {
        const auto g=dimensions(b,pad,resolution,cancel);
        if(g.count<=budget/104) return g;
        resolution-=10;
    }
    const auto g=dimensions(b,pad,minimum,cancel);
    if(g.count>budget/104) throw std::runtime_error("Skin grid exceeds worker memory budget.");
    return g;
}
}
