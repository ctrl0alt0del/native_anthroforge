#pragma once
#include "construction_internal.hpp"
#include "bmesh.hh"
namespace af::blender_mesh {
struct Owned {
    BMesh* value;
    std::vector<BMVert*> vertices;
    explicit Owned(const Mesh& mesh,uint64_t cancel);
    ~Owned() { BM_mesh_free(value); }
    Owned(const Owned&)=delete;
    Owned& operator=(const Owned&)=delete;
};
std::vector<std::array<int,2>> edge_order(const Mesh& source,uint64_t cancel);
std::shared_ptr<Mesh> result(BMesh* mesh,uint64_t cancel);
std::shared_ptr<Mesh> decimate(const Mesh& source,int target,uint64_t cancel);
std::shared_ptr<Mesh> half(const Mesh& source,const V3& origin,const V3& normal,uint64_t cancel);
}
