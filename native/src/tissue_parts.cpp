// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_branches.hpp"
#include "mesh_quality.hpp"
#include <unordered_map>

namespace af::tissue {
bool grid_reversed(const Mesh& source,const MaterialGrid& grid) {
    const auto a=grid.indices[0],b=grid.indices[size_t(grid.columns)];
    for(const auto& face:mesh_faces(source)) {
        if(std::find(face.begin(),face.end(),grid.indices[1])==face.end()||std::find(face.begin(),face.end(),grid.indices[size_t(grid.columns+1)])==face.end()) continue;
        for(size_t i=0;i<face.size();++i) {
        const auto first=face[i],second=face[(i+1)%face.size()];
        if(first==a&&second==b) return false;
        if(first==b&&second==a) return true;
        }
    }
    throw std::runtime_error("Material grid orientation does not resolve to canonical faces.");
}
static std::vector<bool> exterior(const Mesh& source,uint64_t cancel) {
    std::vector<bool> result(size_t(source.vertices.rows()),false);
    for(const auto& edge:mesh_edges(mesh_faces(source),cancel)) if(edge.second.count==1)
        result[size_t(edge.first.first)]=result[size_t(edge.first.second)]=true;
    return result;
}
static std::vector<Points> evaluate_parts(const Mesh& source,const std::vector<MaterialGrid>& grids,const AfTissueInflation* settings,uint64_t cancel) {
    const auto fixed=exterior(source,cancel); std::vector<Points> values;
    for(size_t i=0;i<grids.size();++i) {
        auto config=settings[i]; config.reverse=(config.reverse!=0)!=grid_reversed(source,grids[i]);
        if(grids.size()>1&&config.mode==2) throw std::runtime_error("Section Profile requires an ordinary open loft.");
        const auto weights=grids.size()>1?prepared_weights(source,grids[i],fixed,config,i>0,cancel):InflationWeights{};
        values.push_back(inflate_prepared_grid(source,grids[i],config,grids.size()>1?&weights:nullptr,cancel));
    }
    return values;
}
static void labels(TissueDomain& domain,const std::vector<MaterialGrid>& grids) {
    size_t face=0;
    for(size_t part=0;part<grids.size();++part) {
        const auto& grid=grids[part]; const int count=(grid.rows-int(!grid.closed_v))*(grid.columns-int(!grid.closed_u));
        for(int i=0;i<count;++i) {
            if(face>=domain.parts.size()) throw std::runtime_error("Material part faces do not match their surface.");
            domain.parts[face++]=int64_t(part);
        }
    }
    if(face!=domain.parts.size()) throw std::runtime_error("Surface has faces outside its declared material parts.");
}
static std::shared_ptr<Mesh> assemble(const Mesh& source,const std::vector<MaterialGrid>& grids,const std::vector<Points>& values,uint64_t cancel) {
    auto vertices=source.vertices;
    for(size_t part=0;part<grids.size();++part) for(size_t i=0;i<grids[part].indices.size();++i) {
        check_cancel(cancel); vertices.row(grids[part].indices[i])=values[part][i];
    }
    auto result=deform_mesh(source,vertices,cancel,true);
    result->tissue=tissue_identity(4,vertices.rows(),int64_t(source.offsets.size())-1); labels(result->tissue,grids);
    result->basis=material_basis(source);
    return result;
}
static bool inactive(const AfTissueInflation* settings,int count) {
    for(int i=0;i<count;++i) if(settings[i].enabled) {
        const auto& s=settings[i];
        const bool nonzero=s.mode==2?std::any_of(s.profile,s.profile+4,[](double d){return d>0;}):s.amount>0;
        if(nonzero) return false;
    }
    return true;
}
std::shared_ptr<Mesh> inflate_parts(const Mesh& source,const AfTissueInflation* settings,int count,const double* connectors,bool envelope,uint64_t cancel) {
    const auto grids=material_grids(source);
    if(count<1||grids.size()!=size_t(count)||!settings||!connectors) throw std::runtime_error("Every accepted material part needs settings.");
    const auto seams=connections(grids,connectors); auto values=evaluate_parts(source,grids,settings,cancel);
    if(envelope&&inactive(settings,count)) return assemble(source,grids,values,cancel);
    share_displacements(source,grids,seams,values);
    connect_parts(grids,seams,values,(settings[0].reverse!=0)!=grid_reversed(source,grids[0]),cancel);
    auto result=assemble(source,grids,values,cancel);
    quality::validate(source,*result,cancel);
    return result;
}
}
uint64_t af_tissue_inflate_parts(uint64_t source,const AfTissueInflation* settings,int count,const double* connectors,int envelope,uint64_t cancel) {
    try { return af::retain(af::tissue::inflate_parts(*af::mesh(source),settings,count,connectors,envelope!=0,cancel)); }
    catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
