// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_binding.hpp"
#include <Eigen/LU>

namespace af::binding {
using V4=Eigen::Vector4d;
using Rows=std::map<int64_t,V4>;
static int corners(const Mesh& mesh,int face) { return int(mesh.offsets[size_t(face)+1]-mesh.offsets[size_t(face)]); }
static int64_t vertex(const Mesh& mesh,int face,int corner) { return mesh.corners[size_t(mesh.offsets[size_t(face)]+corner)]; }
static Rows coefficients(const Mesh& mesh,int face) {
    Rows rows; const int count=corners(mesh,face);
    if(count<3||count>4) throw std::runtime_error("Material bindings require triangular or quad tissue faces.");
    for(int j=0;j<count;++j) for(const auto& [key,value]:weights(mesh.tissue,vertex(mesh,face,j))) {
        auto found=rows.try_emplace(key,V4::Zero()).first; found->second[j]=value;
    }
    return rows;
}
static bool barycentric(Rows rows,const Weights& query,V4& bary,bool inside,int count) {
    V4 rhs=V4::Zero(); rhs.head(count).setOnes(); Eigen::Matrix4d gram=rhs*rhs.transpose();
    if(count==3) gram(3,3)=1;
    for(const auto& [key,row]:rows) gram+=row*row.transpose();
    for(const auto& [key,value]:query) rhs+=rows.try_emplace(key,V4::Zero()).first->second*value;
    const Eigen::FullPivLU<Eigen::Matrix4d> solve(gram);
    if(!solve.isInvertible()) return false;
    bary=solve.solve(rhs);
    if(!bary.allFinite()||(inside&&bary.minCoeff()<-1e-8)||std::abs(bary.sum()-1)>1e-8) return false;
    for(const auto& [key,row]:rows) {
        const auto found=query.find(key); const double value=found==query.end()?0:found->second;
        if(std::abs(row.dot(bary)-value)>1e-8) return false;
    }
    return true;
}
static bool matching_side(const Mesh& mesh,int face,int64_t side) {
    for(int j=0;j<corners(mesh,face);++j) {
        const auto current=mesh.tissue.sides[size_t(vertex(mesh,face,j))];
        if(current&&current!=side) return false;
    }
    return true;
}
static int64_t direct(const Index& index,const Weights& query,int64_t side) {
    if(query.size()!=1||std::abs(query.begin()->second-1)>1e-12) return -1;
    for(auto candidate:{side,int64_t(0)}) {
        const auto found=index.vertices.find({query.begin()->first,candidate});
        if(found!=index.vertices.end()) return found->second;
    }
    if(side==2&&index.current.tissue.kind==5) return direct(index,query,1);
    return -1;
}
static std::vector<int> candidates(const Index& index,const Weights& query) {
    std::vector<int> result;
    for(const auto& [key,value]:query) if(value>0) {
        const auto& faces=index.faces.at(size_t(key)); result.insert(result.end(),faces.begin(),faces.end());
    }
    std::sort(result.begin(),result.end()); result.erase(std::unique(result.begin(),result.end()),result.end());
    return result;
}
Weights material_coordinates(const Index& index,const Weights& query,int64_t side,uint64_t cancel,bool inside) {
    const auto& mesh=index.current; side=side?side:1;
    const auto known=direct(index,query,side);
    if(known>=0) return {{known,1}};
    for(int face:candidates(index,query)) {
        check_cancel(cancel); V4 bary;
        if(!matching_side(mesh,face,side)||!barycentric(coefficients(mesh,face),query,bary,inside,corners(mesh,face))) continue;
        Weights value;
        for(int j=0;j<corners(mesh,face);++j) value[vertex(mesh,face,j)]=bary[j];
        return value;
    }
    if(side==2&&mesh.tissue.kind==5) return material_coordinates(index,query,1,cancel,inside);
    throw std::runtime_error("Retained tissue material location is outside the current surface; restore the crop or explicitly rebind.");
}
V3 material_point(const Index& index,const Weights& query,int64_t side,uint64_t cancel,bool inside) {
    V3 value=V3::Zero();
    for(const auto& [vertex,weight]:material_coordinates(index,query,side,cancel,inside))
        value+=index.current.vertices.row(vertex).transpose()*weight;
    return value;
}
}
