#pragma once
#include "tissue_relaxation.hpp"
#include "anthroforge/tissue_stacking.h"

namespace af::tissue::stacking {
using Row=std::map<int64_t,double>;
struct Prepared {
    std::shared_ptr<Mesh> base,rest,own,visible;
    Vertices reference,positions,directions,material;
    std::vector<int64_t> selected,faces,parts,sources,material_faces,interpolation,fixed,constraints;
    std::vector<double> weights,constraint_weights;
    M4 frame;
    int side=1;
    bool reverse=false;
};
Row row(const TissueDomain& domain,size_t index);
std::shared_ptr<Mesh> visible_material(const Mesh& base,const Mesh& rest,const AfTissueStackSource& config,uint64_t cancel);
Vertices resolved_side(const Mesh& material,const Mesh& own,int side,uint64_t cancel);
Vertices limiting(const Mesh& base,const AfTissueStackSource& config,uint64_t cancel);
void pack_geometry(Prepared& output,const AfTissueStackSource& config,uint64_t cancel);
void pack_constraints(Prepared& output,const AfTissueStackSource& config,uint64_t cancel);
void pack_material(Prepared& output,uint64_t cancel);
std::shared_ptr<Mesh> assemble(const Prepared& first,const Prepared* second,const double* a,int acount,const double* b,int bcount,uint64_t cancel);
std::vector<int64_t> triangles(const Mesh& mesh);
void append_row(const Row& row,std::vector<int64_t>& indices,std::vector<double>& weights);
}
