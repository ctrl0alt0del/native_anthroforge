// SPDX-License-Identifier: GPL-3.0-or-later
// Matched perimeter stations include both boundaries' exact corners.
#include "material_chart.hpp"
#include <set>

namespace af::material {
static V2 boundary_point(const Chart& chart,double parameter) {
    auto upper=chart.boundary.upper_bound(parameter),lower=upper;
    if(lower==chart.boundary.begin()) lower=chart.boundary.end();
    --lower;
    const double end=upper==chart.boundary.end()?1:upper->first;
    if(upper==chart.boundary.end()) upper=chart.boundary.begin();
    const double t=(parameter-lower->first)/(end-lower->first);
    return (1-t)*lower->second+t*upper->second;
}
static Cage paired(const Chart& a,const Chart& b,uint64_t cancel) {
    Cage result;
    if(a.boundary.empty()&&b.boundary.empty()) return result;
    if(a.boundary.empty()||b.boundary.empty()) throw std::runtime_error("Material chart kind changed; explicitly rebind.");
    std::set<double> stations;
    for(const auto* chart:{&a,&b}) for(const auto& [t,point]:chart->boundary) { check_cancel(cancel); stations.insert(t); }
    double previous=-1;
    for(double t:stations) if(t-previous>1e-12) {
        check_cancel(cancel); result.source.push_back(boundary_point(a,t)); result.target.push_back(boundary_point(b,t)); previous=t;
    }
    return result;
}
std::vector<Cage> cages(const Atlas& before,const Atlas& after,uint64_t cancel) {
    std::vector<Cage> result;
    for(size_t i=0;i<before.charts.size();++i) result.push_back(paired(before.charts[i],after.charts.at(i),cancel));
    return result;
}
Coordinate transported(const Cage& cage,const M3& triangle,const V3& weights,uint64_t cancel) {
    Coordinate result; result.point=triangle.transpose()*weights;
    for(int i=0;i<2;++i) result.tangents.col(i)=triangle.row(i+1)-triangle.row(0);
    if(!cage.source.empty()) {
        const auto mapping=mean_value(cage,result.point.head<2>(),cancel);
        result.point.head<2>()=mapping.point;
        result.tangents.topRows<2>()=(mapping.derivative*result.tangents.topRows<2>()).eval();
    }
    return result;
}
}
