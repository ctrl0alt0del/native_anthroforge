// SPDX-License-Identifier: GPL-3.0-or-later
// Refine the accepted material surface, retaining every original grid line.
#include "tissue_refinement.hpp"

namespace af::tissue {
std::vector<double> refine_axis(const std::vector<double>& source,int resolution,bool closed) {
    std::vector<double> values=source;
    for(int i=0;i<resolution;++i) values.push_back(double(i)/(resolution-int(!closed)));
    std::sort(values.begin(),values.end());
    values.erase(std::unique(values.begin(),values.end(),[](double a,double b){return std::abs(a-b)<1e-12;}),values.end());
    return values;
}
struct Coordinate { int first,second; double factor; };
static Coordinate cell(double t,const std::vector<double>& axis,bool closed) {
    const int count=int(axis.size());
    const int first=std::max(0,int(std::upper_bound(axis.begin(),axis.end(),t)-axis.begin())-1);
    const int second=closed?(first+1)%count:std::min(first+1,count-1);
    const double end=second?axis[size_t(second)]:1;
    return {first,second,first==second?0:(t-axis[size_t(first)])/(end-axis[size_t(first)])};
}
V3 material_sample(const Mesh& mesh,const MaterialGrid& grid,double row,double column) {
    const auto a=cell(row,grid.across,grid.closed_v),b=cell(column,grid.along,grid.closed_u);
    const auto at=[&](int i,int j)->V3 {return mesh.vertices.row(grid.indices[i*grid.columns+j]);};
    const V3 first=(1-b.factor)*at(a.first,b.first)+b.factor*at(a.first,b.second);
    const V3 second=(1-b.factor)*at(a.second,b.first)+b.factor*at(a.second,b.second);
    return (1-a.factor)*first+a.factor*second;
}
static bool reversed(const Mesh& mesh,const MaterialGrid& grid) {
    const V3 a=mesh.vertices.row(grid.indices[0]),b=mesh.vertices.row(grid.indices[grid.columns]),c=mesh.vertices.row(grid.indices[1]);
    const auto triangle=mesh.triangles.row(0);
    const V3 p=mesh.vertices.row(triangle[0]),q=mesh.vertices.row(triangle[1]),r=mesh.vertices.row(triangle[2]);
    return (b-a).cross(c-a).dot((q-p).cross(r-p))<0;
}
static std::shared_ptr<Mesh> refine(const Mesh& mesh,const MaterialGrid& grid,int resolution,uint64_t cancel) {
    const auto rows=refine_axis(grid.across,resolution,grid.closed_v),cols=refine_axis(grid.along,resolution,grid.closed_u);
    if(rows.size()*cols.size()>262144) throw std::runtime_error("Tissue material refinement exceeds the vertex budget.");
    Points points;
    for(double i:rows) for(double j:cols) { check_cancel(cancel); points.push_back(material_sample(mesh,grid,i,j)); }
    auto faces=grid_faces(int(rows.size()),int(cols.size()),grid.closed_u,grid.closed_v);
    if(reversed(mesh,grid)) for(auto& face:faces) std::reverse(face.begin()+1,face.end());
    auto result=make_mesh(points,faces,cancel,true);
    result->material=grid_material(int(rows.size()),int(cols.size()),grid.closed_u,grid.closed_v);
    result->material_axes=rows; result->material_axes.insert(result->material_axes.end(),cols.begin(),cols.end());
    return result;
}
}
uint64_t af_tissue_refine_grid(uint64_t source,int resolution,uint64_t cancel) {
    try {
        if(resolution<3||resolution>256) throw std::runtime_error("Tissue resolution must be 3..256.");
        const auto mesh=af::mesh(source);
        const auto grids=af::material_grids(*mesh);
        if(grids.empty()) throw std::runtime_error("Grid refinement requires a material loft.");
        if(grids.size()>1) return af::retain(af::tissue::refine_parts(*mesh,grids,resolution,cancel));
        return af::retain(af::tissue::refine(*mesh,grids.front(),resolution,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
