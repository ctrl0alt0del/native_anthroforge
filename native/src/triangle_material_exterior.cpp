// SPDX-License-Identifier: GPL-3.0-or-later
#include "triangle_material_exterior.hpp"
#include <Eigen/LU>

namespace af::triangle_material {
static M3 source_points(const Mesh& mesh,int64_t origin) {
    const auto& material=mesh.triangle_material;
    if(!material.layer_size) throw std::runtime_error("Reevaluate this Boolean primitive to restore its exterior construction chart.");
    M3 result;
    for(int i=0;i<3;++i) result.row(i)=V3(material.source_positions.data()+9*origin+3*i);
    return result;
}
static M3 construction_triangle(const Mesh& mesh,int triangle) {
    return coordinates(mesh,triangle)*source_points(mesh,mesh.triangle_material.origins[size_t(triangle)]);
}
static void append(ExteriorLayer& layer,const Mesh& mesh,int triangle,int output) {
    const M3 points=construction_triangle(mesh,triangle);
    layer.vertices.middleRows(3*output,3)=points;
    layer.triangles.row(output)=Eigen::Vector3i(3*output,3*output+1,3*output+2);
}
static std::unique_ptr<ExteriorLayer> build(const Mesh& mesh,int64_t group,uint64_t cancel) {
    auto output=std::make_unique<ExteriorLayer>(); const auto& m=mesh.triangle_material;
    for(int i=0;i<mesh.triangles.rows();++i) {
        check_cancel(cancel);
        if(m.origins[size_t(i)]/m.layer_size==group) output->identities.push_back(i);
    }
    const auto count=int(output->identities.size()); output->vertices.resize(3*count,3); output->triangles.resize(count,3);
    for(int i=0;i<count;++i) { check_cancel(cancel); append(*output,mesh,output->identities[size_t(i)],i); }
    if(!count) throw std::runtime_error("The retained Boolean layer has no exterior surface.");
    output->tree.init(output->vertices,output->triangles); return output;
}
static material::Location nearest_location(const Mesh& mesh,ExteriorLayers& layers,int64_t origin,const V3& point,uint64_t cancel) {
    const auto group=origin/mesh.triangle_material.layer_size;
    auto& layer=layers[group]; if(!layer) layer=build(mesh,group,cancel);
    int triangle=-1; Eigen::RowVector3d nearest;
    layer->tree.squared_distance(layer->vertices,layer->triangles,point.transpose(),triangle,nearest);
    check_cancel(cancel);
    if(triangle<0) throw std::runtime_error("No usable exterior for the retained Boolean attachment.");
    const int identity=layer->identities.at(size_t(triangle)); const M3 points=construction_triangle(mesh,identity);
    return {identity,barycentric(nearest.transpose(),points.row(0),points.row(1),points.row(2)),coordinates(mesh,identity)};
}
static material::Tangents edges(const M3& points) {
    material::Tangents result; result.col(0)=points.row(1)-points.row(0); result.col(1)=points.row(2)-points.row(0); return result;
}
static material::Tangents transported(const M3& source,const material::Tangents& directions,const M3& target,const M3& coords) {
    const material::Tangents a=source.transpose()*directions,b=edges(target);
    const V3 first=a.col(0).cross(a.col(1)),second=b.col(0).cross(b.col(1));
    if(first.norm()<1e-15||second.norm()<1e-15) throw std::runtime_error("Degenerate retained Boolean material frame.");
    const auto rotation=Eigen::Quaterniond::FromTwoVectors(first,second);
    const Eigen::Matrix2d coefficients=(b.transpose()*b).fullPivLu().solve(b.transpose()*rotation.toRotationMatrix()*a);
    return edges(coords)*coefficients;
}
M4 exterior_frame(const Mesh& mesh,ExteriorLayers& layers,int64_t origin,const V3& query,
    const material::Tangents& directions,const M4& world,const double* record,uint64_t cancel) {
    const M3 source=source_points(mesh,origin);
    const auto location=nearest_location(mesh,layers,origin,source.transpose()*query,cancel);
    const auto tangents=transported(source,directions,construction_triangle(mesh,location.triangle),location.coordinates);
    return material::frame(mesh,location,tangents,world,record);
}
}
