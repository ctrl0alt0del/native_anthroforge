// SPDX-License-Identifier: GPL-3.0-or-later
#include "curve_surface_internal.hpp"

namespace af::curve_surface {
static std::vector<std::pair<double,int>> distances(const Rows& rows,const M4& world,int axis,double shift) {
    std::vector<std::pair<double,int>> output;
    for(size_t i=0;i<rows.size();++i) {
        double total=0;
        for(const auto& p:rows[i].points) total+=point(world,p)[axis]-shift;
        output.emplace_back(total/double(rows[i].points.size()),int(i)+1);
    }
    return output;
}
static std::vector<int> mirror_order(std::vector<std::pair<double,int>> values) {
    double lo=INFINITY,hi=-INFINITY;
    for(const auto& value:values) { lo=std::min(lo,value.first); hi=std::max(hi,value.first); }
    std::vector<int> output;
    if(lo<-1e-6&&hi>1e-6) {
        for(const auto& value:values) output.push_back(value.second);
        return output;
    }
    std::stable_sort(values.begin(),values.end(),[](const auto& a,const auto& b){return std::abs(a.first)<std::abs(b.first);});
    for(auto it=values.rbegin();it!=values.rend();++it)
        if(std::abs(it->first)>1e-6) output.push_back(-it->second);
    for(const auto& value:values) output.push_back(value.second);
    return output;
}
}
int af_curve_surface_mirror_order(const AfSurfaceRow* rows,int count,const double* world,int axis,double shift,int* output,uint64_t cancel) {
    try {
        if(count<1||count>512||!world||axis<0||axis>2||!std::isfinite(shift)||!output)
            throw std::runtime_error("Mirrored rows require 1..512 sources and a finite X/Y/Z plane.");
        const af::M4 frame=Eigen::Map<const af::M4>(world);
        const auto source=af::curve_surface::inputs(rows,count,true,cancel);
        const auto distances=af::curve_surface::distances(source,frame,axis,shift);
        const auto order=af::curve_surface::mirror_order(distances);
        if(order.size()<2) throw std::runtime_error("Mirrored rows need an off-plane source or two distinct central rows.");
        std::copy(order.begin(),order.end(),output); return int(order.size());
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
