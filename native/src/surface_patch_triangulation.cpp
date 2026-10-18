// SPDX-License-Identifier: GPL-3.0-or-later
// Deterministic boundary-preserving ear clipping from addon fiber_surface.py.
#include "surface_patch_internal.hpp"
#include <numeric>

namespace af::curve_surface {
static std::vector<int> ordered(const Polygon& points) {
    double area=0;
    for(size_t i=0;i<points.size();++i) area+=orient(V2::Zero(),points[i],points[(i+1)%points.size()]);
    std::vector<int> result(points.size()); std::iota(result.begin(),result.end(),0);
    if(area<=0) std::reverse(result.begin(),result.end());
    return result;
}
static Triangle at(const std::vector<int>& polygon,size_t i) {
    return {polygon[(i+polygon.size()-1)%polygon.size()],polygon[i],polygon[(i+1)%polygon.size()]};
}
static bool ear(const Polygon& points,const std::vector<int>& polygon,const Triangle& t) {
    const auto& a=points[t[0]]; const auto& b=points[t[1]]; const auto& c=points[t[2]];
    if(orient(a,b,c)<=1e-12) return false;
    for(const int i:polygon) {
        if(std::find(t.begin(),t.end(),i)!=t.end()) continue;
        const auto& p=points[i];
        if(std::min({orient(a,b,p),orient(b,c,p),orient(c,a,p)})>=-1e-12) return false;
    }
    return true;
}
static int first_ear(const Polygon& points,const std::vector<int>& polygon,uint64_t cancel) {
    for(size_t i=0;i<polygon.size();++i) {
        check_cancel(cancel);
        if(ear(points,polygon,at(polygon,i))) return int(i);
    }
    return -1;
}
static bool convex(const Polygon& points) {
    int sign=0;
    for(size_t i=0;i<points.size();++i) {
        const double value=orient(points[(i+points.size()-1)%points.size()],points[i],points[(i+1)%points.size()]);
        if(std::abs(value)<=1e-12) continue;
        const int current=value>0?1:-1;
        if(sign&&sign!=current) return false;
        sign=current;
    }
    return sign!=0;
}
static std::vector<Triangle> fan(Points& points,const Polygon& polygon) {
    if(!convex(polygon)) throw std::runtime_error("Patch boundary cannot be triangulated.");
    V3 center=V3::Zero(); for(const auto& p:points) center+=p;
    center/=double(points.size()); const int added=int(points.size()); points.push_back(center);
    const auto order=ordered(polygon); std::vector<Triangle> result;
    for(size_t i=0;i<order.size();++i) result.push_back({added,order[i],order[(i+1)%order.size()]});
    return result;
}
std::vector<Triangle> triangulate(Points& points,const Polygon& projected,uint64_t cancel) {
    auto polygon=ordered(projected); std::vector<Triangle> result;
    while(polygon.size()>3) {
        const int index=first_ear(projected,polygon,cancel);
        if(index<0) return fan(points,projected);
        result.push_back(at(polygon,size_t(index))); polygon.erase(polygon.begin()+index);
    }
    result.push_back({polygon[0],polygon[1],polygon[2]}); return result;
}
}
