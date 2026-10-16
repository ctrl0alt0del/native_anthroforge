// SPDX-FileCopyrightText: 2005 Blender Authors
// Adapted for AnthroForge; see native/migration/BLENDER_PRIMITIVES.md.
// SPDX-License-Identifier: GPL-3.0-or-later
// Blender 5.0.1 colortools.cc CurveMapping handle and 32/256-sample table algorithms.
#include "construction_internal.hpp"

namespace af {
using V2=Eigen::Vector2d;
struct MapPoint { V2 p,left,right; int mode; };
static void clamp_handles(MapPoint& p,const V2& previous,const V2& next) {
    const double a=previous.y()-p.p.y(),b=next.y()-p.p.y();
    if(a*b>=0) p.left.y()=p.right.y()=p.p.y();
    else {
        p.left.y()=a<=0?std::max(previous.y(),p.left.y()):std::min(previous.y(),p.left.y());
        p.right.y()=a<=0?std::min(next.y(),p.right.y()):std::max(next.y(),p.right.y());
    }
}
static MapPoint map_point(const double* points,const int* modes,int i,int count) {
    MapPoint result{V2(points+2*i),V2::Zero(),V2::Zero(),modes[i]};
    const V2 previous=i?V2(points+2*i-2):V2(2*result.p-V2(points+2));
    const V2 next=i+1<count?V2(points+2*i+2):V2(2*result.p-previous);
    const V2 a=result.p-previous,b=next-result.p;
    if(result.mode==1) { result.left=result.p-a/3; result.right=result.p+b/3; }
    else {
        V2 direction=a.normalized()+b.normalized(); const double length=direction.norm()*2.5614;
        if(length>1e-20) direction/=length;
        result.left=result.p-a.norm()*direction; result.right=result.p+b.norm()*direction;
        if(result.mode==2&&i>0&&i+1<count) clamp_handles(result,previous,next);
    }
    return result;
}
static void endpoint(MapPoint& p,const MapPoint& neighbor,bool first) {
    if(p.mode!=0) return;
    V2 goal=first?neighbor.left:neighbor.right;
    goal.x()=first?std::max(goal.x(),p.p.x()):std::min(goal.x(),p.p.x());
    const V2 vector=goal-p.p;
    const double length=(first?p.right-p.p:p.left-p.p).norm();
    if(vector.norm()<1e-12) return;
    const V2 delta=vector.normalized()*length;
    p.left=p.p+(first?-delta:delta); p.right=p.p+(first?delta:-delta);
}
static void sample_segment(MapPoint a,MapPoint b,std::vector<V2>& output) {
    const double length=b.p.x()-a.p.x();
    const double handles=std::abs(a.right.x()-a.p.x())+std::abs(b.left.x()-b.p.x());
    if(handles>length) { a.right=a.p+(a.right-a.p)*length/handles; b.left=b.p+(b.left-b.p)*length/handles; }
    for(int i=0;i<32;++i) {
        const double t=double(i)/31,s=1-t;
        output.push_back(s*s*s*a.p+3*s*s*t*a.right+3*s*t*t*b.left+t*t*t*b.p);
    }
}
static double extend(const MapPoint& p,double x,bool first,bool extrapolate) {
    if(!extrapolate||std::abs(x-p.p.x())<1e-6) return p.p.y();
    const V2 direction=(p.left-p.p).normalized();
    if(std::abs(direction.x())<1e-20) return p.p.y()+direction.y()*(first?10000:-10000);
    return p.p.y()+direction.y()*(x-p.p.x())/direction.x();
}
static double table_value(const std::vector<V2>& samples,const std::vector<MapPoint>& points,double x,bool extrapolate) {
    const auto next=std::upper_bound(samples.begin(),samples.end(),x,[](double v,const V2& p){return v<p.x();});
    if(next==samples.begin()) return extend(points.front(),x,true,extrapolate);
    if(next==samples.end()) return extend(points.back(),x,false,extrapolate);
    const V2& previous=*(next-1); const double width=next->x()-previous.x();
    const double factor=width>1e-7?(next->x()-x)/width:0;
    return factor*previous.y()+(1-factor)*next->y();
}
static void mapping(const double* values,const int* modes,int count,bool extrapolate,double* table) {
    if(count<2) throw std::runtime_error("Falloff curve needs two points.");
    std::vector<MapPoint> points;
    for(int i=0;i<count;++i) points.push_back(map_point(values,modes,i,count));
    if(count>2) { endpoint(points.front(),points[1],true); endpoint(points.back(),points[count-2],false); }
    std::vector<V2> samples;
    for(int i=1;i<count;++i) sample_segment(points[i-1],points[i],samples);
    const double low=std::min(0.0,points.front().p.x()),high=std::max(1.0,points.back().p.x());
    for(int i=0;i<=256;++i) {
        table[2*i]=low+(high-low)*i/256;
        table[2*i+1]=table_value(samples,points,table[2*i],extrapolate);
    }
}
}
int af_curve_mapping(const double* points,const int* modes,int count,int extrapolate,double* table) {
    try { af::mapping(points,modes,count,extrapolate!=0,table); return 0; }
    catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
