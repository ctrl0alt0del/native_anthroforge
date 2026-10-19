// SPDX-License-Identifier: GPL-3.0-or-later
// Closed alignment from addon free_surface.align_closed_rows; only on explicit request.
#include "curve_surface_internal.hpp"

namespace af::curve_surface {
static Row candidate(const Row& row,size_t first,bool reverse) {
    Row result; result.closed=true; result.extent=row.extent;
    result.direction=reverse?-row.direction:row.direction;
    for(size_t i=0;i<row.points.size();++i) {
        const size_t index=(first+(reverse?row.points.size()-i:i))%row.points.size();
        result.points.push_back(row.points[index]); result.parameters.push_back(row.parameters[index]);
    }
    return result;
}
static double score(const Row& reference,const Row& row) {
    const auto target=stations(reference),positions=stations(row);
    double result=0;
    for(size_t i=0;i<reference.points.size();++i)
        result+=(sample(row,positions,target[i])-reference.points[i]).squaredNorm();
    return result;
}
static Row best(const Row& reference,const Row& row,double* output,uint64_t cancel) {
    double distance=std::numeric_limits<double>::infinity(); Row result;
    for(int reverse=0;reverse<2;++reverse)
        for(size_t i=0;i<row.points.size();++i) {
            check_cancel(cancel);
            const size_t start=reverse?row.points.size()-1-i:i;
            auto trial=candidate(row,start,reverse!=0);
            const double current=score(reference,trial);
            if(current<distance) {
                distance=current; output[0]=row.parameters[start]; output[1]=reverse;
                result=std::move(trial);
            }
        }
    return result;
}
void align(Rows& rows,double* output,uint64_t cancel) {
    std::fill(output,output+rows.size()*2,0.);
    if(!rows.front().closed) return;
    output[0]=rows.front().parameters.front();
    for(size_t i=1;i<rows.size();++i)
        rows[i]=best(rows[i-1],rows[i],output+2*i,cancel);
}
}
