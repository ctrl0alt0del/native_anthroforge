#pragma once
#include "skin_loops.hpp"
namespace af::skin_ring {
struct Projection { V3 center,normal,first,second; Vertices local; double radius; };
Projection project(const Vertices& ring,double scale=1);
bool inside(const Projection& projection,const V3& point);
bool centered(const Vertices& points,const skin_loops::Plane& plane,double diagonal);
Vertices samples(const Vertices& points,int count,uint64_t cancel);
Vertices canonical(const Vertices& points);
Vertices aligned(const Vertices& reference,const Vertices& points,uint64_t cancel);
Vertices rolled(const Vertices& points,int start,bool reverse=false);
}
