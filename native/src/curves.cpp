// SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
// Adapted for AnthroForge; see native/migration/BLENDER_PRIMITIVES.md.
// SPDX-License-Identifier: GPL-3.0-or-later
// Handle formulas adapted from Blender 5.0.1 curve.cc, BKE_nurb_handle_calc.
#include "construction_internal.hpp"

namespace af {
struct Bezier { V3 p,left,right; double radius,tilt; int lm,rm; };
static std::vector<Bezier> read_bezier(const double* data,int count) {
    if(!data||count<2) throw std::runtime_error("A Bézier curve needs two points.");
    std::vector<Bezier> result;
    for(int i=0;i<count;++i) {
        const double* p=data+i*13;
        result.push_back({V3(p),V3(p+3),V3(p+6),p[9],p[10],int(p[11]),int(p[12])});
    }
    return result;
}
static V3 auto_direction(const V3& a,const V3& b) {
    const double la=a.norm(),lb=b.norm();
    const V3 direction=a/(la==0?1:la)+b/(lb==0?1:lb);
    const double length=direction.norm()*2.5614;
    return length>1e-20?V3(direction/length):V3::Zero();
}
static void set_handles(Bezier& p,const V3& a,const V3& b) {
    const V3 direction=auto_direction(a,b);
    const double la=std::min(a.norm(),5*b.norm()),lb=std::min(b.norm(),5*la);
    if(p.lm==0) p.left=p.p-la*direction;
    if(p.rm==0) p.right=p.p+lb*direction;
    if(p.lm==3) p.left=p.p-a/3;
    if(p.rm==3) p.right=p.p+b/3;
    // Evaluation preserves aligned handles; only explicit handle edits align them.
    // Blender's BKE_curve_nurbs_vert_coords_apply uses skip_align=true here.
}
static void handles(std::vector<Bezier>& points,bool closed) {
    const int n=int(points.size());
    for(int i=0;i<n;++i) {
        const V3 p=points[i].p;
        const V3 a=i>0?p-points[i-1].p:(closed?V3(p-points.back().p):V3(points[1].p-p));
        const V3 b=i+1<n?points[i+1].p-p:(closed?V3(points[0].p-p):a);
        set_handles(points[i],a,b);
    }
}
static CurveSample bezier_sample(const Bezier& a,const Bezier& b,double t,const M4& matrix) {
    const double s=1-t;
    const V3 p=s*s*s*a.p+3*s*s*t*a.right+3*s*t*t*b.left+t*t*t*b.p;
    V3 tangent=3*s*s*(a.right-a.p)+6*s*t*(b.left-a.right)+3*t*t*(b.p-b.left);
    if(tangent.norm()<1e-20) tangent=b.p-a.p;
    tangent=matrix.topLeftCorner<3,3>()*tangent;
    if(tangent.norm()<1e-20) tangent=V3::UnitX();
    return {point(matrix,p),tangent.normalized(),V3::Zero(),s*a.radius+t*b.radius,s*a.tilt+t*b.tilt};
}
static Samples evaluated_curve(const std::vector<Bezier>& p,bool closed,int resolution,const M4& matrix) {
    Samples result;
    const int segments=int(p.size())-(closed?0:1);
    for(int i=0;i<segments;++i)
        for(int j=0;j<resolution;++j)
            result.push_back(bezier_sample(p[i],p[(i+1)%p.size()],double(j)/resolution,matrix));
    result.push_back(bezier_sample(p[segments-1],p[segments%p.size()],1,matrix));
    return result;
}
static CurveSample interpolate(const CurveSample& a,const CurveSample& b,double t) {
    V3 tangent=(1-t)*a.tangent+t*b.tangent;
    if(tangent.norm()<1e-20) tangent=a.tangent;
    return {(1-t)*a.position+t*b.position,tangent.normalized(),V3::Zero(),
            (1-t)*a.radius+t*b.radius,(1-t)*a.tilt+t*b.tilt};
}
static std::vector<double> curve_lengths(const Samples& samples) {
    std::vector<double> lengths{0};
    for(size_t i=1;i<samples.size();++i)
        lengths.push_back(lengths.back()+(samples[i].position-samples[i-1].position).norm());
    if(lengths.back()<1e-12) throw std::runtime_error("Curve has zero length.");
    return lengths;
}
static CurveSample at_distance(const Samples& samples,const std::vector<double>& lengths,double distance) {
    auto found=std::lower_bound(lengths.begin()+1,lengths.end(),distance);
    const size_t index=std::min(size_t(found-lengths.begin()),lengths.size()-1);
    const double span=lengths[index]-lengths[index-1];
    return interpolate(samples[index-1],samples[index],span>1e-20?(distance-lengths[index-1])/span:0);
}
static Samples resample(const Samples& source,int count,bool closed) {
    const auto lengths=curve_lengths(source);
    Samples result;
    for(int i=0;i<count;++i)
        result.push_back(at_distance(source,lengths,lengths.back()*i/(closed?count:count-1)));
    return result;
}
static Samples sample_range(const Samples& source,int count,double start,double span,bool closed) {
    Samples result;
    for(int i=0;i<count;++i) {
        double factor=start+span*i/(closed&&span==1?count:count-1);
        factor=closed?factor-std::floor(factor):std::clamp(factor,0.0,1.0);
        const double position=factor*(closed?source.size():source.size()-1);
        const auto a=std::min(size_t(position),source.size()-1),b=(a+1)%source.size();
        result.push_back(interpolate(source[a],source[closed?b:std::min(a+1,source.size()-1)],position-a));
    }
    return result;
}
static void frames(Samples& samples) {
    V3 normal=V3::UnitZ()-samples[0].tangent*samples[0].tangent.z();
    if(normal.norm()<1e-8) normal=V3::UnitY();
    normal.normalize();
    V3 previous=samples[0].tangent;
    for(auto& sample:samples) {
        normal=Eigen::Quaterniond::FromTwoVectors(previous,sample.tangent)*normal;
        normal=(normal-sample.tangent*normal.dot(sample.tangent)).normalized();
        sample.normal=Eigen::AngleAxisd(sample.tilt,sample.tangent)*normal;
        previous=sample.tangent;
    }
}
static void write_samples(const Samples& samples,double* output) {
    for(size_t i=0;i<samples.size();++i) {
        const auto& p=samples[i]; double* o=output+i*11;
        for(int a=0;a<3;++a) { o[a]=p.position[a]; o[a+3]=p.tangent[a]; o[a+6]=p.normal[a]; }
        o[9]=p.radius; o[10]=p.tilt;
    }
}
static void edit_handle(Bezier& p,bool left,const V3& value) {
    V3& edited=left?p.left:p.right; V3& other=left?p.right:p.left;
    int& mode=left?p.lm:p.rm; const int other_mode=left?p.rm:p.lm;
    edited=value;
    if(mode==0||mode==3) mode=2;
    if(other_mode==1&&(edited-p.p).norm()>1e-20)
        other=p.p-(edited-p.p).normalized()*(other-p.p).norm();
}
static void edit_point(Bezier& p,const double* replacement,int fields) {
    if(fields&1) {
        const V3 delta=V3(replacement)-p.p;
        p.p+=delta; p.left+=delta; p.right+=delta;
    }
    if(fields&8) p.lm=int(replacement[11]);
    if(fields&16) p.rm=int(replacement[12]);
    if(fields&2) edit_handle(p,true,V3(replacement+3));
    if(fields&4) edit_handle(p,false,V3(replacement+6));
    if(fields&32) p.radius=replacement[9];
    if(fields&64) p.tilt=replacement[10];
}
static Samples body_path(std::vector<Bezier> points,bool closed,int resolution,uint64_t cancel) {
    if(closed) std::rotate(points.begin(),points.end()-1,points.end());
    Samples result; const int segments=int(points.size())-(closed?0:1);
    for(int i=0;i<segments;++i) {
        check_cancel(cancel); const auto& a=points[i]; const auto& b=points[(i+1)%points.size()];
        const int steps=a.rm%4==3&&b.lm%4==3?1:resolution;
        for(int j=0;j<steps;++j) result.push_back(bezier_sample(a,b,double(j)/steps,M4::Identity()));
    }
    if(!closed) result.push_back(bezier_sample(points[segments-1],points[segments],1,M4::Identity()));
    curve_frames(result,closed,cancel);
    return result;
}
}
int af_curve_path(const double* points,int count,int closed,int resolution,double* output,int* output_count,uint64_t cancel) {
    try {
        auto curve=af::read_bezier(points,count); af::handles(curve,closed!=0);
        const auto samples=af::body_path(curve,closed!=0,resolution,cancel);
        af::write_samples(samples,output); *output_count=int(samples.size()); return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
int af_curve_point_edit(double* points,int count,int closed,int index,const double* replacement,int fields,double* output) {
    try {
        auto curve=af::read_bezier(points,count); af::handles(curve,closed!=0);
        if(index<0||index>=count) throw std::runtime_error("Unknown curve point.");
        auto& p=curve[index]; af::edit_point(p,replacement,fields);
        for(int a=0;a<3;++a) { output[a]=p.p[a]; output[a+3]=p.left[a]; output[a+6]=p.right[a]; }
        output[9]=p.radius; output[10]=p.tilt; output[11]=p.lm; output[12]=p.rm;
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
int af_curve_handles(double* points,int count,int closed) {
    try {
        auto curve=af::read_bezier(points,count); af::handles(curve,closed!=0);
        for(int i=0;i<count;++i) {
            for(int axis=0;axis<3;++axis) {
                points[i*13+3+axis]=curve[i].left[axis];
                points[i*13+6+axis]=curve[i].right[axis];
            }
            points[i*13+11]=curve[i].lm%4+4; points[i*13+12]=curve[i].rm%4+4;
        }
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
int af_curve_sample(const double* points,int count,int closed,int resolution,int samples,
                    double start,double span,const double* matrix,double* output,uint64_t cancel) {
    try {
        if(resolution<1||samples<2||!output) throw std::runtime_error("Invalid curve sampling request.");
        af::check_cancel(cancel);
        auto curve=af::read_bezier(points,count); af::handles(curve,closed!=0);
        const auto evaluated=af::evaluated_curve(curve,closed!=0,resolution,Eigen::Map<const af::M4>(matrix));
        const auto uniform=af::resample(evaluated,samples,closed!=0);
        auto result=af::sample_range(uniform,samples,start,span,closed!=0);
        af::frames(result); af::write_samples(result,output); af::check_cancel(cancel);
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
