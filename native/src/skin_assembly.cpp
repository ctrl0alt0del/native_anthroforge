#include "skin_assembly.hpp"
#include <cmath>

namespace af::skin {
static int64_t vertex(Assembly& output,const V3& point) {
    VertexKey key{};
    for(int a=0;a<3;++a) key[a]=std::nearbyint(point[a]*100000.0)/100000.0;
    const auto next=int64_t(output.vertices.size());
    const auto found=output.vertices.emplace(key,std::make_pair(point,next));
    return found.first->second.second;
}
void append(Assembly& output,const TileMesh& tile,const std::array<int,3>& start) {
    check_cancel(output.cancel);
    std::vector<int64_t> remap; remap.reserve(tile.vertices.size()/3);
    for(size_t i=0;i<tile.vertices.size();i+=3) {
        const V3 p(double(tile.vertices[i])+start[0],double(tile.vertices[i+1])+start[1],double(tile.vertices[i+2])+start[2]);
        remap.push_back(vertex(output,p));
    }
    for(size_t i=0;i<tile.faces.size();i+=3)
        output.faces.push_back({remap[tile.faces[i]],remap[tile.faces[i+1]],remap[tile.faces[i+2]]});
}
std::shared_ptr<Mesh> assemble(Assembly& output,const V3& origin,double voxel) {
    check_cancel(output.cancel); Points points; points.reserve(output.vertices.size());
    std::vector<int64_t> remap(output.vertices.size());
    for(const auto& item:output.vertices) {
        remap[item.second.second]=int64_t(points.size());
        const V3 world=item.second.first*voxel+origin;
        points.push_back(world.cast<float>().cast<double>());
    }
    for(auto& face:output.faces) for(auto& i:face) i=remap[i];
    if(output.faces.empty()) throw std::runtime_error("Skin has no resolved surface.");
    return make_mesh(points,output.faces,output.cancel,false);
}
}
