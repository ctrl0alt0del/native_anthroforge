// SPDX-License-Identifier: GPL-3.0-or-later
// Adapted from AnthroForge core/shortcuts/owner_backsolve.py: retained anchor, translation only.
#include "mesh_internal.hpp"
#include "anthroforge/attachments.h"

namespace af::shortcut {
static V3 face_center(const Mesh& mesh,int index) {
    const auto begin=mesh.offsets.at(index),end=mesh.offsets.at(index+1);
    if(begin>=end) throw std::runtime_error("Retained child anchor face is empty.");
    V3 sum=V3::Zero();
    for(auto i=begin;i<end;++i) sum+=mesh.vertices.row(mesh.corners[i]).transpose();
    return sum/double(end-begin);
}
static V3 anchor(uint64_t handle,const M4& world,const double* offset,int mode,int index,const double* fallback) {
    if(mode<0||mode>2) throw std::runtime_error("Unknown shortcut child-anchor mode.");
    if(mode==2) return world.block<3,1>(0,3);
    if(handle&&index>=0) {
        const auto source=mesh(handle); const M4 frame=geometry_matrix(world.data(),offset);
        if(mode==1&&index<source->vertices.rows()) return point(frame,source->vertices.row(index));
        if(mode==0&&index+1<int(source->offsets.size())) return point(frame,face_center(*source,index));
    }
    return point(world,V3(fallback));
}
static void validate(const M4& world,const M4& parent,const double* offset,const double* fallback) {
    if(!world.allFinite()||!parent.allFinite()||!parent.fullPivLu().isInvertible()||
       !V3(offset).allFinite()||!V3(fallback).allFinite())
        throw std::runtime_error("Shortcut anchor inputs must be finite with an invertible parent frame.");
}
static V3 retained(uint64_t child,const double* world,const double* parent,const double* offset,
                   int mode,int index,const double* fallback) {
    const M4 cw=Eigen::Map<const M4>(world),pw=Eigen::Map<const M4>(parent);
    validate(cw,pw,offset,fallback);
    return point(pw.inverse(),anchor(child,cw,offset,mode,index,fallback));
}
static M4 backsolve(uint64_t child,const double* world,const double* parent,const double* offset,
                    int mode,int index,const double* fallback,const double* target) {
    M4 cw=Eigen::Map<const M4>(world); const M4 pw=Eigen::Map<const M4>(parent);
    validate(cw,pw,offset,fallback);
    if(!V3(target).allFinite()) throw std::runtime_error("Retained shortcut target must be finite.");
    const V3 delta=point(pw,V3(target))-anchor(child,cw,offset,mode,index,fallback);
    if(delta.norm()>1e-7) cw.block<3,1>(0,3)+=delta;
    return cw;
}
}

int af_shortcut_owner_anchor(uint64_t child,const double* world,const double* parent,const double* offset,
                             int mode,int index,const double* fallback,double* output) {
    try {
        Eigen::Map<af::V3> result(output);
        result=af::shortcut::retained(child,world,parent,offset,mode,index,fallback);
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_shortcut_owner_backsolve(uint64_t child,const double* world,const double* parent,const double* offset,
                                int mode,int index,const double* fallback,const double* target,double* output) {
    try {
        Eigen::Map<af::M4> result(output);
        result=af::shortcut::backsolve(child,world,parent,offset,mode,index,fallback,target);
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
