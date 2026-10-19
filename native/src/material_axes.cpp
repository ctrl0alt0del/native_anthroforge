// SPDX-License-Identifier: GPL-3.0-or-later
// Accepted parameter axes are material metadata, independent of deformed edge lengths.
#include "material_domain.hpp"

namespace af {
static std::vector<double> axis(const std::vector<double>& values,size_t& cursor,int count,bool closed) {
    std::vector<double> result(size_t(count),0);
    if(values.empty()) for(int i=0;i<count;++i) result[size_t(i)]=double(i)/(count-int(!closed));
    else {
        if(cursor+size_t(count)>values.size()) throw std::runtime_error("Incomplete material parameter axes.");
        std::copy_n(values.data()+cursor,count,result.data()); cursor+=size_t(count);
    }
    for(size_t i=0;i<result.size();++i)
        if(!std::isfinite(result[i])||result[i]<0||result[i]>1||(i&&result[i]<=result[i-1]))
            throw std::runtime_error("Invalid material parameter order.");
    return result;
}
std::vector<MaterialGrid> material_grids(const Mesh& mesh) {
    auto grids=material_grids(mesh.material,mesh.vertices.rows()); size_t cursor=0;
    for(auto& grid:grids) {
        grid.across=axis(mesh.material_axes,cursor,grid.rows,grid.closed_v);
        grid.along=axis(mesh.material_axes,cursor,grid.columns,grid.closed_u);
    }
    if(cursor!=mesh.material_axes.size()) throw std::runtime_error("Unexpected material parameters.");
    return grids;
}
}
int64_t af_mesh_material_axes(uint64_t source,double* data,int64_t count) {
    try {
        const auto mesh=af::mesh(source); const auto size=int64_t(mesh->material_axes.size());
        if(!data&&count==0) return size;
        if(count!=size||!data) throw std::runtime_error("Invalid material parameter buffer.");
        std::copy(mesh->material_axes.begin(),mesh->material_axes.end(),data); return size;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
