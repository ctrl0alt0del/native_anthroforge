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
static M4 material_backsolve(uint64_t reference,uint64_t current,const double* world,const double* parent,
                             const double* offset,const double* record,const double* target) {
    M4 cw=Eigen::Map<const M4>(world); const M4 pw=Eigen::Map<const M4>(parent);
    const M4 geometry=geometry_matrix(world,offset); M4 resolved;
    validate(cw,pw,offset,target);
    if(af_material_binding_frames(reference,current,geometry.data(),1,record,resolved.data(),0))
        throw std::runtime_error("Cannot resolve retained shortcut owner material anchor.");
    const V3 delta=point(pw,V3(target))-resolved.block<3,1>(0,3);
    if(delta.norm()>1e-7) cw.block<3,1>(0,3)+=delta;
    return cw;
}
}

int af_shortcut_owner_material_capture(uint64_t child,const double* world,const double* offset,
                                       int mode,int index,const double* fallback,double* output) {
    try {
        const af::M4 cw=Eigen::Map<const af::M4>(world),geometry=af::geometry_matrix(world,offset);
        const af::V3 position=af::shortcut::anchor(child,cw,offset,mode,index,fallback);
        int forced=0,target=-1;
        return af_point_attachment_capture(1,&child,geometry.data(),1,position.data(),&forced,&target,output,0);
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_shortcut_owner_material_backsolve(uint64_t reference,uint64_t current,const double* world,
    const double* parent,const double* offset,const double* record,const double* target,double* output) {
    try {
        Eigen::Map<af::M4> result(output);
        result=af::shortcut::material_backsolve(reference,current,world,parent,offset,record,target);
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
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
