#include "skin_stitch.hpp"
namespace af::skin_stitch {
using Key=std::array<int64_t,3>;
static Key key(const V3& point,double tolerance) {
    Key result;
    for(int axis=0;axis<3;++axis) {
        const double value=point[axis]/tolerance;
        if(!std::isfinite(value)||std::abs(value)>9e18) throw std::runtime_error("Skin weld coordinates exceed the supported range.");
        result[axis]=int64_t(std::nearbyint(value));
    }
    return result;
}
static std::map<Key,std::pair<int64_t,V3>> vertices(const std::vector<Quads>& parts,double tolerance,uint64_t cancel) {
    std::map<Key,std::pair<int64_t,V3>> result;
    for(const auto& part:parts) for(size_t i=0;i<part.points.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        result.emplace(key(part.points[i],tolerance),std::make_pair(0,part.points[i]));
    }
    int64_t id=0; for(auto& [position,value]:result) value.first=id++;
    return result;
}
static void remap(Quads& out,const Quads& part,const std::map<Key,std::pair<int64_t,V3>>& map,double tolerance,uint64_t cancel) {
    std::vector<int64_t> ids; ids.reserve(part.points.size());
    for(size_t i=0;i<part.points.size();++i) { if(i%4096==0) check_cancel(cancel); ids.push_back(map.at(key(part.points[i],tolerance)).first); }
    for(size_t i=0;i<part.faces.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        Quad face; for(int j=0;j<4;++j) face[j]=ids[part.faces[i][j]];
        if(std::set<int64_t>(face.begin(),face.end()).size()!=4) continue;
        out.faces.push_back(face); out.regions.push_back(part.regions[i]); out.guides.push_back(part.guides[i]);
    }
}
static void deduplicate(Quads& mesh) {
    std::map<Quad,size_t> last;
    for(size_t i=0;i<mesh.faces.size();++i) { auto key=mesh.faces[i]; std::sort(key.begin(),key.end()); last[key]=i; }
    std::set<size_t> keep; for(const auto& [face,index]:last) keep.insert(index);
    Quads result; result.points=std::move(mesh.points);
    for(const auto i:keep) { result.faces.push_back(mesh.faces[i]); result.regions.push_back(mesh.regions[i]); result.guides.push_back(mesh.guides[i]); }
    mesh=std::move(result);
}
static void compact(Quads& mesh) {
    std::set<int64_t> used; for(const auto& face:mesh.faces) used.insert(face.begin(),face.end());
    Points points; std::vector<int64_t> indices(mesh.points.size(),-1);
    for(const auto i:used) { indices[i]=int64_t(points.size()); points.push_back(mesh.points[i]); }
    for(auto& face:mesh.faces) for(auto& vertex:face) vertex=indices[vertex];
    mesh.points=std::move(points);
}
Quads weld(const std::vector<Quads>& parts,double tolerance,bool unique,uint64_t cancel) {
    if(!std::isfinite(tolerance)||tolerance<=0) throw std::runtime_error("Skin weld tolerance must be positive.");
    const auto map=vertices(parts,tolerance,cancel); Quads result;
    for(const auto& [position,value]:map) result.points.push_back(value.second);
    for(const auto& part:parts) remap(result,part,map,tolerance,cancel);
    if(unique) deduplicate(result);
    check_cancel(cancel); compact(result); return result;
}
}
