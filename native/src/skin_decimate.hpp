#pragma once
#include "construction_internal.hpp"
#include <map>
namespace af::skin_decimate {
using F3=Eigen::Vector3f;
using Q4=Eigen::Matrix4d;
using Edge=std::pair<int,int>;
struct State {
    std::vector<Q4> quadrics;
    std::vector<F3> normals;
    uint64_t cancel=0, budget=0, storage=0;
    int a=-1,b=-1,visits=0;
    float factor=.5f;
};
struct Work { Eigen::MatrixXd vertices; Eigen::MatrixXi faces; };
F3 normal(const Eigen::MatrixXd& vertices,const Eigen::RowVector3i& face);
void prepare(State& state,const Work& input);
void cost(State& state,int edge,const Eigen::MatrixXd& vertices,const Eigen::MatrixXi& edges,double& value,Eigen::RowVectorXd& point);
bool flips(const Eigen::MatrixXd& vertices,const Eigen::MatrixXi& faces,int face,int a,int b,const F3& point);
void collapsed(State& state,bool success);
Work reduce(const Work& input,State& state,int target);
std::shared_ptr<Mesh> evaluate(const Mesh& mesh,int target,uint64_t budget,uint64_t cancel);
}
