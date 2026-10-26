// Owned, serial libigl topology traversal with Blender's collapse policies.
#define IGL_PARALLEL_FOR_FORCE_SERIAL
#include "skin_decimate.hpp"
#include <igl/decimate.h>
#include <igl/connect_boundary_to_infinity.h>
#include <igl/max_faces_stopping_condition.h>
#include <igl/circulation.h>
#include <igl/remove_unreferenced.h>
#include <cfloat>
namespace af::skin_decimate {
static bool valid(State& s,int e,const Eigen::MatrixXd& v,const Eigen::MatrixXi& f,const Eigen::MatrixXi& edges,const Eigen::VectorXi& emap,const Eigen::MatrixXi& ef,const Eigen::MatrixXi& ei,const Eigen::MatrixXd& c) {
    check_cancel(s.cancel); s.a=edges(e,0); s.b=edges(e,1); const F3 p=c.row(e).cast<float>();
    const F3 a=v.row(s.a).cast<float>(),b=v.row(s.b).cast<float>(),d=b-a;
    if(!p.allFinite()||!a.allFinite()||!b.allFinite()) return false;
    s.factor=d.squaredNorm()>FLT_EPSILON*FLT_EPSILON?(p-a).dot(d)/d.squaredNorm():.5f;
    std::vector<int> vertices,faces;
    for(bool direction:{false,true}) {
        igl::circulation(e,direction,f,emap,ef,ei,vertices,faces);
        for(int id:faces) if(flips(v,f,id,s.a,s.b,p)) return false;
    }
    return true;
}
static igl::decimate_cost_and_placement_callback metric(State& state) {
    return [&](int e,const auto& v,const auto&,const auto& edges,const auto&,const auto&,const auto&,double& value,auto& p) {
        cost(state,e,v,edges,value,p);
    };
}
static igl::decimate_pre_collapse_callback before(State& state) {
    return [&](const auto& v,const auto& f,const auto& edges,const auto& emap,const auto& ef,const auto& ei,const auto& queue,const auto&,const auto& c,int e) {
        if(state.storage+queue.size()*sizeof(std::tuple<double,int,int>)>state.budget)
            throw std::runtime_error("Skin proxy collapse queue exceeds worker memory budget.");
        return valid(state,e,v,f,edges,emap,ef,ei,c);
    };
}
static igl::decimate_post_collapse_callback after(State& state) {
    return [&](const auto&,const auto&,const auto&,const auto&,const auto&,const auto&,const auto&,const auto&,const auto&,int,int,int,int,int,bool success) {
        collapsed(state,success);
    };
}
static Work compact(const Work& output,const Eigen::VectorXi& births,int original) {
    Eigen::MatrixXi faces(output.faces.rows(),3); int count=0;
    for(int i=0;i<output.faces.rows();++i) if(births[i]<original) faces.row(count++)=output.faces.row(i);
    if(!count) throw std::runtime_error("Skin proxy requires manifold triangles with manifold boundary vertices.");
    faces.conservativeResize(count,3); Work result; Eigen::VectorXi map,keep;
    igl::remove_unreferenced(output.vertices,faces,result.vertices,result.faces,map,keep);
    return result;
}
Work reduce(const Work& input,State& state,int target) {
    Work closed,output; Eigen::VectorXi births,identities;
    igl::connect_boundary_to_infinity(input.vertices,input.faces,closed.vertices,closed.faces);
    check_cancel(state.cancel); int remaining=int(input.faces.rows());
    igl::decimate(closed.vertices,closed.faces,metric(state),
        igl::max_faces_stopping_condition(remaining,input.faces.rows(),target),before(state),after(state),
        output.vertices,output.faces,births,identities);
    check_cancel(state.cancel); return compact(output,births,int(input.faces.rows()));
}
}
