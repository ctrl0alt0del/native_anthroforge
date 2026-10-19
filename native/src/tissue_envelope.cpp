// SPDX-License-Identifier: GPL-3.0-or-later
// Port of af_muscle_envelope_compose.hpp, retaining exact source/part/side provenance.
#include "tissue_shapes.hpp"
#include "material_domain.hpp"
#include <numeric>

namespace af::tissue {
struct Envelope { Points points; Faces faces; std::vector<int64_t> origins,sides,parts,sources; };
static bool equal(const Mesh& a,const Mesh& b,int64_t i) { return (a.vertices.row(i).array()==b.vertices.row(i).array()).all(); }
static std::vector<bool> boundary(const Mesh& source,uint64_t cancel) {
    std::vector<bool> result(size_t(source.vertices.rows()),false);
    for(const auto& edge:mesh_edges(mesh_faces(source),cancel)) if(edge.second.count==1)
        result[size_t(edge.first.first)]=result[size_t(edge.first.second)]=true;
    return result;
}
static std::vector<int64_t> vertices(Envelope& output,const Mesh& a,const Mesh& b,uint64_t cancel) {
    const auto edge=boundary(a,cancel); const int64_t count=a.vertices.rows(); std::vector<int64_t> mapping;
    for(int64_t i=0;i<count;++i) {
        output.points.push_back(a.vertices.row(i)); output.origins.push_back(i);
        output.sides.push_back(edge[size_t(i)]&&equal(a,b,i)?0:1);
    }
    for(int64_t i=0;i<count;++i) {
        check_cancel(cancel);
        if(edge[size_t(i)]&&equal(a,b,i)) { mapping.push_back(i); continue; }
        mapping.push_back(int64_t(output.points.size())); output.points.push_back(b.vertices.row(i));
        output.origins.push_back(i); output.sides.push_back(2);
    }
    return mapping;
}
static void append(Envelope& output,std::vector<int64_t> face,int64_t part,int64_t source,bool flip) {
    if(flip) std::reverse(face.begin(),face.end());
    output.faces.push_back(std::move(face)); output.parts.push_back(part); output.sources.push_back(source);
}
static void faces(Envelope& output,const Mesh& a,const Mesh& b,const std::vector<int64_t>& mapping,bool flip,uint64_t cancel) {
    const auto polygons=mesh_faces(a);
    for(size_t i=0;i<polygons.size();++i) {
        check_cancel(cancel); const auto part=a.tissue.parts[i]; const auto& face=polygons[i];
        append(output,face,part,int64_t(i),flip);
        if(std::all_of(face.begin(),face.end(),[&](int64_t v){return equal(a,b,v);})) continue;
        std::vector<int64_t> second; for(auto v:face) second.push_back(mapping[size_t(v)]);
        append(output,std::move(second),part,int64_t(i),!flip);
    }
}
static Envelope compact(const Envelope& source) {
    std::vector<int64_t> mapping(source.points.size(),-1); Envelope result; result.faces=source.faces;
    for(const auto& face:source.faces) for(auto index:face) mapping[size_t(index)]=0;
    for(size_t i=0;i<mapping.size();++i) if(mapping[i]==0) {
        mapping[i]=int64_t(result.points.size()); result.points.push_back(source.points[i]);
        result.origins.push_back(source.origins[i]); result.sides.push_back(source.sides[i]);
    }
    for(auto& face:result.faces) for(auto& index:face) index=mapping[size_t(index)];
    result.parts=source.parts; result.sources=source.sources; return result;
}
static TissueDomain correspondence(const Envelope& source,int64_t base_count) {
    TissueDomain d; d.kind=5; d.source_count=base_count;
    d.offsets.resize(source.points.size()+1); std::iota(d.offsets.begin(),d.offsets.end(),0);
    d.weights.resize(source.points.size(),1); d.indices=source.origins; d.sides=source.sides;
    d.parts=source.parts; d.faces=source.sources; return d;
}
static void validate(const Mesh& a,const Mesh& b) {
    if(a.tissue.kind!=4||b.tissue.kind!=4||a.vertices.rows()!=b.vertices.rows()||a.corners!=b.corners||a.offsets!=b.offsets)
        throw std::runtime_error("Two-sided inflation requires matching muscle material domains.");
    for(const auto& grid:material_grids(a)) if(grid.closed_u||grid.closed_v)
        throw std::runtime_error("Two-sided tissue requires open material axes.");
}
static std::shared_ptr<Mesh> compose(const Mesh& a,const Mesh& b,bool flip,uint64_t cancel) {
    validate(a,b); Envelope output;
    const auto mapping=vertices(output,a,b,cancel); faces(output,a,b,mapping,flip,cancel);
    const auto reduced=compact(output); auto mesh=make_mesh(reduced.points,reduced.faces,cancel,true);
    mesh->tissue=correspondence(reduced,a.vertices.rows());
    tissue_validate(mesh->tissue,mesh->vertices.rows(),int64_t(mesh->offsets.size())-1); return mesh;
}
}
uint64_t af_tissue_envelope(uint64_t first,uint64_t second,int reverse,uint64_t cancel) {
    try { return af::retain(af::tissue::compose(*af::mesh(first),*af::mesh(second),reverse!=0,cancel)); }
    catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
