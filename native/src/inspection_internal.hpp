#pragma once
#include "mesh_internal.hpp"
#include "material_binding.hpp"
#include <array>

namespace af::inspection {
struct Comparison {
    std::shared_ptr<Mesh> reference,target;
    std::vector<std::vector<float>> chunks;
    std::array<double,4> stats{}; // minimum, maximum, mean, RMS, in world metres
};
Comparison& comparison(uint64_t handle);
bool canonical(const Mesh& a,const Mesh& b);
Vertices mapped(const Mesh& reference,const Mesh& target,const Vertices& values,bool source,uint64_t cancel);
V3 sample(const Mesh& mesh,const Vertices& values,int triangle,const V3& bary);
V3 mapped_sample(const Mesh& reference,const Mesh& target,const Vertices& values,bool source,int triangle,const V3& bary,uint64_t cancel);
void witness(const Mesh& mesh,int triangle,const V3& bary);
V3 source_point(const Mesh& mesh,const Mesh& base,int64_t vertex);
void buffers(Comparison& out,const Vertices& deltas,uint64_t cancel);
}
