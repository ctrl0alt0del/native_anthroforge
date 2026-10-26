#pragma once
#include "skin_loops.hpp"
namespace af::skin_annuli {
using skin_loops::Context;
using skin_loops::Loop;
using skin_loops::Plane;
using Quad=std::array<int64_t,4>;
constexpr int rows=5;
struct Patch {
    int first=-1,second=-1,mode=0,mirror=-1,inversions=0,segments=0;
    Vertices points,normals;
    std::vector<Quad> faces;
};
using Patches=std::vector<Patch>;
struct Frame { V3 center,first,second,normal; };
int segment_count(const Loop& outer,const Loop& inner,double diagonal);
Loop aligned(const Loop& reference,const Loop& candidate);
void finish(Context& context,Patch& patch);
Patch direct(Context& context,const Loop& outer,const Loop& inner);
Patch planar(Context& context,const Loop& outer,const Loop& inner);
Patch radial(Context& context,const Loop& outer);
Patch choose(Context& context,const Loop& outer,const Loop& inner);
bool symmetry_candidate(const Loop& outer,const Loop& inner,const Plane& plane);
void symmetrize(Context& context,Patch& patch);
void mirror_pairs(Context& context,Patches& patches);
Frame frame(const Vertices& points,const Plane& plane);
Eigen::MatrixXd smooth(const Eigen::MatrixXd& values,int harmonics);
Loop ray_project(Context& context,const Vertices& points,const V3& normal);
std::shared_ptr<const Patches> get(uint64_t handle);
uint64_t retain(Patches patches);
}
