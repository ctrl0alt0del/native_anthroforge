// SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
// Adapted for AnthroForge; see native/migration/BLENDER_PRIMITIVES.md.
// SPDX-License-Identifier: GPL-3.0-or-later
#include "construction_internal.hpp"

namespace af {
struct CurvePath { Samples samples; std::vector<double> distances; bool closed; };
static CurvePath path(const double* samples,int count,bool closed) {
    CurvePath result{read_samples(samples,count),{0},closed};
    if(closed) result.samples.push_back(result.samples.front());
    for(size_t i=1;i<result.samples.size();++i)
        result.distances.push_back(result.distances.back()+(result.samples[i].position-result.samples[i-1].position).norm());
    if(result.distances.back()<1e-12) throw std::runtime_error("Curve has zero length.");
    return result;
}
static Eigen::Quaterniond orientation(const CurveSample& sample) {
    M3 frame; frame.col(0)=sample.tangent; frame.col(1)=sample.normal;
    frame.col(2)=sample.tangent.cross(sample.normal);
    return Eigen::Quaterniond(frame).normalized();
}
static CurveSample blend_frame(const CurveSample& a,const CurveSample& b,double t) {
    const double blend=std::clamp(t,0.0,1.0);
    const auto rotation=orientation(a).slerp(blend,orientation(b));
    return {(1-t)*a.position+t*b.position,rotation*V3::UnitX(),rotation*V3::UnitY(),
            (1-blend)*a.radius+blend*b.radius,0};
}
static CurveSample path_at(const CurvePath& path,double distance) {
    const double total=path.distances.back();
    if(path.closed) distance-=std::floor(distance/total)*total;
    const auto found=std::lower_bound(path.distances.begin()+1,path.distances.end(),distance);
    const size_t i=std::min(size_t(found-path.distances.begin()),path.samples.size()-1);
    const double span=path.distances[i]-path.distances[i-1];
    const double t=span>1e-20?(distance-path.distances[i-1])/span:0;
    return blend_frame(path.samples[i-1],path.samples[i],t);
}
static V3 bent_point(const V3& p,const CurvePath& path,bool fit,double length,double position) {
    const double distance=(fit?p.x()/length*path.distances.back():p.x())+position;
    const auto sample=path_at(path,distance);
    const V3 normal=(sample.normal-sample.tangent*sample.tangent.dot(sample.normal)).normalized();
    const V3 binormal=sample.tangent.cross(normal);
    return sample.position+sample.radius*(p.y()*normal+p.z()*binormal);
}
static Vertices bent_vertices(const Mesh& base,const CurvePath& path,bool fit,double length,double position,uint64_t cancel) {
    Vertices output(base.vertices.rows(),3);
    for(int i=0;i<output.rows();++i) {
        if(i%1024==0) check_cancel(cancel);
        output.row(i)=bent_point(base.vertices.row(i),path,fit,length,position);
    }
    return output;
}
}
uint64_t af_curve_deform(uint64_t base,const double* samples,int count,int fit,double length,double position,int closed,uint64_t cancel) {
    try {
        if(length<=0) throw std::runtime_error("Body length must be positive.");
        const auto source=af::mesh(base);
        const auto curve=af::path(samples,count,closed!=0);
        const auto vertices=af::bent_vertices(*source,curve,fit!=0,length,position,cancel);
        return af::retain(af::deform_mesh(*source,vertices,cancel,source->prepared));
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
