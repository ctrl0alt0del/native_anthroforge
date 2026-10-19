// SPDX-License-Identifier: GPL-3.0-or-later
// Refine the accepted material surface, retaining every original grid line.
#include "tissue_inflation.hpp"

namespace af::tissue {
static std::vector<double> axis(int count,int resolution,bool closed) {
    std::vector<double> values;
    for(int i=0;i<count;++i) values.push_back(double(i)/(count-int(!closed)));
    for(int i=0;i<resolution;++i) values.push_back(double(i)/(resolution-int(!closed)));
    std::sort(values.begin(),values.end());
    values.erase(std::unique(values.begin(),values.end(),[](double a,double b){return std::abs(a-b)<1e-12;}),values.end());
    return values;
}
struct Coordinate { int first,second; double factor; };
static Coordinate cell(double t,int count,bool closed) {
    const double position=t*(count-int(!closed));
    const int first=std::min(int(position),count-1);
    return {first,closed?(first+1)%count:std::min(first+1,count-1),position-first};
}
static V3 sample(const Mesh& mesh,const MaterialGrid& grid,double row,double column) {
    const auto a=cell(row,grid.rows,grid.closed_v),b=cell(column,grid.columns,grid.closed_u);
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
    const auto rows=axis(grid.rows,resolution,grid.closed_v),cols=axis(grid.columns,resolution,grid.closed_u);
    if(rows.size()*cols.size()>262144) throw std::runtime_error("Tissue material refinement exceeds the vertex budget.");
    Points points;
    for(double i:rows) for(double j:cols) { check_cancel(cancel); points.push_back(sample(mesh,grid,i,j)); }
    auto faces=grid_faces(int(rows.size()),int(cols.size()),grid.closed_u,grid.closed_v);
    if(reversed(mesh,grid)) for(auto& face:faces) std::reverse(face.begin()+1,face.end());
    auto result=make_mesh(points,faces,cancel,true);
    result->material=grid_material(int(rows.size()),int(cols.size()),grid.closed_u,grid.closed_v);
    return result;
}
}
uint64_t af_tissue_refine_grid(uint64_t source,int resolution,uint64_t cancel) {
    try {
        if(resolution<3||resolution>256) throw std::runtime_error("Tissue resolution must be 3..256.");
        const auto mesh=af::mesh(source);
        const auto grids=af::material_grids(mesh->material,mesh->vertices.rows());
        if(grids.size()!=1) throw std::runtime_error("Grid refinement requires an ordinary loft.");
        return af::retain(af::tissue::refine(*mesh,grids.front(),resolution,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
