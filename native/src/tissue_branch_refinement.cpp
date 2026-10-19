// SPDX-License-Identifier: GPL-3.0-or-later
// Refine accepted bilinear parts while sharing every seam sample by material identity.
#include "tissue_refinement.hpp"
#include <numeric>

namespace af::tissue {
struct Refined { Points points; Faces faces; std::vector<int64_t> material; std::vector<double> axes,across,along; };
static std::vector<double> main_stations(const MaterialGrid& main,const std::vector<MaterialGrid>& grids,const std::vector<Connection>& seams,int resolution) {
    auto values=main.along;
    for(size_t i=0;i<seams.size();++i) {
        const double first=main.along[size_t(seams[i].seam.front())],last=main.along[size_t(seams[i].seam.back())];
        for(double x:refine_axis(grids[i+1].across,resolution,false)) values.push_back(first+x*(last-first));
    }
    return refine_axis(values,resolution,false);
}
static void append(Refined& out,const std::vector<uint32_t>& indices,const std::vector<double>& across,const std::vector<double>& along,bool flip) {
    const auto faces=grid_faces(int(across.size()),int(along.size()),false,false);
    for(auto face:faces) {
        for(auto& i:face) i=indices[size_t(i)];
        if(flip) std::reverse(face.begin(),face.end());
        out.faces.push_back(std::move(face));
    }
    append_material_grid(out.material,indices,across.size(),along.size());
    out.axes.insert(out.axes.end(),across.begin(),across.end()); out.axes.insert(out.axes.end(),along.begin(),along.end());
}
static Refined main_grid(const Mesh& source,const std::vector<MaterialGrid>& grids,const std::vector<Connection>& seams,int resolution,uint64_t cancel) {
    Refined result; result.across=refine_axis(grids[0].across,resolution,false);
    result.along=main_stations(grids[0],grids,seams,resolution);
    if(result.across.size()*result.along.size()>262144) throw std::runtime_error("Tissue material refinement exceeds the vertex budget.");
    for(double i:result.across) for(double j:result.along) { check_cancel(cancel); result.points.push_back(material_sample(source,grids[0],i,j)); }
    std::vector<uint32_t> indices(result.points.size()); std::iota(indices.begin(),indices.end(),0);
    append(result,indices,result.across,result.along,grid_reversed(source,grids[0])); return result;
}
static std::pair<size_t,size_t> interval(const Refined& output,const MaterialGrid& main,const Connection& seam) {
    const double first=main.along[size_t(seam.seam.front())],last=main.along[size_t(seam.seam.back())];
    const auto a=std::lower_bound(output.along.begin(),output.along.end(),first-1e-12);
    const auto b=std::upper_bound(a,output.along.end(),last+1e-12);
    return {size_t(a-output.along.begin()),size_t(b-output.along.begin())};
}
static std::vector<double> across_axis(const Refined& out,size_t first,size_t end) {
    std::vector<double> values; const double a=out.along[first],b=out.along[end-1];
    for(size_t i=first;i<end;++i) values.push_back((out.along[i]-a)/(b-a));
    return values;
}
static void append_vertices(Refined& out,const Mesh& source,const MaterialGrid& grid,const Connection& seam,size_t first,const std::vector<double>& across,const std::vector<double>& along,std::vector<uint32_t>& indices,uint64_t cancel) {
    const size_t boundary=seam.boundary==0?0:out.across.size()-1;
    if(out.points.size()+across.size()*(along.size()-1)>262144) throw std::runtime_error("Tissue material refinement exceeds the vertex budget.");
    for(size_t i=0;i<across.size();++i) {
        indices.push_back(uint32_t(boundary*out.along.size()+first+i));
        for(size_t j=1;j<along.size();++j) {
            check_cancel(cancel); indices.push_back(uint32_t(out.points.size()));
            out.points.push_back(material_sample(source,grid,across[i],along[j]));
        }
    }
}
static void branch(Refined& out,const Mesh& source,const std::vector<MaterialGrid>& grids,size_t index,const Connection& seam,int resolution,uint64_t cancel) {
    const auto [first,end]=interval(out,grids[0],seam); const auto& grid=grids[index];
    const auto across=across_axis(out,first,end),along=refine_axis(grid.along,resolution,false);
    std::vector<uint32_t> indices; append_vertices(out,source,grid,seam,first,across,along,indices,cancel);
    append(out,indices,across,along,grid_reversed(source,grid));
}
std::shared_ptr<Mesh> refine_parts(const Mesh& source,const std::vector<MaterialGrid>& grids,int resolution,uint64_t cancel) {
    std::vector<double> parameters(grids.size()*2,.25); const auto seams=connections(grids,parameters.data());
    auto output=main_grid(source,grids,seams,resolution,cancel);
    for(size_t i=1;i<grids.size();++i) branch(output,source,grids,i,seams[i-1],resolution,cancel);
    auto result=make_mesh(output.points,output.faces,cancel,true);
    result->material=std::move(output.material); result->material_axes=std::move(output.axes); return result;
}
}
