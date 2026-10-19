// SPDX-License-Identifier: GPL-3.0-or-later
// Native port of soft_tissue_surface_inflation.py; source normals/fields are owned here.
#include "tissue_shapes.hpp"

namespace af::tissue {
static std::vector<double> field(const Mesh& mesh,const Edges& edges,const double* values,int64_t count,uint64_t cancel) {
    if(!count) return boundary_weights(mesh,edges,cancel);
    if(!values||count!=mesh.vertices.rows()) throw std::runtime_error("Thickness field must match the accepted base topology.");
    std::vector<double> weights(values,values+count);
    for(double w:weights) if(!std::isfinite(w)||w<0||w>1) throw std::runtime_error("Invalid thickness field weight.");
    return weights;
}
static Points shell_points(const Mesh& mesh,const Vertices& normals,const std::vector<double>& weights,const AfTissueShape& s,uint64_t cancel) {
    Points points; points.reserve(size_t(mesh.vertices.rows()*2));
    for(int64_t i=0;i<mesh.vertices.rows();++i) {
        check_cancel(cancel); const V3 p=mesh.vertices.row(i),n=normals.row(i);
        const double thickness=s.enabled?(s.minimum+(s.amount-s.minimum)*std::pow(weights[size_t(i)],s.power)):0;
        points.push_back(p+n*thickness);
    }
    for(int64_t i=0;i<mesh.vertices.rows();++i) points.push_back(mesh.vertices.row(i));
    return points;
}
static Faces shell_faces(const Faces& source,const Edges& edges,int64_t count) {
    Faces result=source;
    for(auto face:source) {
        std::reverse(face.begin(),face.end());
        for(auto& index:face) index+=count;
        result.push_back(std::move(face));
    }
    for(const auto& face:source) for(size_t i=0;i<face.size();++i) {
        const auto a=face[i],b=face[(i+1)%face.size()];
        if(edges.at(std::minmax(a,b)).count==1) result.push_back({b,a,a+count,b+count});
    }
    return result;
}
std::shared_ptr<Mesh> normal_shell(const Mesh& mesh,const AfTissueShape& settings,const double* weights,int64_t count,uint64_t cancel) {
    auto faces=mesh_faces(mesh);
    if(settings.reverse) for(auto& face:faces) std::reverse(face.begin(),face.end());
    const auto edges=boundary_topology(faces,cancel); const auto normals=surface_normals(mesh,faces,cancel);
    const auto points=shell_points(mesh,normals,field(mesh,edges,weights,count,cancel),settings,cancel);
    const auto polygons=shell_faces(faces,edges,mesh.vertices.rows());
    auto result=make_mesh(points,polygons,cancel,true);
    result->tissue=tissue_identity(3,mesh.vertices.rows(),int64_t(polygons.size()),2);
    for(size_t i=0;i<polygons.size();++i) result->tissue.faces[i]=i<2*faces.size()?int64_t(i%faces.size()):-1;
    tissue_validate(result->tissue,result->vertices.rows(),int64_t(polygons.size()));
    return result;
}
}
