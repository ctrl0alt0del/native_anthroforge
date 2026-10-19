#pragma once
#include "construction_internal.hpp"

namespace af::tissue {
std::shared_ptr<Mesh> compose_envelope(const Mesh& a,const Mesh& b,bool flip,uint64_t cancel);
std::shared_ptr<Mesh> crop_material(const Mesh& base,const Mesh& own,const double* plane,uint64_t cancel);
std::shared_ptr<Mesh> crop_envelope(const Mesh& base,const Mesh& own,const double* plane,uint64_t cancel);
}
