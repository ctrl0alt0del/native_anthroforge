// Blender bisect/triangulate policy adapted to owned triangle inputs.
// Convex planar cut quads retain the Blender beauty area/perimeter criterion.
#include "skin_symmetry.hpp"
namespace af::skin_symmetry {
using F3=Eigen::Vector3f;
struct Cut { Points points; Faces faces; std::vector<float> distances; std::map<skin_quads::Edge,int64_t> edges; };
static Cut capture(const Mesh& source,const Plane& plane,uint64_t cancel) {
    Cut result; const F3 normal=plane.normal.cast<float>(),origin=plane.origin.cast<float>();
    for(int i=0;i<source.vertices.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        const F3 point=source.vertices.row(i).cast<float>();
        if(!point.allFinite()) throw std::runtime_error("Skin half-mesh coordinates exceed float range.");
        result.points.push_back(point.cast<double>()); result.distances.push_back((point-origin).dot(normal));
    }
    return result;
}
static int64_t crossing(Cut& cut,int64_t a,int64_t b) {
    const skin_quads::Edge key=std::minmax(a,b); const auto found=cut.edges.find(key);
    if(found!=cut.edges.end()) return found->second;
    const float d=cut.distances[key.first],e=cut.distances[key.second],factor=d/(d-e);
    const F3 start=cut.points[key.first].cast<float>(),end=cut.points[key.second].cast<float>();
    const F3 point=start+factor*(end-start); const auto index=int64_t(cut.points.size());
    cut.points.push_back(point.cast<double>()); cut.edges.emplace(key,index); return index;
}
static std::vector<int64_t> clipped(Cut& cut,const Eigen::Vector3i& face) {
    std::vector<int64_t> polygon;
    for(int i=0;i<3;++i) {
        const int a=face[i],b=face[(i+1)%3]; const float first=cut.distances[a],second=cut.distances[b];
        if(first<=0) polygon.push_back(a);
        if((first<0&&second>0)||(first>0&&second<0)) polygon.push_back(crossing(cut,a,b));
    }
    return polygon;
}
static float quality(const F3& a,const F3& b,const F3& c) {
    const float perimeter=(a-b).norm()+(b-c).norm()+(c-a).norm();
    return perimeter>0?(b-a).cross(c-a).norm()/perimeter:0;
}
static void triangulate(Cut& cut,const std::vector<int64_t>& polygon) {
    if(polygon.size()<3) return;
    if(polygon.size()==3) { cut.faces.push_back(polygon); return; }
    std::array<F3,4> p; for(int i=0;i<4;++i) p[i]=cut.points[polygon[i]].cast<float>();
    const float first=quality(p[0],p[1],p[2])+quality(p[0],p[2],p[3]);
    const float second=quality(p[1],p[2],p[3])+quality(p[1],p[3],p[0]);
    const int start=first>second?0:1;
    cut.faces.push_back({polygon[start],polygon[(start+1)%4],polygon[(start+2)%4]});
    cut.faces.push_back({polygon[start],polygon[(start+2)%4],polygon[(start+3)%4]});
}
static std::shared_ptr<Mesh> complete(Cut& cut,uint64_t cancel) {
    if(cut.faces.empty()) throw std::runtime_error("Skin symmetry plane leaves no source surface on the negative side.");
    std::set<int64_t> used; for(const auto& face:cut.faces) used.insert(face.begin(),face.end());
    Points points; std::vector<int64_t> map(cut.points.size(),-1);
    for(const auto index:used) { map[index]=int64_t(points.size()); points.push_back(cut.points[index]); }
    for(auto& face:cut.faces) for(auto& index:face) index=map[index];
    return make_mesh(points,cut.faces,cancel);
}
std::shared_ptr<Mesh> half(const Mesh& source,const Plane& plane,uint64_t cancel) {
    auto cut=capture(source,plane,cancel);
    for(int i=0;i<source.triangles.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        triangulate(cut,clipped(cut,source.triangles.row(i)));
    }
    return complete(cut,cancel);
}
}
