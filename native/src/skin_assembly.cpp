#include "skin_assembly.hpp"
#include <algorithm>
#include <cmath>

namespace af::skin {
// Match addon np.unique(round(vertices, 5)): sorted keys, first unrounded sample.
struct KeyedVertex { std::array<double,3> key; size_t original; };
static std::vector<KeyedVertex> sorted_keys(const Assembly& input) {
    std::vector<KeyedVertex> keys(input.vertices.size());
    for(size_t i=0;i<keys.size();++i) {
        if((i&8191)==0) check_cancel(input.cancel);
        keys[i].original=i;
        for(int a=0;a<3;++a) keys[i].key[a]=std::nearbyint(input.vertices[i][a]*100000.0)/100000.0;
    }
    size_t comparisons=0;
    std::sort(keys.begin(),keys.end(),[&](const KeyedVertex& a,const KeyedVertex& b) {
        if((++comparisons&65535)==0) check_cancel(input.cancel);
        return a.key==b.key?a.original<b.original:a.key<b.key;
    });
    return keys;
}
static Points stitch(const Assembly& input,std::vector<int64_t>& remap,const V3& origin,double voxel) {
    const auto keys=sorted_keys(input); Points points; points.reserve(keys.size());
    for(size_t i=0;i<keys.size();++i) {
        if((i&8191)==0) check_cancel(input.cancel);
        if(i==0||keys[i].key!=keys[i-1].key) {
            const V3 world=input.vertices[keys[i].original]*voxel+origin;
            points.push_back(world.cast<float>().cast<double>());
        }
        remap[keys[i].original]=int64_t(points.size())-1;
    }
    return points;
}
void append(Assembly& output,const TileMesh& tile,const std::array<int,3>& start) {
    check_cancel(output.cancel);
    const auto offset=int64_t(output.vertices.size());
    for(size_t i=0;i<tile.vertices.size();i+=3) {
        if(i%24576==0) check_cancel(output.cancel);
        const V3 p(double(tile.vertices[i])+start[0],double(tile.vertices[i+1])+start[1],double(tile.vertices[i+2])+start[2]);
        output.vertices.push_back(p);
    }
    for(size_t i=0;i<tile.faces.size();i+=3)
        output.faces.push_back({offset+tile.faces[i],offset+tile.faces[i+1],offset+tile.faces[i+2]});
}
std::shared_ptr<Mesh> assemble(Assembly& output,const V3& origin,double voxel) {
    check_cancel(output.cancel);
    if(output.faces.empty()) throw std::runtime_error("Skin has no resolved surface.");
    std::vector<int64_t> remap(output.vertices.size());
    const auto points=stitch(output,remap,origin,voxel);
    Points{}.swap(output.vertices);
    for(size_t i=0;i<output.faces.size();++i) {
        if((i&8191)==0) check_cancel(output.cancel);
        for(auto& vertex:output.faces[i]) vertex=remap[vertex];
    }
    std::vector<int64_t>{}.swap(remap);
    return make_mesh(points,output.faces,output.cancel,false);
}
}
