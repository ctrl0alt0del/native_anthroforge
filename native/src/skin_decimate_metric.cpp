// SPDX-License-Identifier: GPL-2.0-or-later
// Blender 5.0.1 collapse cost, placement, face-flip guard and normal interpolation.
#include "skin_decimate.hpp"
#include <cfloat>
namespace af::skin_decimate {
static float score(const State& state,int a,int b,const V3& point,const V3& delta) {
    const Eigen::Vector4d h(point[0],point[1],point[2],1);
    float value=std::abs(float(h.dot(state.quadrics[a]*h)+h.dot(state.quadrics[b]*h)));
    if(value<1e-12f) value=std::abs(state.normals[a].dot(state.normals[b]))/std::min(-delta.cast<float>().squaredNorm(),-FLT_EPSILON)-value;
    return value;
}
void cost(State& state,int edge,const Eigen::MatrixXd& vertices,const Eigen::MatrixXi& edges,double& value,Eigen::RowVectorXd& point) {
    if(state.visits++%4096==0) check_cancel(state.cancel);
    const int a=edges(edge,0),b=edges(edge,1); const V3 pa=vertices.row(a),pb=vertices.row(b);
    point=(pa+pb)*.5; value=std::numeric_limits<double>::infinity();
    if(!pa.allFinite()||!pb.allFinite()) return;
    const Q4 q=state.quadrics[a]+state.quadrics[b]; const M3 tensor=q.block<3,3>(0,0);
    if(std::abs(tensor.determinant())>1e-8) point=-tensor.inverse()*q.block<3,1>(0,3);
    if(!point.allFinite()) return;
    value=score(state,a,b,point,pa-pb); point=point.cast<float>().cast<double>();
}
bool flips(const Eigen::MatrixXd& vertices,const Eigen::MatrixXi& faces,int id,int a,int b,const F3& point) {
    const auto face=faces.row(id); int found=-1,count=0;
    for(int local=0;local<3;++local) {
        if(!vertices.row(face[local]).allFinite()) return false;
        if(face[local]==a||face[local]==b) { found=local; ++count; }
    }
    if(count!=1) return false;
    const F3 prev=vertices.row(face[(found+2)%3]).cast<float>(),next=vertices.row(face[(found+1)%3]).cast<float>();
    const F3 old=vertices.row(face[found]).cast<float>();
    const F3 first=(prev-next).cross(prev-old),second=(prev-next).cross(prev-point);
    return first.dot(second)<=(first.squaredNorm()+second.squaredNorm())*.01f;
}
void collapsed(State& state,bool success) {
    if(!success) return;
    const int keep=std::min(state.a,state.b);
    const F3 normal=(1-state.factor)*state.normals[state.a]+state.factor*state.normals[state.b];
    state.quadrics[keep]=state.quadrics[state.a]+state.quadrics[state.b];
    state.normals[keep]=normal.normalized();
}
}
