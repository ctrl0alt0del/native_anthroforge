#include "skin_meshing.hpp"
#include "construction_internal.hpp"
#include "anthroforge/skin_fields.h"
#include <bioimage_cpp/mesh/marching_cubes.hxx>

namespace af::skin {
static void validate_tile(const float* values,const std::array<int,3>& shape,uint64_t cancel) {
    check_cancel(cancel);
    if(!values) throw std::runtime_error("Missing skin tile field.");
    uint64_t count=1;
    for(const auto n:shape) {
        if(n<2||n>33) throw std::runtime_error("Skin tiles require dimensions between 2 and 33.");
        count*=n;
    }
    for(uint64_t i=0;i<count;++i) if(!std::isfinite(values[i]))
        throw std::runtime_error("Skin tile contains nonfinite values.");
}
TileMesh extract_tile(const float* values,const std::array<int,3>& shape,uint64_t cancel) {
    validate_tile(values,shape,cancel); using namespace bioimage_cpp;
    ConstArrayView<float> view{values,{shape[0],shape[1],shape[2]},
        {ptrdiff_t(shape[1])*shape[2],shape[2],1}};
    auto result=mesh::marching_cubes(view,0,1,mesh::MarchingCubesMethod::Lewiner,
        mesh::GradientDirection::Descent,nullptr,false);
    check_cancel(cancel); return {std::move(result.vertices),std::move(result.faces)};
}
static std::shared_ptr<Mesh> tile_mesh(const TileMesh& tile,uint64_t cancel) {
    Points points; points.reserve(tile.vertices.size()/3); Faces faces; faces.reserve(tile.faces.size()/3);
    for(size_t i=0;i<tile.vertices.size();i+=3) points.emplace_back(tile.vertices[i],tile.vertices[i+1],tile.vertices[i+2]);
    for(size_t i=0;i<tile.faces.size();i+=3) faces.push_back({tile.faces[i],tile.faces[i+1],tile.faces[i+2]});
    if(faces.empty()) throw std::runtime_error("Skin tile contains no resolved surface.");
    return make_mesh(points,faces,cancel,false);
}
}
uint64_t af_skin_tile_mesh(const float* values,const int* shape,uint64_t cancel) {
    try {
        if(!shape) throw std::runtime_error("Missing skin tile shape.");
        const auto result=af::skin::extract_tile(values,{shape[0],shape[1],shape[2]},cancel);
        return af::retain(af::skin::tile_mesh(result,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
