// SPDX-License-Identifier: GPL-2.0-or-later
// Blender 5.0.1 decimate quadrics and angle-weighted normals; Blender Authors.
#include "skin_decimate.hpp"
#include <cfloat>
namespace af::skin_decimate {
static float corner_angle(float cosine) {
    const float value=std::abs(cosine);
    const float m=value<1.f?1.f-(1.f-value):1.f;
    const float angle=std::sqrt(1.f-m)*(1.5707963267f+m*(-.213300989f+m*(.077980478f+m*-.02164095f)));
    return cosine<0?3.14159265358979323846f-angle:angle;
}
F3 normal(const Eigen::MatrixXd& vertices,const Eigen::RowVector3i& face) {
    const F3 a=vertices.row(face[0]).cast<float>(),b=vertices.row(face[1]).cast<float>(),c=vertices.row(face[2]).cast<float>();
    return (b-a).cross(c-a).normalized();
}
static Q4 plane(const V3& normal,const V3& point) {
    Eigen::Vector4d equation; equation<<normal,-normal.dot(point);
    return equation*equation.transpose();
}
static void corner(State& state,const Work& input,int face,int local,const F3& normal) {
    const auto ids=input.faces.row(face); const F3 point=input.vertices.row(ids[local]).cast<float>();
    const F3 a=F3(input.vertices.row(ids[(local+1)%3]).cast<float>())-point;
    const F3 b=F3(input.vertices.row(ids[(local+2)%3]).cast<float>())-point;
    state.normals[ids[local]]+=normal*corner_angle(a.normalized().dot(b.normalized()));
}
static void face(State& state,const Work& input,int index,std::map<Edge,std::vector<int>>& edges) {
    const auto ids=input.faces.row(index); const F3 n=normal(input.vertices,ids);
    const F3 center=(input.vertices.row(ids[0]).cast<float>()+input.vertices.row(ids[1]).cast<float>()+input.vertices.row(ids[2]).cast<float>())/3.f;
    const Q4 q=plane(n.cast<double>(),center.cast<double>());
    if(!q.allFinite()) throw std::runtime_error("Skin proxy quadrics exceed numerical range.");
    for(int local=0;local<3;++local) {
        state.quadrics[ids[local]]+=q; corner(state,input,index,local,n);
        edges[std::minmax(ids[local],ids[(local+1)%3])].push_back(index);
    }
}
static void boundary(State& state,const Work& input,const Edge& edge,int face) {
    const F3 a=input.vertices.row(edge.first).cast<float>(),b=input.vertices.row(edge.second).cast<float>();
    const V3 n=(b-a).cross(normal(input.vertices,input.faces.row(face))).cast<double>();
    if(n.norm()<=double(FLT_EPSILON)) return;
    const Q4 q=100*plane(n.normalized(),((a+b)*.5f).cast<double>());
    state.quadrics[edge.first]+=q; state.quadrics[edge.second]+=q;
}
void prepare(State& state,const Work& input) {
    state.quadrics.assign(input.vertices.rows()+1,Q4::Zero());
    state.normals.assign(input.vertices.rows()+1,F3::Zero());
    std::map<Edge,std::vector<int>> edges;
    for(int i=0;i<input.faces.rows();++i) {
        if(i%4096==0) check_cancel(state.cancel);
        face(state,input,i,edges);
    }
    for(auto& value:state.normals) value.normalize();
    for(const auto& item:edges) {
        if(state.visits++%4096==0) check_cancel(state.cancel);
        if(item.second.size()==1) boundary(state,input,item.first,item.second[0]);
    }
}
}
