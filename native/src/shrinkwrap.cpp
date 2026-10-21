// SPDX-FileCopyrightText: Blender Authors
// SPDX-License-Identifier: GPL-3.0-or-later
// Nearest-surface snap semantics adapted from Blender 5.0.1 blenkernel/intern/shrinkwrap.cc.
#include "construction_internal.hpp"
#include <cfloat>

namespace af::wrap {
static V3 stable_direction(V3 delta,const V3& normal,const V3& hit,double offset,double distance) {
    const double sign=(delta.dot(normal)>0)-(delta.dot(normal)<0);
    delta*=sign/distance;
    const double epsilon=(std::abs(offset)+hit.cwiseAbs().sum())*1e-4;
    if(distance<epsilon) delta=normal+(delta-normal)*(distance/epsilon);
    return delta;
}
static V3 snapped(const V3& start,const V3& hit,const V3& normal,double offset,int mode) {
    if((mode==0||mode==3)&&offset==0) return hit;
    const V3 delta=start-hit;
    const double distance=delta.norm(),side=(delta.dot(normal)>0)-(delta.dot(normal)<0);
    double force=mode==1?-1:(mode==0?0:1);
    const bool snap=mode==0||mode==3;
    if(distance<FLT_EPSILON) return hit+normal*((snap||offset>0)?offset*force:0);
    if(force==0) force=side;
    if(!snap&&side*distance*force>=offset) return start;
    return hit+stable_direction(delta,normal,hit,offset,distance)*(offset*force);
}
static V3 nearest_point(const Mesh& target,const V3& start,double offset,int mode) {
    int index=-1; Eigen::RowVector3d hit;
    target.tree.squared_distance(target.vertices,target.triangles,start.transpose(),index,hit);
    if(index<0) throw std::runtime_error("Shrinkwrap target has no usable surface.");
    const auto face=target.triangles.row(index);
    const V3 a=target.vertices.row(face[1])-target.vertices.row(face[0]);
    const V3 b=target.vertices.row(face[2])-target.vertices.row(face[0]);
    return snapped(start,hit.transpose(),a.cross(b).normalized(),offset,mode);
}
static void deform(double* values,int count,const Mesh& target,const M4& matrix,
                   double offset,int mode,double strength,const double* weights,uint64_t cancel) {
    const M4 inverse=matrix.inverse();
    for(int i=0;i<count;++i) {
        if(i%256==0) check_cancel(cancel);
        const double weight=strength*(weights?weights[i]:1);
        if(weight==0) continue;
        Eigen::Map<V3> source(values+3*i);
        const V3 hit=nearest_point(target,point(matrix,source),offset,mode);
        source+=weight*(point(inverse,hit)-source);
    }
}
}
int af_shrinkwrap(double* points,int count,uint64_t target,const double* matrix,double offset,
                  int mode,double strength,const double* weights,uint64_t cancel) {
    try {
        const auto geometry=af::mesh(target);
        if(!geometry->prepared||!geometry->triangles.rows()) throw std::runtime_error("Shrinkwrap needs accepted target geometry.");
        if(count<0||mode<0||mode>3||!std::isfinite(offset)||!std::isfinite(strength)||strength<0||strength>1)
            throw std::runtime_error("Invalid Shrinkwrap parameters.");
        af::wrap::deform(points,count,*geometry,af::M4(matrix),offset,mode,strength,weights,cancel);
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
