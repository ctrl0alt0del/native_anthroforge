#include "anthroforge/inspection.h"
#include "anthroforge/sections.h"
#include "mesh_internal.hpp"
#include <Eigen/SVD>
#include <map>

namespace af::inspection {
struct Metrics {
    Eigen::AlignedBox3d bounds;
    double min_edge=INFINITY,max_edge=0,min_quality=1;
    std::map<std::pair<int,int>,std::pair<int,int>> edges;
    int64_t degenerate=0;
};
static void edge(Metrics& out,int a,int b,double length) {
    out.min_edge=std::min(out.min_edge,length); out.max_edge=std::max(out.max_edge,length);
    auto& value=out.edges[std::minmax(a,b)]; ++value.first; value.second+=a<b?1:-1;
}
static void face(Metrics& out,const Mesh& mesh,const M4& frame,int index) {
    V3 p[3]; const Eigen::Vector3i ids=mesh.triangles.row(index);
    for(int j=0;j<3;++j) p[j]=point(frame,mesh.vertices.row(ids[j]));
    double longest=0;
    for(int j=0;j<3;++j) { const double length=(p[j]-p[(j+1)%3]).norm();
        longest=std::max(longest,length); edge(out,ids[j],ids[(j+1)%3],length); }
    const double area=(p[1]-p[0]).cross(p[2]-p[0]).norm();
    const double quality=longest>0?area/(longest*longest):0;
    out.min_quality=std::min(out.min_quality,quality); if(quality<=1e-12) ++out.degenerate;
}
static void topology(const Metrics& out,int64_t* counts) {
    counts[0]=int64_t(out.edges.size()); counts[1]=0; counts[2]=0; counts[3]=0; counts[4]=out.degenerate;
    for(const auto& [key,value]:out.edges) {
        if(value.first==1) ++counts[1];
        if(value.first>2) ++counts[2];
        if(value.first==2&&value.second!=0) ++counts[3];
    }
}
static void axes(const V3& low,const V3& high,double* lines) {
    for(int axis=0;axis<3;++axis) { V3 end=low; end[axis]=high[axis];
        std::copy(low.data(),low.data()+3,lines+6*axis); std::copy(end.data(),end.data()+3,lines+6*axis+3); }
}
static void summary(const Metrics& out,const M4& frame,double* values,double* lines) {
    const auto lo=out.bounds.min(),hi=out.bounds.max(); const V3 spans=hi-lo;
    std::copy(lo.data(),lo.data()+3,values); std::copy(hi.data(),hi.data()+3,values+3);
    std::copy(spans.data(),spans.data()+3,values+6); axes(lo,hi,lines);
    values[9]=std::isfinite(out.min_edge)?out.min_edge:0; values[10]=out.max_edge; values[11]=out.min_quality;
    const Eigen::Vector3d singular=frame.block<3,3>(0,0).jacobiSvd().singularValues();
    values[12]=singular[2]>0?singular[0]/singular[2]:0;
    values[13]=spans.maxCoeff()>0?std::max(lo.cwiseAbs().maxCoeff(),hi.cwiseAbs().maxCoeff())/spans.maxCoeff():0;
}
static void measure(const Mesh& mesh,const M4& frame,double* values,int64_t* counts,double* lines,uint64_t cancel) {
    if(!frame.allFinite()||mesh.vertices.rows()==0) throw std::runtime_error("Measurements need a finite transform and nonempty surface.");
    Metrics out;
    for(int i=0;i<mesh.vertices.rows();++i) { check_cancel(cancel); const V3 p=point(frame,mesh.vertices.row(i));
        if(!p.allFinite()) throw std::runtime_error("The surface contains nonfinite coordinates."); out.bounds.extend(p); }
    for(int i=0;i<mesh.triangles.rows();++i) { check_cancel(cancel); face(out,mesh,frame,i); }
    topology(out,counts); summary(out,frame,values,lines);
}
static void section(const std::vector<double>& points,int count,const Eigen::Vector4d& plane,double* values,double* lines) {
    const V3 n=plane.head<3>().normalized(); const V3 u=n.unitOrthogonal(),v=n.cross(u);
    Eigen::AlignedBox2d bounds;
    for(int i=0;i<count;++i) { const V3 p(points.data()+3*i); bounds.extend(Eigen::Vector2d(u.dot(p),v.dot(p))); }
    const auto lo=bounds.min(),hi=bounds.max(); const V3 start=n*(-plane[3]/plane.head<3>().norm())+u*lo[0]+v*lo[1];
    values[0]=hi[0]-lo[0]; values[1]=hi[1]-lo[1];
    std::copy(u.data(),u.data()+3,values+2); std::copy(v.data(),v.data()+3,values+5);
    for(int i=0;i<2;++i) { const V3 end=start+(i==0?u:v)*values[i];
        std::copy(start.data(),start.data()+3,lines+6*i); std::copy(end.data(),end.data()+3,lines+6*i+3); }
}
}
int af_inspection_metrics(uint64_t handle,const double* frame,double* values,int64_t* counts,double* lines,uint64_t cancel) {
    try { af::inspection::measure(*af::mesh(handle),af::M4(frame),values,counts,lines,cancel); return 0; }
    catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_inspection_section_spans(uint64_t handle,const double* frame,const double* plane,double* values,double* lines,int64_t* counts,uint64_t cancel) {
    try {
        std::vector<double> points(32768*3);
        if(af_section_contours(handle,frame,plane,32768,points.data(),counts,cancel)) return 1;
        std::fill(values,values+8,0); std::fill(lines,lines+12,0);
        if(counts[0]) af::inspection::section(points,int(counts[0]),Eigen::Vector4d(plane),values,lines);
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
