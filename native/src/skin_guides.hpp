#pragma once
#include "mesh_internal.hpp"
#include "path_internal.hpp"
#include <array>

namespace af::skin_guides {
struct Guides {
    std::vector<std::array<double,10>> samples;
    std::vector<double> points;
    std::vector<int64_t> offsets{0};
};
Guides charts(const Mesh& base,const Mesh& current,const M4& frame,bool reverse,uint64_t cancel);
Guides path(const Path& source,const M4& frame,uint64_t cancel);
}
