#include "construction_internal.hpp"
#include <set>

namespace af {
static void validate_triangle(const Mesh& source,int index) {
    const auto polygon=source.polygons[index];
    if(polygon<0||polygon+1>=int64_t(source.offsets.size()))
        throw std::runtime_error("Invalid triangle polygon reference.");
    const auto first=source.corners.begin()+source.offsets[polygon];
    const auto last=source.corners.begin()+source.offsets[polygon+1];
    for(int axis=0;axis<3;++axis)
        if(std::find(first,last,source.triangles(index,axis))==last)
            throw std::runtime_error("Triangle does not belong to its canonical polygon.");
}
static void validate_topology(const Mesh& source) {
    if(source.vertices.rows()==0||!source.vertices.allFinite()||source.triangles.rows()==0)
        throw std::runtime_error("Invalid saved geometry.");
    for(size_t i=1;i<source.offsets.size();++i) {
        if(source.offsets[i]-source.offsets[i-1]<3) throw std::runtime_error("Invalid polygon offsets.");
        std::set<int64_t> indices;
        for(auto j=source.offsets[i-1];j<source.offsets[i];++j)
            if(source.corners[j]<0||source.corners[j]>=source.vertices.rows()||!indices.insert(source.corners[j]).second)
                throw std::runtime_error("Invalid polygon corner.");
    }
    for(int i=0;i<source.triangles.rows();++i) validate_triangle(source,i);
}
static std::shared_ptr<Mesh> restore(const double* vertices,int64_t count,const int64_t* corners,
    const int64_t* offsets,int64_t faces,const int32_t* triangles,const int64_t* polygons,int64_t triangle_count) {
    if(count<1||faces<1||triangle_count<1||offsets[0]!=0||offsets[faces]<0)
        throw std::runtime_error("Invalid saved mesh dimensions.");
    auto result=std::make_shared<Mesh>(); result->generated=true;
    result->vertices=Eigen::Map<const Vertices>(vertices,count,3);
    result->triangles=Eigen::Map<const Triangles>(triangles,triangle_count,3);
    result->corners.assign(corners,corners+offsets[faces]);
    result->offsets.assign(offsets,offsets+faces+1);
    result->polygons.assign(polygons,polygons+triangle_count);
    validate_topology(*result); rebuild_mesh(*result,0);
    return result;
}
}
uint64_t af_mesh_restore(const double* vertices,int64_t count,const int64_t* corners,
    const int64_t* offsets,int64_t faces,const int32_t* triangles,const int64_t* polygons,int64_t triangle_count) {
    try { return af::retain(af::restore(vertices,count,corners,offsets,faces,triangles,polygons,triangle_count)); }
    catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
uint64_t af_mesh_reuse_topology(uint64_t source,uint64_t previous,uint64_t cancel) {
    try {
        auto current=af::mesh(source); const auto old=af::mesh(previous);
        if(current->vertices.rows()==old->vertices.rows()&&current->corners==old->corners&&current->offsets==old->offsets) {
            auto updated=af::deform_mesh(*old,current->vertices,cancel);
            updated->material=current->material; updated->tissue=current->tissue; current=std::move(updated);
        }
        return af::retain(current);
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
uint64_t af_mesh_draft(uint64_t source,uint64_t cancel) {
    try {
        const auto mesh=af::mesh(source);
        return af::retain(af::deform_mesh(*mesh,mesh->vertices,cancel,false));
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
uint64_t af_mesh_finalize(uint64_t source,uint64_t previous,uint64_t cancel) {
    try {
        af::check_cancel(cancel); const auto mesh=af::mesh(source);
        auto topology=previous?af::mesh(previous):mesh;
        if(mesh->vertices.rows()!=topology->vertices.rows()||mesh->corners!=topology->corners||mesh->offsets!=topology->offsets)
            topology=mesh;
        if(mesh->prepared&&mesh->triangles.rows()==topology->triangles.rows()&&mesh->triangles==topology->triangles&&mesh->polygons==topology->polygons)
            return af::retain(mesh);
        auto result=af::deform_mesh(*topology,mesh->vertices,cancel);
        result->material=mesh->material;
        result->tissue=mesh->tissue;
        return af::retain(result);
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
uint64_t af_mesh_storage_bytes(uint64_t source) {
    try {
        const auto mesh=af::mesh(source);
        if(mesh->prepared) throw std::runtime_error("Storage accounting requires a geometry-only draft.");
        return sizeof(af::Mesh)+mesh->vertices.size()*sizeof(double)+mesh->triangles.size()*sizeof(int)
            +(mesh->corners.capacity()+mesh->offsets.capacity()+mesh->polygons.capacity()+mesh->material.capacity())*sizeof(int64_t)
            +af::tissue_storage(mesh->tissue);
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
