// SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
// Adapted for AnthroForge; see native/migration/BLENDER_PRIMITIVES.md.
// SPDX-License-Identifier: GPL-3.0-or-later
// Interpolation and deformation formulas adapted from Blender 5.0.1 key.cc,
// lattice_deform.cc and lattice.cc; no Blender object/runtime dependency.
#include "construction_internal.hpp"

namespace af {
using Weights=std::array<double,4>;
static Weights cubic_weights(double t,int kind) {
    const double t2=t*t,t3=t2*t;
    if(kind==0) return {0,1-t,t,0};
    if(kind==3) return {(1-3*t+3*t2-t3)/6,(4-6*t2+3*t3)/6,(1+3*t+3*t2-3*t3)/6,t3/6};
    const double fc=kind==1?0.71:0.5;
    return {-fc*t3+2*fc*t2-fc*t,(2-fc)*t3+(fc-3)*t2+1,
            (fc-2)*t3+(3-2*fc)*t2+fc*t,fc*t3-fc*t2};
}
static int grid_index(int u,int v,int w,const int* n) {
    return std::clamp(u,0,n[0]-1)+n[0]*(std::clamp(v,0,n[1]-1)+n[1]*std::clamp(w,0,n[2]-1));
}
static V3 grid_point(int u,int v,int w,const int* n) {
    const int indices[3]={u,v,w}; V3 point;
    for(int axis=0;axis<3;++axis) point[axis]=n[axis]>1?double(indices[axis])/(n[axis]-1)-0.5:0;
    return point;
}
static void validate_grid(const int* n) {
    if(!n||n[0]<1||n[1]<1||n[2]<1||n[0]>64||n[1]>64||n[2]>64||n[0]*n[1]*n[2]>32000)
        throw std::runtime_error("Invalid lattice resolution.");
}
struct LatticeQuery { std::array<Weights,3> weights; std::array<int,3> base; };
static LatticeQuery lattice_query(const V3& point,const int* n,const int* interpolation) {
    LatticeQuery query;
    for(int axis=0;axis<3;++axis) {
        const double coordinate=(point[axis]+0.5)*(n[axis]-1);
        query.base[axis]=int(std::floor(coordinate));
        query.weights[axis]=n[axis]>1?cubic_weights(coordinate-query.base[axis],interpolation[axis]):Weights{0,1,0,0};
    }
    return query;
}
static V3 lattice_delta(const LatticeQuery& q,const double* cage,const int* n,const double* weights,double strength) {
    V3 result=V3::Zero(); double blend=0;
    for(int w=0;w<4;++w) for(int v=0;v<4;++v) for(int u=0;u<4;++u) {
        const int x=std::clamp(q.base[0]+u-1,0,n[0]-1),y=std::clamp(q.base[1]+v-1,0,n[1]-1);
        const int z=std::clamp(q.base[2]+w-1,0,n[2]-1),index=grid_index(x,y,z,n);
        const double factor=q.weights[0][u]*q.weights[1][v]*q.weights[2][w];
        result+=factor*(V3(cage+3*index)-grid_point(x,y,z,n));
        if(weights) blend+=factor*weights[index]*strength;
    }
    return result*(weights?blend:1);
}
static V3 outside_point(int u,int v,int w,const int* n,const double* cage) {
    const int indices[3]={u,v,w}; V3 result=V3::Zero();
    for(int axis=0;axis<3;++axis) {
        int low[3]={u,v,w},high[3]={u,v,w}; low[axis]=0; high[axis]=n[axis]-1;
        const double t=double(indices[axis])/(n[axis]-1);
        const V3 a(cage+3*grid_index(low[0],low[1],low[2],n));
        const V3 b(cage+3*grid_index(high[0],high[1],high[2],n));
        result+=(1-t)*a+t*b;
    }
    return result/3;
}
static void lattice_points(double* points,int count,const double* cage,const int* n,const int* interpolation,
                           const M4& matrix,double strength,const double* weights,const double* cage_weights,uint64_t cancel) {
    const M3 inverse=matrix.inverse().topLeftCorner<3,3>();
    for(int i=0;i<count;++i) {
        if(i%1024==0) check_cancel(cancel);
        Eigen::Map<V3> p(points+3*i);
        const double weight=strength*(weights?weights[i]:1);
        const auto query=lattice_query(point(matrix,p),n,interpolation);
        p+=inverse*lattice_delta(query,cage,n,cage_weights,weight)*weight;
    }
}
}
int af_lattice_resolution(int* n) {
    if(!n||n[0]<1||n[1]<1||n[2]<1||n[0]>64||n[1]>64||n[2]>64) {
        af::set_error("Lattice resolution must be 1–64 on each axis."); return 1;
    }
    while(n[0]*n[1]*n[2]>32000) {
        if(n[0]>=n[1]&&n[0]>=n[2]) --n[0];
        else if(n[1]>=n[0]&&n[1]>=n[2]) --n[1];
        else --n[2];
    }
    return 0;
}
int af_lattice_grid(const int* resolution,double* points) {
    try {
        af::validate_grid(resolution);
        for(int w=0;w<resolution[2];++w) for(int v=0;v<resolution[1];++v) for(int u=0;u<resolution[0];++u) {
            Eigen::Map<af::V3> p(points+3*af::grid_index(u,v,w,resolution));
            p=af::grid_point(u,v,w,resolution);
        }
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
int af_lattice(double* points,int count,const double* cage,const int* resolution,const int* interpolation,
               const double* matrix,double strength,const double* weights,const double* cage_weights,uint64_t cancel) {
    try {
        af::validate_grid(resolution);
        af::lattice_points(points,count,cage,resolution,interpolation,Eigen::Map<const af::M4>(matrix),
                           strength,weights,cage_weights,cancel);
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
int af_lattice_outside(double* cage,const int* n) {
    try {
        af::validate_grid(n);
        for(int w=1;w<n[2]-1;++w) for(int v=1;v<n[1]-1;++v) for(int u=1;u<n[0]-1;++u) {
            Eigen::Map<af::V3> p(cage+3*af::grid_index(u,v,w,n));
            p=af::outside_point(u,v,w,n,cage);
        }
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
