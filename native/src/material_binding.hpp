// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "construction_internal.hpp"
#include <map>

namespace af::binding {
using Weights=std::map<int64_t,double>;
struct Index {
    const Mesh& current;
    std::map<std::pair<int64_t,int64_t>,int64_t> vertices;
    std::vector<std::vector<int>> faces;
};
Weights weights(const TissueDomain& domain,int64_t vertex);
Index index(const Mesh& current,uint64_t cancel);
Weights material_coordinates(const Index& index,const Weights& location,int64_t side,uint64_t cancel,bool inside=true);
V3 material_point(const Index& index,const Weights& location,int64_t side,uint64_t cancel,bool inside=true);
}
