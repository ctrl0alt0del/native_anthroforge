// SPDX-License-Identifier: GPL-3.0-or-later
// Native port of soft_tissue_curve_inflation.py on accepted curve frames.
#include "tissue_shapes.hpp"
#include <numeric>

namespace af::tissue {
static V3 tangent(const Samples& samples,int i,bool closed) {
    const int count=int(samples.size());
    const int before=closed?(i+count-1)%count:std::max(0,i-1);
    const int after=closed?(i+1)%count:std::min(count-1,i+1);
    return unit(samples[size_t(after)].position-samples[size_t(before)].position);
}
static void ring(Points& points,const Samples& samples,int i,bool closed,const AfTissueShape& s) {
    const V3 normal=unit(samples[size_t(i)].normal)*(s.reverse?-1:1);
    const V3 lateral=unit(normal.cross(tangent(samples,i,closed)));
    const double wave=std::max(0.0,std::sin(3.141592653589793*i/(samples.size()-1)));
    const double taper=closed?1:s.endpoint_taper+(1-s.endpoint_taper)*std::pow(wave,.65);
    for(int j=0;j<s.segments;++j) {
        const double x=-1+2.*j/(s.segments-1),bulge=std::pow(std::max(0.0,1-x*x),s.power);
        points.push_back(samples[size_t(i)].position+lateral*(s.width*taper*x)+normal*(s.amount*taper*bulge));
    }
}
static Points sweep_points(const Samples& samples,bool closed,const AfTissueShape& s,uint64_t cancel) {
    Points points;
    for(int i=0;i<int(samples.size());++i) { check_cancel(cancel); ring(points,samples,i,closed,s); }
    return points;
}
static Faces sweep_faces(int count,int size,bool closed) {
    Faces faces;
    for(int a=0;a<count-int(!closed);++a) {
        const int b=(a+1)%count;
        for(int j=0;j<size-1;++j) faces.push_back({a*size+j,b*size+j,b*size+j+1,a*size+j+1});
    }
    for(int a=0;a<count-int(!closed);++a) faces.push_back({a*size,a*size+size-1,((a+1)%count)*size+size-1,((a+1)%count)*size});
    if(!closed) {
        std::vector<int64_t> first(size),last(size); std::iota(first.rbegin(),first.rend(),0);
        std::iota(last.begin(),last.end(),(count-1)*size); faces.push_back(first); faces.push_back(last);
    }
    return faces;
}
static TissueDomain sweep_domain(int count,int size,bool closed,int64_t faces) {
    auto d=tissue_identity(2,int64_t(count)*size,faces); d.source_count=count; d.ring_size=size; d.closed=closed;
    for(size_t i=0;i<d.indices.size();++i) { d.indices[i]=int64_t(i)/size; d.sides[i]=(i%size==0||i%size==size_t(size-1))?0:1; }
    std::fill(d.faces.begin(),d.faces.end(),-1);
    return d;
}
std::shared_ptr<Mesh> profile_sweep(const double* values,int count,bool closed,const AfTissueShape& s,uint64_t cancel) {
    if(count<(closed?3:2)||int64_t(count)*s.segments>262144) throw std::runtime_error("Invalid tissue sweep sampling budget.");
    const auto samples=read_samples(values,count); const auto faces=sweep_faces(count,s.segments,closed);
    auto reference=s; reference.amount=std::max(s.amount,1e-4); reference.endpoint_taper=std::max(s.endpoint_taper,1e-4);
    auto result=make_mesh(sweep_points(samples,closed,reference,cancel),faces,cancel,false);
    auto actual=s; if(!s.enabled) actual.amount=0;
    const auto points=sweep_points(samples,closed,actual,cancel); Vertices vertices(points.size(),3);
    for(size_t i=0;i<points.size();++i) vertices.row(i)=points[i];
    result=deform_mesh(*result,vertices,cancel,true);
    result->tissue=sweep_domain(count,s.segments,closed,int64_t(faces.size()));
    tissue_validate(result->tissue,result->vertices.rows(),int64_t(faces.size()));
    return result;
}
}
