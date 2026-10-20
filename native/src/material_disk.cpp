// SPDX-License-Identifier: GPL-3.0-or-later
// Radial homeomorphism between boundary polygons defines the same continuous disk
// when boundary sampling changes. Its analytic derivative transports attachment frames.
#include "material_chart.hpp"

namespace af::material {
void disk_boundary(Chart& chart) {
    for(const auto& [id,p]:chart.points)
        if(std::abs(p.head<2>().squaredNorm()-1)<1e-12) chart.boundary.push_back(std::atan2(p.y(),p.x()));
    std::sort(chart.boundary.begin(),chart.boundary.end());
    if(chart.boundary.size()<3) throw std::runtime_error("Material disk has no closed boundary.");
}
static V3 edge_plane(const Chart& chart,const V3& point) {
    const double angle=std::atan2(point.y(),point.x());
    const auto found=std::upper_bound(chart.boundary.begin(),chart.boundary.end(),angle);
    const auto b=size_t(found-chart.boundary.begin())%chart.boundary.size(),a=(b+chart.boundary.size()-1)%chart.boundary.size();
    const Eigen::Vector2d first(std::cos(chart.boundary[a]),std::sin(chart.boundary[a]));
    const Eigen::Vector2d last(std::cos(chart.boundary[b]),std::sin(chart.boundary[b]));
    const Eigen::Vector2d n(last.y()-first.y(),first.x()-last.x());
    return V3(n.x(),n.y(),n.dot(first));
}
void transport(const Chart& before,const Chart& after,V3& query,V3& tangent) {
    if(before.boundary.empty()&&after.boundary.empty()) return;
    if(before.boundary.empty()||after.boundary.empty()) throw std::runtime_error("Material chart kind changed; explicitly rebind.");
    if(query.head<2>().squaredNorm()<1e-24) return;
    const V3 a=edge_plane(before,query),b=edge_plane(after,query);
    const double x=a.head<2>().dot(query.head<2>()),y=b.head<2>().dot(query.head<2>());
    const double ratio=b.z()/a.z(),scale=ratio*x/y;
    const Eigen::Vector2d gradient=ratio*(a.head<2>()*y-b.head<2>()*x)/(y*y);
    tangent.head<2>()=scale*tangent.head<2>()+query.head<2>()*gradient.dot(tangent.head<2>());
    query.head<2>()*=scale;
}
Coordinate transported(const Chart& before,const Chart& after,const M3& triangle,const V3& weights) {
    Coordinate result;
    for(int i=0;i<2;++i) {
        V3 query=triangle.transpose()*weights,tangent=triangle.row(i+1)-triangle.row(0);
        transport(before,after,query,tangent);
        result.point=query; result.tangents.col(i)=tangent;
    }
    return result;
}
}
