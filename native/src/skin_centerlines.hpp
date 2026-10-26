#pragma once
#include "component_index.hpp"

namespace af::skin {
struct LineHit { V3 point=V3::Zero(); double distance=INFINITY,parameter=0; int segment=-1,owner=-1,local=-1; };
struct Centerlines {
    ComponentIndex index;
    std::vector<int> owners,locals;
    LineHit nearest(const V3& point,double reach,const std::vector<int>& excluded={}) const;
};
std::shared_ptr<Centerlines> centerlines(const double* xyz,int vertices,const int64_t* edges,
    const int* owners,int count,int sources,uint64_t cancel);
}
