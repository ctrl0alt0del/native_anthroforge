// SPDX-License-Identifier: GPL-3.0-or-later
// Native port of addon branched_surface.py station and across interpolation.
#include "surface_branch_internal.hpp"

namespace af::curve_surface {
std::vector<double> unique_stations(std::vector<double> values) {
    std::sort(values.begin(),values.end());
    values.erase(std::unique(values.begin(),values.end(),[](double a,double b){return std::abs(a-b)<1e-12;}),values.end());
    if(values.size()>max_stations) throw std::runtime_error("Branch station budget exceeded.");
    return values;
}
std::vector<double> uniform_stations(size_t count) {
    std::vector<double> values(count);
    for(size_t i=0;i<count;++i) values[i]=double(i)/double(count-1);
    return values;
}
std::vector<double> merged_stations(const Rows& rows,bool exact,int minimum,int samples) {
    std::vector<double> values=minimum>1||!exact?uniform_stations(size_t(std::max(minimum,exact?0:samples))):std::vector<double>{};
    if(exact) for(const auto& row:rows) {
        const auto source=stations(row); values.insert(values.end(),source.begin(),source.end());
    }
    return unique_stations(std::move(values));
}
Grid sampled_grid(const Rows& rows,const std::vector<double>& along,uint64_t cancel) {
    budget(rows.size()*along.size(),2*rows.size()*along.size());
    Grid result; result.rows=rows.size(); result.columns=along.size();
    for(const auto& row:rows) {
        const auto source=stations(row);
        for(double value:along) { check_cancel(cancel); result.points.push_back(sample(row,source,value)); }
    }
    return result;
}
static std::pair<size_t,double> segment(const std::vector<double>& source,double value) {
    const auto found=std::lower_bound(source.begin()+1,source.end(),value);
    const size_t b=std::min(size_t(found-source.begin()),source.size()-1),a=b-1;
    return {a,(value-source[a])/(source[b]-source[a])};
}
Grid across_grid(const Grid& grid,const std::vector<double>& source,const std::vector<double>& target,uint64_t cancel) {
    budget(target.size()*grid.columns,2*target.size()*grid.columns);
    Grid result; result.rows=target.size(); result.columns=grid.columns;
    for(double value:target) {
        const auto edge=segment(source,value); const double t=edge.second;
        for(size_t j=0;j<grid.columns;++j) {
            check_cancel(cancel); const size_t a=edge.first*grid.columns+j;
            result.points.push_back((1-t)*grid.points[a]+t*grid.points[a+grid.columns]);
        }
    }
    return result;
}
}
