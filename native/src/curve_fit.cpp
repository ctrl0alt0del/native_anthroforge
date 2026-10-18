/* Fitting/handle policy adapted from Blender v5.0.1 editcurve_paint.cc
 * (Blender Authors, GPL-2.0-or-later). Unchanged BSD kernel is vendored separately. */
#include "mesh_internal.hpp"
#include "anthroforge/drawing.h"
#include <algorithm>
#include <cstdlib>
extern "C" {
#include "curve_fit_nd/curve_fit_nd.h"
}

namespace af {
struct FitSettings { int dimensions,method; bool closed; float error,angle; uint64_t cancel; };
struct Fitted {
    float* data=nullptr;
    unsigned int *corners=nullptr,count=0,corner_count=0;
    Fitted()=default;
    Fitted(const Fitted&)=delete;
    Fitted& operator=(const Fitted&)=delete;
    ~Fitted() { std::free(data); std::free(corners); }
};
static void validate_fit(const double* points,int count,const FitSettings& s) {
    if(!points||count<2||count>100000||(s.dimensions!=3&&s.dimensions!=4)||s.method<0||s.method>2)
        throw std::runtime_error("Invalid stroke dimensions, count or fitting method.");
    if(!std::isfinite(s.error)||s.error<=0||!std::isfinite(s.angle)||s.angle<0||s.angle>float(M_PI))
        throw std::runtime_error("Fitting error must be positive and corner angle between zero and pi.");
}
static std::vector<float> stroke_points(const double* points,int count,const FitSettings& s) {
    validate_fit(points,count,s); std::vector<float> values;
    for(int i=0;i<count;++i) {
        check_cancel(s.cancel); std::vector<float> next(points+i*s.dimensions,points+(i+1)*s.dimensions);
        if(!std::all_of(next.begin(),next.end(),[](float v){return std::isfinite(v);}) ||
            (s.dimensions==4&&next[3]<0)) throw std::runtime_error("Stroke values must be finite; radius nonnegative.");
        if(values.empty()||!std::equal(next.begin(),next.end(),values.end()-s.dimensions))
            values.insert(values.end(),next.begin(),next.end());
    }
    if(s.closed&&values.size()>size_t(s.dimensions)&&std::equal(values.begin(),values.begin()+s.dimensions,values.end()-s.dimensions))
        values.resize(values.size()-s.dimensions);
    if(values.size()<size_t((s.closed?3:2)*s.dimensions)) throw std::runtime_error("Stroke needs distinct points.");
    return values;
}
static void fit_split(const std::vector<float>& points,const FitSettings& s,unsigned int flags,Fitted& output) {
    Fitted detected; const auto count=static_cast<unsigned int>(points.size()/s.dimensions);
    if(s.angle<float(M_PI)) curve_fit_corners_detect_fl(points.data(),count,s.dimensions,
        s.error/8,s.error*2,16,s.angle,&detected.corners,&detected.corner_count);
    if(curve_fit_cubic_to_points_fl(points.data(),count,s.dimensions,s.error,flags,
        detected.corners,detected.corner_count,&output.data,&output.count,nullptr,&output.corners,&output.corner_count))
        throw std::runtime_error("Curve split fitting failed.");
}
static void fit_stroke(const std::vector<float>& points,const FitSettings& s,Fitted& output) {
    const auto count=static_cast<unsigned int>(points.size()/s.dimensions);
    const unsigned int flags=CURVE_FIT_CALC_HIGH_QUALIY|(s.closed?CURVE_FIT_CALC_CYCLIC:0);
    check_cancel(s.cancel);
    if(s.method==1) fit_split(points,s,flags,output);
    else if(curve_fit_cubic_to_points_refit_fl(points.data(),count,s.dimensions,s.error,flags,nullptr,0,
        s.angle,&output.data,&output.count,nullptr,&output.corners,&output.corner_count))
        throw std::runtime_error("Curve refitting failed.");
    check_cancel(s.cancel);
    if(output.count<unsigned(s.closed?3:2)) throw std::runtime_error("Fit has too few knots; reduce fitting error.");
}
static void copy_knot(const float* left,const float* point,const float* right,int dims,double* output) {
    std::copy_n(point,3,output); std::copy_n(left,3,output+3); std::copy_n(right,3,output+6);
    output[9]=dims==4?std::max(0.0f,point[3]):1; output[10]=0; output[11]=output[12]=1;
}
static void copy_fit(const Fitted& fitted,const FitSettings& s,double* output) {
    for(unsigned int i=0;i<fitted.count;++i) {
        const auto* data=fitted.data+size_t(i)*3*s.dimensions;
        copy_knot(data,data+s.dimensions,data+2*s.dimensions,s.dimensions,output+size_t(i)*13);
    }
    for(unsigned int i=0;i<fitted.corner_count;++i) {
        const auto index=fitted.corners[i];
        if(index>=fitted.count||(!s.closed&&(index==0||index==fitted.count-1))) continue;
        output[size_t(index)*13+11]=output[size_t(index)*13+12]=2;
    }
}
static std::vector<double> fit_records(const std::vector<float>& points,const FitSettings& s) {
    Fitted fitted; fit_stroke(points,s,fitted);
    std::vector<double> records(size_t(fitted.count)*13);
    copy_fit(fitted,s,records.data()); return records;
}
static std::vector<double> polyline_records(const std::vector<float>& points,const FitSettings& s) {
    std::vector<double> records(points.size()/s.dimensions*13);
    for(size_t i=0;i<points.size()/s.dimensions;++i) {
        const auto* point=points.data()+i*s.dimensions;
        copy_knot(point,point,point,s.dimensions,records.data()+i*13);
        records[i*13+11]=records[i*13+12]=3;
    }
    return records;
}
}
int af_curve_fit(const double* points,int count,int dimensions,int method,int closed,double error,
    double angle,double** output,int* output_count,uint64_t cancel) {
    try {
        if(!output||!output_count) throw std::runtime_error("Fitting requires output buffers.");
        *output=nullptr; *output_count=0;
        const af::FitSettings s{dimensions,method,closed!=0,float(error),float(angle),cancel};
        const auto values=af::stroke_points(points,count,s);
        const auto records=method==2?af::polyline_records(values,s):af::fit_records(values,s);
        af::check_cancel(cancel); auto owned=std::make_unique<double[]>(records.size());
        std::copy(records.begin(),records.end(),owned.get()); *output_count=int(records.size()/13);
        *output=owned.release(); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
void af_curve_fit_free(double* output) { delete[] output; }
