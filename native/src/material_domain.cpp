// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_domain.hpp"
#include "construction_internal.hpp"
#include <numeric>

namespace af {
std::vector<int64_t> grid_material(int rows,int columns,bool closed_u,bool closed_v) {
    std::vector<int64_t> data{rows,columns,closed_u,closed_v,int64_t(rows)*columns};
    data.resize(size_t(5+int64_t(rows)*columns));
    std::iota(data.begin()+5,data.end(),0);
    return data;
}
void append_material_grid(std::vector<int64_t>& data,const std::vector<uint32_t>& indices,size_t rows,size_t columns) {
    data.insert(data.end(),{int64_t(rows),int64_t(columns),0,0,int64_t(indices.size())});
    data.insert(data.end(),indices.begin(),indices.end());
}
static MaterialGrid read_grid(const std::vector<int64_t>& data,size_t& cursor,int64_t vertices) {
    if(data.size()-cursor<5) throw std::runtime_error("Incomplete material grid header.");
    const auto* p=data.data()+cursor; const int64_t rows=p[0],cols=p[1],count=p[4];
    if(rows<2||cols<2||rows>262144||cols>262144||count!=rows*cols||count>262144)
        throw std::runtime_error("Invalid material grid dimensions.");
    if((p[2]!=0&&p[2]!=1)||(p[3]!=0&&p[3]!=1)||count>int64_t(data.size()-cursor-5))
        throw std::runtime_error("Invalid material grid flags or index count.");
    MaterialGrid grid{int(rows),int(cols),p[2]!=0,p[3]!=0,{p+5,p+5+count},{},{}};
    for(auto index:grid.indices) if(index<0||index>=vertices)
        throw std::runtime_error("Material grid references a missing vertex.");
    cursor+=size_t(count)+5;
    return grid;
}
std::vector<MaterialGrid> material_grids(const std::vector<int64_t>& data,int64_t vertices) {
    std::vector<MaterialGrid> grids; size_t cursor=0;
    while(cursor<data.size()) grids.push_back(read_grid(data,cursor,vertices));
    return grids;
}
}
int64_t af_mesh_material_size(uint64_t source) {
    try { return int64_t(af::mesh(source)->material.size()); }
    catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
int af_mesh_material_copy(uint64_t source,int64_t* data,int64_t count) {
    try {
        const auto mesh=af::mesh(source);
        if(count!=int64_t(mesh->material.size())||(count&&!data)) throw std::runtime_error("Invalid material copy buffer.");
        std::copy(mesh->material.begin(),mesh->material.end(),data);
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
uint64_t af_mesh_with_material(uint64_t source,const int64_t* data,int64_t count,const double* axes,int64_t axis_count,uint64_t cancel) {
    try {
        if(count<0||count>16777216||(count&&!data)) throw std::runtime_error("Invalid material storage.");
        if(axis_count<0||axis_count>16777216||(axis_count&&!axes)) throw std::runtime_error("Invalid material axis storage.");
        const auto mesh=af::mesh(source); std::vector<int64_t> material;
        if(count) material.assign(data,data+count);
        af::material_grids(material,mesh->vertices.rows());
        auto result=af::deform_mesh(*mesh,mesh->vertices,cancel,mesh->prepared);
        result->material=material;
        result->material_axes.assign(axes,axes+axis_count); af::material_grids(*result);
        return af::retain(result);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
