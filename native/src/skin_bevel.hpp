#pragma once
#include "path_internal.hpp"
namespace af::skin {
struct BevelPoint { float vec[3]{},dir[3]{},quat[4]{},tilt=0; };
using BevelPoints=std::vector<BevelPoint>;
void bevel_frames(BevelPoints& points,bool closed);
BevelPoints bevel_points(const Path& path,const M4& frame,uint64_t cancel);
std::shared_ptr<Mesh> fiber_bevel(const Path& path,const M4& frame,double radius,uint64_t cancel);
}
