// SPDX-License-Identifier: GPL-3.0-or-later
// Port of prepared_inflation.py: weighted grid geodesics and branch tip-only taper.
#include "tissue_branches.hpp"

namespace af::tissue {
static double smooth(double x) { x=std::clamp(x,0.,1.); return x*x*(3-2*x); }
static Mesh local_grid(const Mesh& source,const MaterialGrid& grid) {
    Mesh result; result.vertices.resize(grid.indices.size(),3);
    for(size_t i=0;i<grid.indices.size();++i) result.vertices.row(i)=source.vertices.row(grid.indices[i]);
    return result;
}
static std::vector<double> boundary_field(const Mesh& local,const MaterialGrid& grid,const std::vector<double>& mask,const AfTissueInflation& s,uint64_t cancel) {
    const auto edges=mesh_edges(grid_faces(grid.rows,grid.columns,false,false),cancel);
    auto field=mask_distances(local,edges,mask,cancel); double length=0;
    for(const auto& edge:edges) length+=(local.vertices.row(edge.first.first)-local.vertices.row(edge.first.second)).norm();
    const double step=std::max(length/double(edges.size()),1e-12),band=step*std::max(.1,s.boundary_band);
    for(size_t i=0;i<field.size();++i)
        field[i]=mask[i]?0:1-s.boundary_strength+s.boundary_strength*std::pow(smooth(field[i]/band),s.boundary_power);
    return field;
}
static std::vector<double> taper(const Mesh& local,const MaterialGrid& grid,double fraction,bool branch,uint64_t cancel) {
    std::vector<double> result(grid.indices.size());
    for(int i=0;i<grid.rows;++i) {
        check_cancel(cancel); const int start=i*grid.columns; std::vector<double> along(size_t(grid.columns),0);
        for(int j=1;j<grid.columns;++j) along[size_t(j)]=along[size_t(j-1)]+(local.vertices.row(start+j)-local.vertices.row(start+j-1)).norm();
        const double end=along.back(),band=std::max(end*fraction,1e-12);
        for(int j=0;j<grid.columns;++j) result[size_t(start+j)]=smooth((branch?end-along[size_t(j)]:std::min(along[size_t(j)],end-along[size_t(j)]))/band);
    }
    return result;
}
InflationWeights prepared_weights(const Mesh& source,const MaterialGrid& grid,const std::vector<bool>& fixed,const AfTissueInflation& settings,bool branch,uint64_t cancel) {
    const auto local=local_grid(source,grid); std::vector<double> mask;
    for(auto index:grid.indices) mask.push_back(fixed[size_t(index)]?1:0);
    return {boundary_field(local,grid,mask,settings,cancel),taper(local,grid,settings.taper,branch,cancel)};
}
}
