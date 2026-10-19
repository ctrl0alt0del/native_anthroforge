#pragma once
#include "construction_internal.hpp"
#include <map>

namespace af::tissue {
using MaterialRow=std::map<int64_t,double>;
struct CropState {
    Points base,own;
    std::vector<double> distances;
    std::vector<MaterialRow> material;
    std::vector<int64_t> sides,parts,sources;
    std::map<std::pair<int64_t,int64_t>,int64_t> intersections;
    Faces faces;
};
CropState crop_inputs(const Mesh& base,const Mesh& own,const double* plane,uint64_t cancel);
std::shared_ptr<Mesh> crop_output(const CropState& state,const TissueDomain& source,uint64_t cancel);
}
