#include "mesh_internal.hpp"

namespace af {
static bool same_geometry(const Mesh& a,const Mesh& b,uint64_t cancel) {
    if(a.vertices.rows()!=b.vertices.rows()||a.triangles.rows()!=b.triangles.rows()) return false;
    for(int64_t i=0;i<a.vertices.rows();++i) {
        check_cancel(cancel); if(a.vertices.row(i)!=b.vertices.row(i)) return false;
    }
    return a.triangles==b.triangles&&a.corners==b.corners&&a.offsets==b.offsets&&a.polygons==b.polygons;
}
static bool same_material(const Mesh& a,const Mesh& b) {
    return a.material==b.material&&a.material_axes==b.material_axes&&a.material_pins==b.material_pins
        &&a.triangle_material.source_count==b.triangle_material.source_count
        &&a.triangle_material.origins==b.triangle_material.origins&&a.triangle_material.coordinates==b.triangle_material.coordinates
        &&a.triangle_material.layer_size==b.triangle_material.layer_size&&a.triangle_material.source_positions==b.triangle_material.source_positions
        &&tissue_records(a.tissue)==tissue_records(b.tissue)&&a.tissue.weights==b.tissue.weights&&same_basis(a.basis,b.basis);
}
}
int af_mesh_same_content(uint64_t first,uint64_t second,uint64_t cancel) {
    try {
        af::check_cancel(cancel); const auto a=af::mesh(first),b=af::mesh(second);
        return a==b||(af::same_geometry(*a,*b,cancel)&&af::same_material(*a,*b));
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
