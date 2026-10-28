#include "skin_reconstruction.hpp"
#include "skin_assembly.hpp"
#include "anthroforge/skin_gaps.h"

namespace af::skin {
static std::shared_ptr<Mesh> extract(Tiles& tiles,uint64_t cancel) {
    Assembly assembly; assembly.cancel=cancel;
    std::vector<float> values(kernel::af_skin::SKIN_SAMPLES); std::array<int,3> start{};
    for(int i=0;i<int(tiles.surface_tiles.size());++i) {
        check_cancel(cancel); kernel::af_skin::copy_skin_tile(tiles,i,0,start.data(),values.data());
        append(assembly,extract_tile(values.data(),{33,33,33},cancel),start);
    }
    const auto& o=tiles.grid.origin;
    return assemble(assembly,V3(o.x,o.y,o.z),tiles.grid.h);
}
static std::shared_ptr<Mesh> supported(const Scene& scene,const Mesh& mesh,double* diagnostics,uint64_t cancel) {
    std::vector<uint8_t> keep(mesh.vertices.rows()); int stats[3]{};
    kernel::af_skin::keep_supported_components(scene,mesh.vertices.data(),int(mesh.vertices.rows()),
        mesh.corners.data(),int(mesh.corners.size()/3),keep.data(),stats);
    diagnostics[18]=stats[1];
    Points points; std::vector<int64_t> remap(keep.size(),-1); Faces faces;
    for(size_t i=0;i<keep.size();++i) if(keep[i]) { remap[i]=int64_t(points.size()); points.push_back(mesh.vertices.row(i)); }
    for(size_t i=0;i<mesh.corners.size();i+=3) if(keep[mesh.corners[i]])
        faces.push_back({remap[mesh.corners[i]],remap[mesh.corners[i+1]],remap[mesh.corners[i+2]]});
    if(faces.empty()) throw std::runtime_error("Skin has no supported surface components.");
    return make_mesh(points,faces,cancel,false);
}
static void orient(Mesh& mesh) {
    double volume=0;
    for(size_t i=0;i<mesh.corners.size();i+=3) {
        const V3 a=mesh.vertices.row(mesh.corners[i]),b=mesh.vertices.row(mesh.corners[i+1]),c=mesh.vertices.row(mesh.corners[i+2]);
        volume+=a.dot(b.cross(c));
    }
    if(volume<0) for(size_t i=0;i<mesh.corners.size();i+=3) {
        std::swap(mesh.corners[i],mesh.corners[i+2]); mesh.triangles.row(i/3).reverseInPlace();
    }
}
std::shared_ptr<Mesh> extract_envelope(Tiles& tiles,double* diagnostics,uint64_t cancel) {
    auto raw=extract(tiles,cancel); auto result=supported(*tiles.scene,*raw,diagnostics,cancel);
    raw.reset();
    check_cancel(cancel);
    kernel::af_skin::finish_skin_tiles(tiles,result->vertices.data(),int(result->vertices.rows()),
        result->corners.data(),int(result->corners.size()/3),8);
    // Match addon finish(): only geometry, source queries and gap constraints survive.
    kernel::af_skin_tiles_release_field(&tiles);
    result->vertices=result->vertices.cast<float>().cast<double>(); orient(*result);
    diagnose(tiles,*result,diagnostics,cancel); rebuild_mesh(*result,cancel); return result;
}
static std::shared_ptr<Mesh> envelope(uint64_t fields,uint64_t source,uint64_t budget,double* diagnostics,uint64_t cancel) {
    if(!diagnostics) throw std::runtime_error("Missing skin diagnostic buffer.");
    std::fill(diagnostics,diagnostics+19,0.0);
    const auto input=get_fields(fields); SceneAccess access(source,cancel);
    // Like the addon, this budget governs sparse fields, not mesh/output allocation.
    auto tiles=prepare_tiles(access.value,*input,budget,cancel);
    return extract_envelope(*tiles,diagnostics,cancel);
}
}
uint64_t af_skin_envelope_mesh(uint64_t fields,uint64_t scene,uint64_t budget,double* diagnostics,uint64_t cancel) {
    try { return af::retain(af::skin::envelope(fields,scene,budget,diagnostics,cancel)); }
    catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
