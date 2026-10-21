// SPDX-License-Identifier: GPL-3.0-or-later
// AnthroForge addon fiber_surface.py/free_surface.py; see migration/CURVE_SURFACES.md.
#include "curve_surface_internal.hpp"

namespace af::curve_surface {
void budget(size_t vertices,size_t triangles) {
    if(vertices>max_vertices||triangles>max_triangles)
        throw std::runtime_error("Surface output exceeds bounded vertex/triangle budget.");
}
std::vector<double> stations(const Row& row) {
    if(!row.material_stations.empty()) return row.material_stations;
    std::vector<double> result{0};
    for(size_t i=1;i<row.points.size()+size_t(row.closed);++i)
        result.push_back(result.back()+(row.points[i%row.points.size()]-row.points[i-1]).norm());
    if(result.back()<=1e-12) throw std::runtime_error("Surface source has zero length.");
    const double length=result.back();
    for(auto& value:result) value/=length;
    return result;
}
V3 sample(const Row& row,const std::vector<double>& positions,double factor) {
    auto found=std::lower_bound(positions.begin()+1,positions.end(),factor);
    const size_t b=std::min(size_t(found-positions.begin()),positions.size()-1),a=b-1;
    const double width=positions[b]-positions[a];
    const double t=width>1e-12?(factor-positions[a])/width:0;
    return (1-t)*row.points[a]+t*row.points[b%row.points.size()];
}
static std::vector<double> union_stations(const Rows& rows) {
    std::vector<double> ordered;
    const double end=stations(rows.front()).back();
    for(const auto& row:rows) {
        auto values=stations(row);
        if(std::abs(values.back()-end)>1e-10)
            throw std::runtime_error("Surface material correspondence extents must match.");
        if(row.closed) values.pop_back();
        ordered.insert(ordered.end(),values.begin(),values.end());
    }
    return unique_stations(std::move(ordered));
}
Rows common_stations(const Rows& rows,uint64_t cancel) {
    const auto target=union_stations(rows);
    budget(rows.size()*target.size(),2*(rows.size()-1)*target.size());
    Rows result;
    for(const auto& row:rows) {
        Row prepared; prepared.closed=row.closed; prepared.material_stations=target;
        const auto positions=stations(row);
        for(const double factor:target) {
            check_cancel(cancel); prepared.points.push_back(sample(row,positions,factor));
        }
        result.push_back(std::move(prepared));
    }
    return result;
}
static double average_step(const Rows& rows) {
    double length=0; size_t count=0;
    for(const auto& row:rows)
        for(size_t i=1;i<row.points.size();++i) {
            length+=(row.points[i]-row.points[i-1]).norm(); ++count;
        }
    return std::max(1e-6,length/double(std::max(size_t(1),count)));
}
static int inserts(const Row& a,const Row& b,double step,int minimum) {
    double distance=0;
    for(size_t i=0;i<a.points.size();++i) distance+=(a.points[i]-b.points[i]).norm();
    const double value=distance/double(a.points.size())/step-1e-6;
    if(value>double(max_vertices)) throw std::runtime_error("Surface density exceeds output budget.");
    return std::max(minimum,int(std::nearbyint(value))-1);
}
std::vector<int> density(const Rows& rows,int strips,bool exact) {
    const double step=average_step(rows);
    const int minimum=rows.front().closed?3:int(exact&&rows.size()==2);
    std::vector<int> result;
    for(size_t i=1;i<rows.size();++i)
        result.push_back(strips?strips-1:inserts(rows[i-1],rows[i],step,minimum));
    return result;
}
}
