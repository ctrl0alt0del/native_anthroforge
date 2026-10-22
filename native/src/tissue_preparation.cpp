// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_preparation.hpp"
#include "tissue_branches.hpp"
#include "tissue_kernel.hpp"

namespace af::tissue {
int preparation_mode(const AfTissueInflation& s) {
    return !s.enabled||(s.mode==1&&s.amount<=0)?0:s.mode;
}
static PreparedGrid prepare_grid(const Mesh& source,MaterialGrid grid,const AfTissueInflation& s,uint64_t cancel) {
    validate_inflation(s,grid); PreparedGrid out; out.grid=std::move(grid);
    out.mode=preparation_mode(s); out.direction=s.direction; out.reversed=grid_reversed(source,out.grid);
    for(auto id:out.grid.indices) {
        check_cancel(cancel); const auto p=source.vertices.row(id); out.base.push_back({p.x(),p.y(),p.z()});
    }
    if(out.mode==2) {
        out.limit=1e-12*std::pow(kernel::af_env_diagonal(out.base),2);
        out.normals=section_directions(out.base,out.grid.rows,out.grid.columns,s.direction,out.areas);
    }
    if(out.mode==1) out.diffusion=prepare_directions(source,out.grid,cancel);
    return out;
}
InflationPreparation prepare_inflation(std::shared_ptr<Mesh> source,const AfTissueInflation* settings,int count,uint64_t cancel) {
    const kernel::CancelScope scope(cancel); InflationPreparation out; out.source=std::move(source);
    auto grids=material_grids(*out.source);
    if(count<1||grids.size()!=size_t(count)||!settings) throw std::runtime_error("Every accepted material part needs settings.");
    for(int i=0;i<count;++i) out.parts.push_back(prepare_grid(*out.source,std::move(grids[i]),settings[i],cancel));
    check_cancel(cancel); return out;
}
static uint64_t sparse_bytes(const Eigen::SparseMatrix<double>& matrix) {
    return uint64_t(matrix.data().allocatedSize())*(sizeof(double)+sizeof(int))+(matrix.outerSize()+1)*sizeof(int);
}
static uint64_t grid_bytes(const PreparedGrid& p) {
    uint64_t size=(p.base.capacity()+p.normals.capacity())*sizeof(kernel::Vec)+p.areas.capacity()*sizeof(double);
    size+=p.grid.indices.capacity()*sizeof(int64_t)+(p.grid.across.capacity()+p.grid.along.capacity())*sizeof(double);
    if(p.diffusion) size+=p.diffusion->normals.size()*sizeof(double)
        +sparse_bytes(p.diffusion->mass)+sparse_bytes(p.diffusion->stiffness);
    return size;
}
uint64_t preparation_bytes(const InflationPreparation& value) {
    uint64_t size=sizeof(value)+value.parts.capacity()*sizeof(PreparedGrid);
    for(const auto& part:value.parts) size+=grid_bytes(part);
    return size;
}
}
