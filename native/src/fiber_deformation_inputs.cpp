#include "fiber_deformation.hpp"
#include <Eigen/LU>
#include <set>
namespace af::fiber {
double kernel(double x) { x=std::abs(x); return x>=1?0:std::pow(1-x,4)*(1+4*x); }
double distance(const Preparation& v,double a,double b) {
    const double d=std::abs(a-b); return v.path->closed?std::min(d,v.length-d):d;
}
static void points(Preparation& v,const AfFiberReference& in) {
    const M4 world=Eigen::Map<const M4>(in.world); const int count=int(v.path->parameters.size());
    if(!world.allFinite()||!world.fullPivLu().isInvertible()) throw std::runtime_error("Invalid fiber bind frame.");
    v.points.resize(count+3*in.controls,3);
    for(int i=0;i<count;++i) v.points.row(i)=point(world,V3(v.path->samples.data()+11*i));
    for(int i=0;i<in.controls;++i) {
        const auto it=std::lower_bound(v.path->parameters.begin(),v.path->parameters.end(),double(i)-1e-9);
        if(it==v.path->parameters.end()||std::abs(*it-i)>1e-8) throw std::runtime_error("Fiber bind path is missing an authored knot.");
        v.knots.push_back(int(it-v.path->parameters.begin()));
        for(int j=0;j<3;++j) v.points.row(count+3*i+j)=point(world,V3(in.records+13*i+3*j));
    }
}
static void arcs(Preparation& v) {
    const int count=int(v.path->parameters.size()); v.arc.resize(size_t(v.points.rows()),0);
    for(int i=1;i<count;++i) v.arc[size_t(i)]=v.arc[size_t(i-1)]+(v.points.row(i)-v.points.row(i-1)).norm();
    v.length=v.arc[size_t(count-1)];
    if(v.path->closed) v.length+=(v.points.row(0)-v.points.row(count-1)).norm();
    v.length=std::max(v.length,1e-12); v.width=.2*v.length;
    for(int i=count;i<v.points.rows();++i) v.arc[size_t(i)]=v.arc[size_t(v.knots[size_t((i-count)/3)])];
    v.mass.resize(size_t(count));
    for(int i=0;i<count;++i) {
        const double a=i?v.arc[size_t(i)]-v.arc[size_t(i-1)]:(v.path->closed?v.length-v.arc[size_t(count-1)]:0);
        const double b=i+1<count?v.arc[size_t(i+1)]-v.arc[size_t(i)]:(v.path->closed?v.length-v.arc[size_t(i)]:0);
        v.mass[size_t(i)]=std::max((a+b)*.5/v.length,1e-12);
    }
}
static void pins(Preparation& v,const AfFiberReference& in) {
    std::set<int> indices;
    for(int i=0;i<in.pins;++i) {
        const int k=in.indices[i];
        if(k<0||k>=in.controls||!indices.insert(k).second) throw std::runtime_error("Invalid fiber hard pin.");
        v.pins.push_back(v.knots[size_t(k)]); v.pin_owners.push_back(in.owners[2*v.pins.back()]);
    }
    if(!std::is_sorted(v.pins.begin(),v.pins.end())) throw std::runtime_error("Fiber pins must be ordered.");
}
static void validate_influences(const Preparation& v,const AfFiberReference& in,uint64_t cancel) {
    for(int i=0;i<v.points.rows()*2;++i) {
        check_cancel(cancel); const double weight=in.weights[i]; const int owner=in.owners[i];
        if(!std::isfinite(weight)||weight<0||weight>1) throw std::runtime_error("Invalid fiber influence weight.");
        if(weight==0) continue;
        if(owner<0||owner>=in.surfaces) throw std::runtime_error("Invalid fiber support owner.");
        const auto geometry=mesh(in.meshes[owner]); const double* r=in.bindings+28*i;
        for(int j=0;j<28;++j) if(!std::isfinite(r[j])) throw std::runtime_error("Nonfinite fiber binding.");
        for(int j=0;j<3;++j) if(r[j]<0||r[j]>=geometry->vertices.rows()||std::floor(r[j])!=r[j])
            throw std::runtime_error("Invalid fiber reference triangle.");
    }
}
std::shared_ptr<Preparation> prepare(const AfFiberReference& in,uint64_t cancel) {
    if(in.controls<2||in.controls>100000||in.surfaces<1||in.surfaces>10000||in.pins<1||in.pins>in.controls
        ||!in.records||!in.world||!in.owners||!in.weights||!in.bindings||!in.meshes||!in.frames||!in.indices||!in.groups||!in.hints)
        throw std::runtime_error("Invalid smooth fiber inputs.");
    auto v=std::make_shared<Preparation>(); v->path=path(in.path);
    if(v->path->parameters.size()<2||v->path->parameters.size()>262144) throw std::runtime_error("Invalid smooth fiber sample count.");
    points(*v,in); arcs(*v); pins(*v,in); validate_influences(*v,in,cancel);
    prepare_parents(*v,in,cancel); prepare_weights(*v,in,cancel);
    prepare_reconstruction(*v,cancel); return v;
}
V3 curve_point(const Preparation& v,double s) {
    const int count=int(v.path->parameters.size());
    const auto it=std::lower_bound(v.arc.begin(),v.arc.begin()+count,s);
    const int high=int(it-v.arc.begin()),low=std::max(0,high-1),next=high==count?0:high;
    const double end=high==count?v.length:v.arc[size_t(high)],start=v.arc[size_t(low)];
    const double f=end-start>1e-20?(s-start)/(end-start):0;
    return v.points.row(low).transpose()*(1-f)+v.points.row(next).transpose()*f;
}
double pin_width(const Preparation& v,int p) {
    double available=v.length;
    const int count=int(v.pins.size());
    for(int neighbor:{p-1,p+1}) if(v.path->closed||(neighbor>=0&&neighbor<count)) {
        const int index=(neighbor+count)%count;
        if(index!=p) available=std::min(available,distance(v,v.arc[size_t(v.pins[index])],v.arc[size_t(v.pins[p])]));
    }
    return std::max(std::min(v.width,.45*available),1e-12);
}
int nearest_pin(const Preparation& v,double station) {
    const auto next=std::lower_bound(v.pins.begin(),v.pins.end(),station,
        [&](int node,double s) { return v.arc[size_t(node)]<s; });
    const int count=int(v.pins.size()),right=int(next-v.pins.begin());
    int best=std::min(right,count-1); double value=v.length;
    for(int candidate:{right-1,right}) if(v.path->closed||(candidate>=0&&candidate<count)) {
        const int index=(candidate+count)%count; const double d=distance(v,station,v.arc[size_t(v.pins[index])]);
        if(d<value) { value=d; best=index; }
    }
    return best;
}
}
