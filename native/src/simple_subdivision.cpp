// SPDX-License-Identifier: GPL-3.0-or-later
// Linear face/edge splitting (Blender Simple subdivision), without surface smoothing.
#include "construction_internal.hpp"
#include <map>

namespace af::subdivision {
using Edges=std::map<std::pair<int64_t,int64_t>,int64_t>;
static int64_t midpoint(Points& points,Edges& edges,int64_t a,int64_t b) {
    const auto key=std::minmax(a,b); const auto found=edges.find(key);
    if(found!=edges.end()) return found->second;
    const auto index=int64_t(points.size()); points.push_back((points[size_t(a)]+points[size_t(b)])*.5);
    edges.emplace(key,index); return index;
}
static void face(Points& points,Faces& output,Edges& edges,const std::vector<int64_t>& source) {
    V3 center=V3::Zero(); for(auto i:source) center+=points[size_t(i)];
    const auto middle=int64_t(points.size()); points.push_back(center/double(source.size()));
    for(size_t j=0;j<source.size();++j) {
        const auto a=source[j],b=source[(j+1)%source.size()],c=source[(j+source.size()-1)%source.size()];
        output.push_back({a,midpoint(points,edges,a,b),middle,midpoint(points,edges,c,a)});
    }
}
static std::shared_ptr<Mesh> once(const Mesh& mesh,uint64_t cancel) {
    if(mesh.corners.size()>4000000) throw std::runtime_error("Subdivision exceeds the geometry budget.");
    Points points; Faces faces; Edges edges; std::vector<int> parents; int index=0;
    for(int i=0;i<mesh.vertices.rows();++i) points.push_back(mesh.vertices.row(i));
    for(const auto& polygon:mesh_faces(mesh)) {
        check_cancel(cancel); face(points,faces,edges,polygon);
        parents.insert(parents.end(),polygon.size(),index++);
    }
    auto result=make_mesh(points,faces,cancel,false);
    refine_triangle_material(mesh,*result,parents,cancel); return result;
}
}
uint64_t af_simple_subdivision(uint64_t source,int levels,uint64_t cancel) {
    try {
        if(levels<0||levels>5) throw std::runtime_error("Invalid Simple subdivision level.");
        auto mesh=af::mesh(source);
        for(int i=0;i<levels;++i) mesh=af::subdivision::once(*mesh,cancel);
        return af::retain(mesh);
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
int af_displace(const double* points,int count,const double* offset,const double* weights,int invert,double strength,double* output,uint64_t cancel) {
    try {
        if(count<0||!offset||!std::isfinite(strength)||(count&&(!points||!output))) throw std::runtime_error("Invalid displacement buffers.");
        const af::V3 delta(offset); if(!delta.allFinite()) throw std::runtime_error("Nonfinite displacement.");
        for(int i=0;i<count;++i) {
            if(i%1024==0) af::check_cancel(cancel);
            const double weight=weights?(invert?1-weights[i]:weights[i]):1;
            Eigen::Map<af::V3> point(output+3*i); point=af::V3(points+3*i)+strength*weight*delta;
            if(!point.allFinite()) throw std::runtime_error("Nonfinite displaced point.");
        }
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
