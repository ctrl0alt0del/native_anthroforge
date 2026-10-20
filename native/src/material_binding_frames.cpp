// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_chart.hpp"
#include "anthroforge/attachments.h"
#include <Eigen/LU>

namespace af::material {
static Eigen::Matrix<double,3,2> edges(const M3& points) {
    Eigen::Matrix<double,3,2> result;
    result.col(0)=points.row(1)-points.row(0); result.col(1)=points.row(2)-points.row(0); return result;
}
M4 frame(const Mesh& current,const Location& location,const Tangents& directions,const M4& world,const double* record) {
    M3 points; for(int i=0;i<3;++i) points.row(i)=point(world,current.vertices.row(current.triangles(location.triangle,i)));
    const auto parameters=edges(location.coordinates),geometry=edges(points);
    const Eigen::Matrix2d coefficients=(parameters.transpose()*parameters).fullPivLu().solve(parameters.transpose()*directions);
    const Tangents transported=geometry*coefficients;
    V3 normal=transported.col(0).cross(transported.col(1)),tangent=transported.col(0);
    if(normal.norm()<1e-12||tangent.norm()<1e-12) throw std::runtime_error("Retained material attachment frame is degenerate.");
    normal.normalize(); tangent.normalize(); const V3 bitangent=normal.cross(tangent).normalized();
    M4 result=M4::Identity(); result.block<3,1>(0,0)=bitangent.cross(normal);
    result.block<3,1>(0,1)=bitangent; result.block<3,1>(0,2)=normal;
    result.block<3,1>(0,3)=points.transpose()*location.weights+result.block<3,3>(0,0)*V3(record+15);
    return result;
}
static Eigen::Vector3i indices(const Mesh& mesh,const double* record) {
    for(int i=0;i<28;++i) if(!std::isfinite(record[i])) throw std::runtime_error("Nonfinite retained attachment.");
    Eigen::Vector3i result;
    for(int i=0;i<3;++i) {
        if(record[i]<0||record[i]>=mesh.vertices.rows()||std::floor(record[i])!=record[i]) throw std::runtime_error("Invalid retained material triangle.");
        result[i]=int(record[i]);
    }
    const V3 weights(record+3);
    if(weights.minCoeff()<-1e-6||std::abs(weights.sum()-1)>1e-6) throw std::runtime_error("Invalid retained material weights.");
    return result;
}
static M4 resolve(const Mesh& before,const Mesh& after,const Atlas& a,const Atlas& b,const Indices& index,const M4& world,const double* record,uint64_t cancel) {
    const auto source=coordinates(before,a,indices(before,record));
    const auto position=transported(a.charts[size_t(source.chart)],b.charts.at(size_t(source.chart)),source.coordinates,V3(record+3));
    V3 query=position.point;
    auto location=locate(index,b,source.chart,query,cancel);
    if(location.triangle<0&&after.tissue.kind==5&&query.z()<0) {
        query.z()=1; location=locate(index,b,source.chart,query,cancel);
    }
    if(location.triangle<0) throw std::runtime_error("Retained tissue material location is outside the current surface; restore the crop or explicitly rebind.");
    return frame(after,location,position.tangents,world,record);
}
static void resolve_batch(const Mesh& before,const Mesh& after,const M4& world,int count,const double* records,double* frames,uint64_t cancel) {
    const auto a=atlas(material_basis(before),cancel),b=atlas(material_basis(after),cancel);
    if(a.charts.size()!=b.charts.size()||before.tissue.kind!=after.tissue.kind) throw std::runtime_error("Anatomical material domain changed; explicitly rebind.");
    for(size_t i=0;i<a.charts.size();++i)
        if(a.charts[i].closed_u!=b.charts[i].closed_u||a.charts[i].closed_v!=b.charts[i].closed_v)
            throw std::runtime_error("Material closure changed; explicitly rebind.");
    const auto index=indexed(after,b,cancel);
    for(int i=0;i<count;++i) {
        check_cancel(cancel); Eigen::Map<M4> output(frames+16*i);
        output=resolve(before,after,a,b,index,world,records+28*i,cancel);
    }
}
static int retained_frames(uint64_t reference,uint64_t current,const double* world,int count,const double* records,double* frames,uint64_t cancel) {
    const uint64_t handle=reference==current?current:af_material_binding_surface(reference,current,count,records,cancel);
    if(!handle) return 1;
    const std::vector<int> owners(size_t(count),0);
    const int status=af_point_attachment_resolve(1,&handle,world,count,owners.data(),records,frames,cancel);
    if(handle!=current) af_mesh_release(handle);
    return status;
}
}
int af_material_binding_frames(uint64_t reference,uint64_t current,const double* world,int count,const double* records,double* frames,uint64_t cancel) {
    try {
        if(count<1||count>1000000||!world||!records||!frames) throw std::runtime_error("Invalid material frame buffers.");
        const auto a=af::mesh(reference),b=af::mesh(current);
        const auto first=af::material_basis(*a),second=af::material_basis(*b);
        if(!first.count||!second.count||af::same_basis(first,second))
            return af::material::retained_frames(reference,current,world,count,records,frames,cancel);
        const af::M4 matrix=Eigen::Map<const af::M4>(world);
        if(!matrix.allFinite()||!matrix.fullPivLu().isInvertible()) throw std::runtime_error("Invalid attachment frame.");
        af::material::resolve_batch(*a,*b,matrix,count,records,frames,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_attachment_blend_frames(int count,const double* frames,const double* weights,double* points,uint64_t cancel) {
    try {
        if(count<1||count>1000000||!frames||!weights||!points) throw std::runtime_error("Invalid attachment influence frames.");
        for(int i=0;i<count;++i) {
            af::check_cancel(cancel); af::V3 point=af::V3::Zero();
            const double a=weights[2*i],b=weights[2*i+1];
            if(!std::isfinite(a)||!std::isfinite(b)||a<0||b<0||std::abs(a+b-1)>1e-9) throw std::runtime_error("Invalid attachment influence weights.");
            for(int j=0;j<2;++j) if(weights[2*i+j]>0) point+=weights[2*i+j]*Eigen::Map<const af::M4>(frames+16*(2*i+j)).block<3,1>(0,3);
            if(!point.allFinite()) throw std::runtime_error("Nonfinite attachment influence position.");
            Eigen::Map<af::V3> output(points+3*i); output=point;
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
