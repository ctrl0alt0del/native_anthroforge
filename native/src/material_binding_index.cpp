// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_binding.hpp"

namespace af::binding {
Weights weights(const TissueDomain& d,int64_t vertex) {
    Weights result;
    for(auto j=d.offsets[size_t(vertex)];j<d.offsets[size_t(vertex)+1];++j)
        result[d.indices[size_t(j)]]+=d.weights[size_t(j)];
    return result;
}
static void vertex(Index& out,int64_t i) {
    const auto& d=out.current.tissue; const auto a=d.offsets[size_t(i)],b=d.offsets[size_t(i)+1];
    if(b==a+1&&std::abs(d.weights[size_t(a)]-1)<1e-12)
        out.vertices[{d.indices[size_t(a)],d.sides[size_t(i)]}]=i;
}
Index index(const Mesh& current,uint64_t cancel) {
    Index result{current,{},std::vector<std::vector<int>>(size_t(current.tissue.source_count))};
    for(int64_t i=0;i<current.vertices.rows();++i) { check_cancel(cancel); vertex(result,i); }
    for(int i=0;i<int(current.offsets.size())-1;++i) {
        check_cancel(cancel);
        for(auto j=current.offsets[size_t(i)];j<current.offsets[size_t(i)+1];++j)
            for(const auto& [key,value]:weights(current.tissue,current.corners[size_t(j)]))
                if(value>0) result.faces[size_t(key)].push_back(i);
    }
    return result;
}
}
