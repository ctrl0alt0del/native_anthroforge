// SPDX-License-Identifier: GPL-3.0-or-later
// Port of addon fiber_surface.py patch projection and intersection predicates.
#include "surface_patch_internal.hpp"

namespace af::curve_surface {
static V3 center(const Points& points) {
    V3 result=V3::Zero();
    for(const auto& p:points) result+=p;
    return result/double(points.size());
}
static V3 newell(const Points& points) {
    V3 result=V3::Zero();
    for(size_t i=0;i<points.size();++i) {
        const auto& a=points[i]; const auto& b=points[(i+1)%points.size()];
        result+=V3((a.y()-b.y())*(a.z()+b.z()),(a.z()-b.z())*(a.x()+b.x()),(a.x()-b.x())*(a.y()+b.y()));
    }
    if(result.squaredNorm()<=1e-16) throw std::runtime_error("Patch boundary is degenerate.");
    return result.normalized();
}
static V3 best_fit(const Points& points,const V3& origin) {
    V3 normal=newell(points); M3 covariance=M3::Zero();
    for(const auto& p:points) { const V3 offset=p-origin; covariance+=offset*offset.transpose(); }
    const double scale=std::max(1e-12,covariance.cwiseAbs().rowwise().sum().maxCoeff());
    for(int i=0;i<32;++i) {
        const V3 candidate=normal-covariance*normal/scale;
        if(candidate.squaredNorm()>1e-20) normal=candidate.normalized();
    }
    return normal;
}
double orient(const V2& a,const V2& b,const V2& c) {
    return (b.x()-a.x())*(c.y()-a.y())-(b.y()-a.y())*(c.x()-a.x());
}
static bool crosses(const V2& a,const V2& b,const V2& c,const V2& d) {
    return orient(a,b,c)*orient(a,b,d)<-1e-12&&orient(c,d,a)*orient(c,d,b)<-1e-12;
}
static void check_intersections(const Polygon& points,uint64_t cancel) {
    const size_t n=points.size();
    for(size_t i=0;i<n;++i) {
        check_cancel(cancel);
        for(size_t j=i+1;j<n;++j) {
            if((i+1)%n==j||(j+1)%n==i) continue;
            if(crosses(points[i],points[(i+1)%n],points[j],points[(j+1)%n]))
                throw std::runtime_error("Patch boundary self-intersects.");
        }
    }
}
Projection projection(const Points& points) {
    if(points.size()<3) throw std::runtime_error("Patch needs three boundary samples.");
    const V3 origin=center(points),normal=best_fit(points,origin);
    Eigen::Index axis=0; normal.cwiseAbs().minCoeff(&axis);
    const V3 first=normal.cross(V3::Unit(axis)).normalized(),second=normal.cross(first);
    return {origin,first,second};
}
Polygon project(const Points& points,uint64_t cancel) {
    const auto frame=projection(points);
    Polygon result;
    for(const auto& p:points) result.emplace_back((p-frame.origin).dot(frame.first),(p-frame.origin).dot(frame.second));
    check_intersections(result,cancel); return result;
}
}
