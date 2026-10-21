#pragma once
#include "inspection_internal.hpp"
namespace af::painting {
using Mapping=std::vector<binding::Weights>;
struct View { V3 origin,right,up,forward; double scale; bool perspective; };
struct Occluder { std::shared_ptr<Mesh> geometry; M4 inverse; };
struct Prepared {
    std::shared_ptr<Mesh> target,reference;
    Mapping mapping;
    Vertices projected;
    std::vector<uint8_t> visible;
    int count=0;
};
Prepared& prepared(uint64_t handle);
Mapping correspondence(const Mesh& target,const Mesh* reference,bool source,int count,uint64_t cancel);
View view(const double* values);
void project(Prepared& out,const M4& frame,const View& camera,const std::vector<Occluder>& occluders,uint64_t cancel);
std::unique_ptr<inspection::Comparison> stroke(const Prepared& data,const double* baseline,const double* samples,
    int count,const double* settings,double* values,uint64_t cancel);
}
