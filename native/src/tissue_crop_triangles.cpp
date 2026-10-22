// SPDX-License-Identifier: GPL-3.0-or-later
// Material-domain triangulation ports core/vcp/muscle_domain_clip.py, independent of display tessellation.
#include "tissue_crop.hpp"
#include <numeric>
#include <limits>

namespace af::tissue {
using Point2=Eigen::Vector2d;
static double cross2(const Point2& a,const Point2& b) { return a.x()*b.y()-a.y()*b.x(); }
static std::vector<Point2> project(const Points& points,double& epsilon) {
    V3 normal=V3::Zero(),largest=V3::Zero();
    for(size_t i=0;i<points.size();++i) {
        const V3 product=points[i].cross(points[(i+1)%points.size()]); normal+=product;
        if(product.norm()>largest.norm()) largest=product;
    }
    if(normal.isZero(0)) normal=largest;
    Eigen::Index axis; normal.cwiseAbs().maxCoeff(&axis);
    std::vector<Point2> result; double scale=0;
    for(const auto& point:points) { result.emplace_back(point[(axis+1)%3],point[(axis+2)%3]); scale=std::max(scale,result.back().cwiseAbs().maxCoeff()); }
    epsilon=std::numeric_limits<double>::epsilon()*scale*scale*32; return result;
}
static bool intersects(const Point2& a,const Point2& b,const Point2& c,const Point2& d,double epsilon) {
    const double x=cross2(b-a,c-a),y=cross2(b-a,d-a),u=cross2(d-c,a-c),v=cross2(d-c,b-c);
    if(std::min(x,y)>epsilon||std::max(x,y)<-epsilon||std::min(u,v)>epsilon||std::max(u,v)<-epsilon) return false;
    return (a.cwiseMin(b).cwiseMax(c.cwiseMin(d)).array()<=a.cwiseMax(b).cwiseMin(c.cwiseMax(d)).array()).all();
}
static bool simple(const std::vector<Point2>& points,double epsilon) {
    const auto count=points.size();
    for(size_t i=0;i<count;++i) for(size_t j=i+2;j<count;++j) {
        if(i==0&&j==count-1) continue;
        if(intersects(points[i],points[(i+1)%count],points[j],points[(j+1)%count],epsilon)) return false;
    }
    return true;
}
static Faces fan(const std::vector<int64_t>& ids) {
    Faces result;
    for(size_t i=1;i+1<ids.size();++i) result.push_back({ids[0],ids[i],ids[i+1]});
    return result;
}
static bool contains(const std::vector<Point2>& points,const std::vector<int>& remaining,
    const std::array<int,3>& triangle,double sign,double epsilon) {
    for(auto i:remaining) {
        if(std::find(triangle.begin(),triangle.end(),i)!=triangle.end()) continue;
        bool inside=true;
        for(int j=0;j<3;++j) {
            const auto& a=points[triangle[j]]; const auto& b=points[triangle[(j+1)%3]];
            inside=inside&&sign*cross2(b-a,points[i]-a)>=-epsilon;
        }
        if(inside) return true;
    }
    return false;
}
static size_t ear(const std::vector<Point2>& points,const std::vector<int>& remaining,double sign,double epsilon) {
    for(size_t i=0;i<remaining.size();++i) {
        const std::array<int,3> t={remaining[(i+remaining.size()-1)%remaining.size()],remaining[i],remaining[(i+1)%remaining.size()]};
        if(sign*cross2(points[t[1]]-points[t[0]],points[t[2]]-points[t[1]])<=epsilon) continue;
        if(!contains(points,remaining,t,sign,epsilon)) return i;
    }
    throw std::runtime_error("Material crop polygon cannot be triangulated safely.");
}
static Faces ears(const std::vector<int64_t>& ids,const std::vector<Point2>& points,double sign,double epsilon) {
    std::vector<int> remaining(ids.size()); std::iota(remaining.begin(),remaining.end(),0); Faces result;
    while(remaining.size()>3) {
        const auto i=ear(points,remaining,sign,epsilon),count=remaining.size();
        result.push_back({ids[remaining[(i+count-1)%count]],ids[remaining[i]],ids[remaining[(i+1)%count]]});
        remaining.erase(remaining.begin()+i);
    }
    result.push_back({ids[remaining[0]],ids[remaining[1]],ids[remaining[2]]}); return result;
}
static bool nonplanar(const Points& points) {
    if(points.size()!=4) return false;
    double scale=0; for(const auto& p:points) scale=std::max(scale,p.cwiseAbs().maxCoeff());
    if(scale==0) return false;
    return std::abs((points[1]/scale).cross(points[2]/scale).dot(points[3]/scale))>std::numeric_limits<double>::epsilon()*64;
}
static Faces triangulate(const std::vector<int64_t>& ids,const Points& source) {
    double epsilon=0; const auto p=project(source,epsilon); double area=0;
    for(size_t i=0;i<p.size();++i) area+=cross2(p[i],p[(i+1)%p.size()]);
    bool convex=std::abs(area)>epsilon,turns=false; const double sign=area>0?1:-1;
    for(size_t i=0;i<p.size();++i) {
        const double turn=cross2(p[(i+1)%p.size()]-p[i],p[(i+2)%p.size()]-p[(i+1)%p.size()]);
        convex=convex&&sign*turn>=-epsilon; turns=turns||std::abs(turn)>epsilon;
    }
    if(!turns) return {};
    if((ids.size()>4||!convex)&&!simple(p,epsilon)) {
        if(nonplanar(source)) return fan(ids);
        throw std::runtime_error("Material crop requires a simple projected polygon.");
    }
    if(std::abs(area)<=epsilon) return {};
    return convex?fan(ids):ears(ids,p,sign,epsilon);
}
Faces crop_triangles(const CropState& state,const Mesh& own,size_t face) {
    std::vector<int64_t> ids(own.corners.begin()+own.offsets[face],own.corners.begin()+own.offsets[face+1]);
    if(std::none_of(ids.begin(),ids.end(),[&](int64_t id){return state.distances[size_t(id)]>=0;})) return {};
    if(ids.size()==3) return {ids};
    Points points; for(auto id:ids) points.push_back(state.base[size_t(id)]-state.base[size_t(ids[0])]);
    return triangulate(ids,points);
}
}
