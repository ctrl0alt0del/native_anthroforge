// Blender 5.0.1 bmo_normals.cc: outward seed and manifold-neighbor propagation.
// Blender Authors, GPL-2.0-or-later. Owned quad adapter; no BMesh runtime.
#include "skin_stitch.hpp"
#include <cfloat>
namespace af::skin_stitch {
using F3=Eigen::Vector3f;
struct Seed { int face=0; bool flip=false; std::array<float,3> score{FLT_EPSILON,-FLT_MAX,-FLT_MAX}; };
struct FaceInfo { std::array<F3,4> points; F3 normal,center; float area; };
static FaceInfo info(const Quads& mesh,int index) {
    FaceInfo out; out.normal=F3::Zero(); out.center=F3::Zero(); float weight=0;
    for(int i=0;i<4;++i) out.points[i]=mesh.points[mesh.faces[index][i]].cast<float>();
    for(int i=1;i<3;++i) out.normal+=(out.points[i]-out.points[0]).cross(out.points[i+1]-out.points[0]);
    out.area=.5f*out.normal.norm(); if(out.area>0) out.normal.normalize();
    for(int i=0;i<4;++i) {
        const float edge=(out.points[i]-out.points[(i+1)%4]).norm();
        out.center+=edge*(out.points[i]+out.points[(i+1)%4]); weight+=2*edge;
    }
    if(weight>0) out.center/=weight;
    return out;
}
static F3 group_center(const std::vector<FaceInfo>& faces,const std::vector<int>& group) {
    F3 center=F3::Zero(); float area=0; const float factor=1.0f/float(group.size());
    for(const int i:group) { center+=faces[i].center*(factor*faces[i].area); area+=faces[i].area; }
    if(area!=0) center/=area; return center;
}
static void consider(Seed& best,const FaceInfo& face,int index,int corner,const F3& center) {
    F3 direction=face.points[corner]-center; const float distance=direction.squaredNorm();
    if(distance<best.score[0]||distance<=FLT_EPSILON) return;
    direction/=std::sqrt(distance); F3 next=face.points[(corner+1)%4]-face.points[corner],previous=face.points[(corner+3)%4]-face.points[corner];
    if(next.norm()<=FLT_EPSILON||previous.norm()<=FLT_EPSILON) return;
    next.normalize(); previous.normalize(); const float edge=std::max(direction.dot(next),direction.dot(previous));
    if(distance==best.score[0]&&edge<best.score[1]) return;
    F3 normal=next.cross(previous); if(normal.norm()<=FLT_EPSILON) return; normal.normalize();
    if(normal.dot(face.normal)<0) normal=-normal;
    const float dot=direction.dot(normal);
    if(distance>best.score[0]||edge>best.score[1]||std::abs(dot)>best.score[2]) best={index,dot<0,{distance,edge,std::abs(dot)}};
}
static Seed seed(const std::vector<FaceInfo>& faces,const std::vector<int>& group) {
    const F3 center=group_center(faces,group); Seed result; result.face=group.front();
    for(const int i:group) for(int j=0;j<4;++j) consider(result,faces[i],i,j,center);
    return result;
}
using Graph=std::vector<std::vector<std::pair<int,bool>>>;
static Graph neighbors(const Quads& mesh) {
    std::map<Edge,std::vector<std::pair<int,bool>>> owners;
    for(int i=0;i<int(mesh.faces.size());++i) for(int j=0;j<4;++j) {
        const auto a=mesh.faces[i][j],b=mesh.faces[i][(j+1)%4]; owners[std::minmax(a,b)].emplace_back(i,a<b);
    }
    Graph result(mesh.faces.size());
    for(const auto& [edge,values]:owners) if(values.size()==2) {
        const auto a=values[0],b=values[1]; result[a.first].emplace_back(b.first,a.second==b.second); result[b.first].emplace_back(a.first,a.second==b.second);
    }
    return result;
}
static std::vector<int> group(const Graph& graph,int start,std::vector<bool>& seen,uint64_t cancel) {
    std::vector<int> stack{start},result; seen[start]=true;
    while(!stack.empty()) {
        check_cancel(cancel); const int current=stack.back(); stack.pop_back(); result.push_back(current);
        for(const auto& [other,same]:graph[current]) if(!seen[other]) { seen[other]=true; stack.push_back(other); }
    }
    std::sort(result.begin(),result.end()); return result;
}
static void propagate(const Graph& graph,const Seed& start,std::vector<int>& flips,uint64_t cancel) {
    std::vector<int> stack{start.face}; flips[start.face]=start.flip?1:0;
    while(!stack.empty()) {
        check_cancel(cancel); const int current=stack.back(); stack.pop_back();
        for(const auto& [other,same]:graph[current]) if(flips[other]<0) {
            flips[other]=same!=bool(flips[current]); stack.push_back(other);
        }
    }
}
void orient(Quads& mesh,uint64_t cancel) {
    const auto graph=neighbors(mesh); std::vector<FaceInfo> faces; std::vector<bool> seen(mesh.faces.size(),false);
    for(int i=0;i<int(mesh.faces.size());++i) { if(i%4096==0) check_cancel(cancel); faces.push_back(info(mesh,i)); }
    std::vector<int> flips(mesh.faces.size(),-1);
    for(int i=0;i<int(mesh.faces.size());++i) if(!seen[i]) {
        const auto component=group(graph,i,seen,cancel); propagate(graph,seed(faces,component),flips,cancel);
    }
    for(size_t i=0;i<mesh.faces.size();++i) if(flips[i]) std::reverse(mesh.faces[i].begin(),mesh.faces[i].end());
}
}
