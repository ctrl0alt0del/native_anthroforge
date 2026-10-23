// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_chart.hpp"
#include "tissue_crop.hpp"
#include "tissue_envelope.hpp"
#include "anthroforge/tissue.h"

namespace af::tissue {
struct CropReference {
    material::Atlas current,reference;
    material::Indices index;
    std::vector<material::Cage> maps;
};
static CropReference charts(const Mesh& reference,const Mesh& current,uint64_t cancel) {
    CropReference result;
    result.current=material::atlas(material_basis(current),cancel);
    result.reference=material::atlas(material_basis(reference),cancel);
    if(result.current.charts.size()!=result.reference.charts.size())
        throw std::runtime_error("Crop material topology changed; explicitly redefine the cut.");
    for(size_t i=0;i<result.current.charts.size();++i)
        if(result.current.charts[i].closed_u!=result.reference.charts[i].closed_u||result.current.charts[i].closed_v!=result.reference.charts[i].closed_v)
            throw std::runtime_error("Crop material closure changed; explicitly redefine the cut.");
    result.index=material::indexed(reference,result.reference,cancel);
    result.maps=material::cages(result.current,result.reference,cancel); return result;
}
static V3 mapped(const Mesh& reference,const CropReference& charts,const material::Triangle& triangle,int corner,uint64_t cancel) {
    V3 weights=V3::Zero(); weights[corner]=1;
    const auto coordinate=material::transported(charts.maps.at(size_t(triangle.chart)),triangle.coordinates,weights,cancel);
    const auto location=material::locate(charts.index,charts.reference,triangle.chart,coordinate.point,coordinate.tangents,cancel);
    if(location.triangle<0) throw std::runtime_error("Crop material location no longer exists; explicitly redefine the cut.");
    V3 output=V3::Zero();
    for(int i=0;i<3;++i) output+=location.weights[i]*V3(reference.vertices.row(reference.triangles(location.triangle,i)));
    return output;
}
static Vertices resampled(const Mesh& reference,const Mesh& current,uint64_t cancel) {
    const auto map=charts(reference,current,cancel); auto output=current.vertices;
    std::vector<bool> visited(size_t(output.rows()),false);
    for(int i=0;i<current.triangles.rows();++i) {
        check_cancel(cancel); const auto ids=current.triangles.row(i);
        const auto triangle=material::coordinates(current,map.current,ids);
        for(int j=0;j<3;++j) if(!visited[size_t(ids[j])]) {
            output.row(ids[j])=mapped(reference,map,triangle,j,cancel); visited[size_t(ids[j])]=true;
        }
    }
    if(std::find(visited.begin(),visited.end(),false)!=visited.end())
        throw std::runtime_error("Crop base has unused material vertices.");
    return output;
}
static std::shared_ptr<Mesh> retained_base(const Mesh& reference,const Mesh& current,uint64_t cancel) {
    const auto a=material_basis(reference),b=material_basis(current);
    if(reference.vertices.rows()==current.vertices.rows()&&reference.corners==current.corners&&reference.offsets==current.offsets&&same_basis(a,b))
        return deform_mesh(current,reference.vertices,cancel,false);
    if(!a.count||!b.count) throw std::runtime_error("Crop sampling changed without material correspondence; explicitly redefine the cut.");
    return deform_mesh(current,resampled(reference,current,cancel),cancel,false);
}
}
uint64_t af_tissue_crop_retained(uint64_t reference,uint64_t base,uint64_t own,const double* plane,uint64_t cancel) {
    try {
        af::check_cancel(cancel);
        const auto material=af::tissue::retained_base(*af::mesh(reference),*af::mesh(base),cancel);
        return af::retain(af::tissue::crop_material(*material,*af::mesh(own),plane,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
