#include "skin_fields.hpp"
#include "mesh_internal.hpp"
#include <algorithm>
#include <cmath>

namespace af::skin {
struct Triangle { std::array<V3,3> p; std::array<float,3> weights; bool skeletal; };
static Triangle triangle(const Source& s,int face) {
    Triangle t; t.skeletal=s.skeletal[face]!=0;
    for(int a=0;a<3;++a) {
        const auto i=s.faces[3LL*face+a]; t.p[a]=V3(s.vertices+3*i);
        if(!std::isfinite(s.collagen[i])) throw std::runtime_error("Invalid skin collagen value.");
        t.weights[a]=float(s.collagen[i]);
    }
    return t;
}
static uint64_t cell(const Grid& g,const V3& p) {
    std::array<int,3> c{};
    for(int a=0;a<3;++a) {
        const double value=std::nearbyint((p[a]-g.origin[a])/g.voxel);
        c[a]=int(std::clamp(value,0.0,double(g.shape[a]-1)));
    }
    return index(g,c[0],c[1],c[2]);
}
static void point(const Grid& g,Raster& r,const Triangle& t,double u,double v) {
    const double w=1.0-(u+v);
    const auto i=cell(g,w*t.p[0]+u*t.p[1]+v*t.p[2]); r.all[i]=1;
    if(!t.skeletal) return;
    r.skeletal[i]=1;
    r.seeds[i]=std::min(r.seeds[i],float(w*t.weights[0]+u*t.weights[1]+v*t.weights[2]));
}
static void face(const Grid& g,Raster& r,const Triangle& t) {
    const double length=std::max({(t.p[1]-t.p[0]).norm(),(t.p[2]-t.p[1]).norm(),(t.p[0]-t.p[2]).norm()});
    const double steps=std::max(1.0,std::ceil(length/(.45*g.voxel)));
    if(steps>1048576) throw std::runtime_error("Skin raster sampling exceeds supported range.");
    const int n=int(steps);
    for(int u=0;u<=n;++u) {
        check_cancel(g.cancel);
        for(int v=0;v<=n-u;++v) point(g,r,t,double(u)/n,double(v)/n);
    }
}
static void segment(const Grid& g,Raster& r,const Source& source,int edge) {
    const V3 a(source.vertices+3*source.segments[2LL*edge]);
    const V3 b(source.vertices+3*source.segments[2LL*edge+1]);
    const double steps=std::max(1.0,std::ceil((b-a).norm()/(.45*g.voxel)));
    if(steps>1048576) throw std::runtime_error("Skin segment sampling exceeds supported range.");
    const int count=int(steps);
    for(int i=0;i<=count;++i) {
        if(i%4096==0) check_cancel(g.cancel);
        r.all[cell(g,a+(b-a)*(double(i)/count))]=1;
    }
}
Raster raster(const Grid& g,const Source& source) {
    Raster result{Mask(g.count),Mask(g.count),std::vector<float>(g.count,INFINITY)};
    for(int f=0;f<source.triangles;++f) { check_cancel(g.cancel); face(g,result,triangle(source,f)); }
    for(int e=0;e<source.segment_count;++e) { check_cancel(g.cancel); segment(g,result,source,e); }
    result.all=dilate(g,result.all); result.skeletal=dilate(g,result.skeletal);
    return result;
}
}
