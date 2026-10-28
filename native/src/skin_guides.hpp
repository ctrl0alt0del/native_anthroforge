#pragma once
#include "mesh_internal.hpp"
#include "path_internal.hpp"
#include <array>
#include "anthroforge/skin_guides.h"

namespace af::skin_guides {
struct Guides {
    std::vector<std::array<double,10>> samples;
    std::vector<double> points;
    std::vector<int64_t> offsets{0};
    std::vector<std::array<int64_t,2>> regions;
};
Guides merge(const AFGuideInput* inputs,int count,uint64_t cancel);
Guides half(const AFGuideInput& input,const double* plane,uint64_t cancel);
Guides charts(const Mesh& base,const Mesh& current,const M4& frame,bool reverse,uint64_t cancel);
Guides path(const Path& source,const M4& frame,uint64_t cancel);
}
