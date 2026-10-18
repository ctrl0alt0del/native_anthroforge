// SPDX-License-Identifier: GPL-3.0-or-later
// Boundary constraints, four half-Laplacian passes and boundary-last ordering from addon.
#include "surface_patch_internal.hpp"

namespace af::curve_surface {
static bool fixed(const PatchKey& key,int count) {
    if(key[0]==0) return key[1]<count;
    return key[0]==1&&(key[2]-key[1]==1||(key[1]==0&&key[2]==count-1));
}
static std::vector<std::set<int>> adjacency(const Patch& patch) {
    std::vector<std::set<int>> result(patch.points.size());
    for(const auto& face:patch.faces)
        for(size_t i=0;i<face.size();++i) {
            const int a=int(face[i]),b=int(face[(i+1)%face.size()]);
            result[a].insert(b); result[b].insert(a);
        }
    return result;
}
static Points fair_pass(const Patch& patch,const std::vector<std::set<int>>& neighbors,int count,uint64_t cancel) {
    Points result=patch.points;
    for(size_t i=0;i<result.size();++i) {
        check_cancel(cancel);
        if(fixed(patch.keys[i],count)||neighbors[i].empty()) continue;
        V3 average=V3::Zero(); for(const int j:neighbors[i]) average+=patch.points[j];
        result[i]=0.5*(patch.points[i]+average/double(neighbors[i].size()));
    }
    return result;
}
void fair(Patch& patch,int boundary_count,uint64_t cancel) {
    const auto neighbors=adjacency(patch);
    for(int i=0;i<4;++i) patch.points=fair_pass(patch,neighbors,boundary_count,cancel);
}
void boundary_last(Patch& patch,int count) {
    std::vector<int> order; Points points; std::vector<int> remap(patch.points.size());
    for(size_t i=0;i<patch.points.size();++i)
        if(patch.keys[i][0]!=0||patch.keys[i][1]>=count) order.push_back(int(i));
    for(int i=0;i<count;++i) order.push_back(patch.indices.at({0,i,0,0,0}));
    for(size_t i=0;i<order.size();++i) { points.push_back(patch.points[order[i]]); remap[order[i]]=int(i); }
    for(auto& face:patch.faces) for(auto& index:face) index=remap[size_t(index)];
    patch.points=std::move(points);
}
std::shared_ptr<Mesh> patch(const Row& row,int resolution,bool flip,uint64_t cancel) {
    if(!row.closed||resolution<1||resolution>64) throw std::runtime_error("Patch requires a closed curve and resolution 1..64.");
    auto points=row.points; const auto projected=project(points,cancel);
    const auto triangles=triangulate(points,projected,cancel);
    auto result=subdivide(points,triangles,resolution,cancel);
    fair(result,int(row.points.size()),cancel); boundary_last(result,int(row.points.size()));
    if(flip) for(auto& face:result.faces) std::reverse(face.begin(),face.end());
    return make_mesh(result.points,result.faces,cancel,false);
}
}
