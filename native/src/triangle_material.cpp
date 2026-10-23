// SPDX-License-Identifier: GPL-3.0-or-later
#include "construction_internal.hpp"
#include "anthroforge/attachments.h"

namespace af {
static void refined_triangle(const Mesh& source,Mesh& output,int original,int triangle) {
    const auto parent=source.triangles.row(original); auto& material=output.triangle_material;
    material.origins.push_back(source.triangle_material.origins[size_t(original)]);
    for(int j=0;j<3;++j) {
        const V3 point=output.vertices.row(output.triangles(triangle,j));
        const V3 weights=barycentric(point,source.vertices.row(parent[0]),source.vertices.row(parent[1]),source.vertices.row(parent[2]));
        V3 coordinate=V3::Zero();
        for(int k=0;k<3;++k) coordinate+=weights[k]*V3(source.triangle_material.coordinates.data()+9*original+3*k);
        material.coordinates.insert(material.coordinates.end(),coordinate.data(),coordinate.data()+3);
    }
}
void refine_triangle_material(const Mesh& source,Mesh& output,const std::vector<int>& parents,uint64_t cancel) {
    if(!source.triangle_material.source_count) return;
    std::vector<int> triangles(source.offsets.size()-1,-1);
    for(int i=0;i<source.triangles.rows();++i) triangles[size_t(source.polygons[size_t(i)])]=i;
    output.triangle_material.source_count=source.triangle_material.source_count;
    output.triangle_material.layer_size=source.triangle_material.layer_size;
    output.triangle_material.source_positions=source.triangle_material.source_positions;
    for(int i=0;i<output.triangles.rows();++i) {
        check_cancel(cancel); const auto parent=parents.at(size_t(output.polygons[size_t(i)]));
        refined_triangle(source,output,triangles.at(size_t(parent)),i);
    }
    validate_triangle_material(output.triangle_material,output.triangles.rows());
}
uint64_t triangle_material_storage(const TriangleMaterial& m) {
    return m.origins.capacity()*sizeof(int64_t)+(m.coordinates.capacity()+m.source_positions.capacity())*sizeof(double);
}
void validate_triangle_material(const TriangleMaterial& m,int64_t triangles) {
    validate_triangle_source(m);
    if(m.source_count<0||m.source_count>10000000) throw std::runtime_error("Invalid source triangle count.");
    if(!m.source_count&&m.origins.empty()&&m.coordinates.empty()) return;
    if(int64_t(m.origins.size())!=triangles||m.coordinates.size()!=m.origins.size()*9)
        throw std::runtime_error("Triangle provenance does not match geometry.");
    for(auto origin:m.origins) if(origin<0||origin>=m.source_count) throw std::runtime_error("Invalid source triangle identity.");
    for(size_t i=0;i<m.coordinates.size();i+=3) {
        const V3 p(m.coordinates.data()+i);
        if(!p.allFinite()||p.minCoeff()<-1e-6||std::abs(p.sum()-1)>1e-6)
            throw std::runtime_error("Invalid source triangle coordinates.");
    }
}
}
int af_mesh_triangle_material_sizes(uint64_t source,int64_t* sizes) {
    try {
        if(!sizes) throw std::runtime_error("Missing triangle material sizes.");
        const auto m=af::mesh(source); const auto& p=m->triangle_material;
        sizes[0]=p.source_count?1+int64_t(p.origins.size()):0; sizes[1]=int64_t(p.coordinates.size()); return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
int af_mesh_triangle_material_copy(uint64_t source,int64_t* records,int64_t count,double* coordinates,int64_t size) {
    try {
        const auto m=af::mesh(source); const auto& p=m->triangle_material;
        if(count!=(p.source_count?1+int64_t(p.origins.size()):0)||size!=int64_t(p.coordinates.size())||(count&&!records)||(size&&!coordinates))
            throw std::runtime_error("Invalid triangle material buffers.");
        if(count) { records[0]=p.source_count; std::copy(p.origins.begin(),p.origins.end(),records+1); }
        std::copy(p.coordinates.begin(),p.coordinates.end(),coordinates); return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
uint64_t af_mesh_triangle_material_restore(uint64_t source,const int64_t* records,int64_t count,const double* coordinates,int64_t size,uint64_t cancel) {
    try {
        if(count<1||count>10000001||size!=9*(count-1)||!records||(size&&!coordinates)) throw std::runtime_error("Invalid triangle material storage.");
        const auto m=af::mesh(source);
        af::TriangleMaterial p{records[0],{records+1,records+count},{coordinates,coordinates+size},0,{}};
        af::validate_triangle_material(p,m->triangles.rows());
        auto result=af::deform_mesh(*m,m->vertices,cancel,m->prepared);
        result->triangle_material=std::move(p); return af::retain(result);
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
