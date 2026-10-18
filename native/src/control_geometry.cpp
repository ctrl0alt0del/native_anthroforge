// Display and cursor-query geometry prepared from owned, resolved control arrays.
#include "construction_internal.hpp"

namespace af {
static void transformed_output(const double* source,const M4& matrix,double* output) {
    Eigen::Map<V3> result(output);
    result=point(matrix,V3(source));
}
static void cubic_controls(const double* a,const double* b,const M4& matrix,double* output) {
    transformed_output(a,matrix,output);
    transformed_output(a+6,matrix,output+3);
    transformed_output(b+3,matrix,output+6);
    transformed_output(b,matrix,output+9);
}
static int polyline_lines(const double* points,int count,int group,bool closed,const M4& matrix,double* output) {
    int written=0;
    for(int start=0;start<count;start+=group) {
        for(int i=0;i<group-(closed?0:1);++i) {
            transformed_output(points+3*(start+i),matrix,output+3*written++);
            transformed_output(points+3*(start+(i+1)%group),matrix,output+3*written++);
        }
    }
    return written;
}
}
int af_curve_cubics(const double* resolved,int count,int closed,const double* matrix,double* output) {
    try {
        if(count<2||!resolved||!matrix||!output) throw std::runtime_error("Invalid cubic buffers.");
        const af::M4 frame=Eigen::Map<const af::M4>(matrix);
        for(int i=0;i<count-(closed?0:1);++i)
            af::cubic_controls(resolved+13*i,resolved+13*((i+1)%count),frame,output+12*i);
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
int af_polyline_lines(const double* points,int count,int group,int closed,const double* matrix,double* output) {
    try {
        if(count<0||group<1||count%group||!matrix||(count&&(!points||!output)))
            throw std::runtime_error("Invalid polyline buffers or grouping.");
        return af::polyline_lines(points,count,group,closed!=0,Eigen::Map<const af::M4>(matrix),output);
    } catch(const std::exception& e) { af::set_error(e.what()); return -1; }
}
