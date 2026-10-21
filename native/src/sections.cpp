#include "anthroforge/sections.h"
#include "mesh_internal.hpp"
#include <map>
#include <set>
namespace af::section {
using Key=std::pair<int,int>;
struct End { Key key; V3 point; };
struct Query {
    const Mesh& mesh; M4 frame; Eigen::Vector4d plane; double epsilon;
    double* lines; int capacity,count=0; int64_t coplanar=0; bool truncated=false;
    std::set<std::pair<Key,Key>> segments{};
    std::map<Key,int> flat_edges{};
};
static void emit(Query& query,End a,End b) {
    if(a.key==b.key) return;
    if(a.key>b.key) std::swap(a,b);
    if(!query.segments.emplace(a.key,b.key).second) return;
    if(query.count+2>query.capacity) { query.truncated=true; return; }
    for(const auto& end:{a,b}) {
        for(int axis=0;axis<3;++axis) query.lines[3*query.count+axis]=end.point[axis];
        ++query.count;
    }
}
static void flat(Query& query,const Eigen::Vector3i& ids) {
    ++query.coplanar;
    for(int j=0;j<3;++j) ++query.flat_edges[std::minmax(ids[j],ids[(j+1)%3])];
}
static std::vector<End> crossings(const Query& query,const Eigen::Vector3i& ids,const std::array<V3,3>& points,const V3& distances) {
    std::map<Key,V3> unique;
    for(int j=0;j<3;++j) {
        const int k=(j+1)%3;
        if(std::abs(distances[j])<=query.epsilon) unique[{ids[j],ids[j]}]=points[j];
        if((distances[j]>query.epsilon&&distances[k]<-query.epsilon)||(distances[j]<-query.epsilon&&distances[k]>query.epsilon)) {
            const double t=distances[j]/(distances[j]-distances[k]);
            unique[std::minmax(ids[j],ids[k])]=points[j]+(points[k]-points[j])*t;
        }
    }
    std::vector<End> result; for(const auto& [key,point]:unique) result.push_back({key,point}); return result;
}
static void triangle(Query& query,int face) {
    const Eigen::Vector3i ids=query.mesh.triangles.row(face);
    std::array<V3,3> points; V3 distances;
    for(int j=0;j<3;++j) {
        points[j]=point(query.frame,query.mesh.vertices.row(ids[j]));
        distances[j]=query.plane.head<3>().dot(points[j])+query.plane[3];
    }
    if(distances.cwiseAbs().maxCoeff()<=query.epsilon) { flat(query,ids); return; }
    const auto ends=crossings(query,ids,points,distances);
    if(ends.size()==2) emit(query,ends[0],ends[1]);
}
static void flat_boundaries(Query& query,uint64_t cancel) {
    for(const auto& [edge,count]:query.flat_edges) if(count==1) {
        check_cancel(cancel);
        const End a{{edge.first,edge.first},point(query.frame,query.mesh.vertices.row(edge.first))};
        const End b{{edge.second,edge.second},point(query.frame,query.mesh.vertices.row(edge.second))};
        emit(query,a,b); if(query.truncated) break;
    }
}
static Query query(const Mesh& mesh,const double* frame,const double* plane,int capacity,double* lines) {
    const Eigen::Vector4d equation(plane); const double norm=equation.head<3>().norm();
    if(!equation.allFinite()||norm<1e-12||!M4(frame).allFinite()||capacity<2||capacity>32768)
        throw std::runtime_error("Section plane, transform and bounded capacity must be valid.");
    const double extent=mesh.vertices.rows()?mesh.vertices.cwiseAbs().maxCoeff():0;
    const double scale=std::max({1.0,extent,M4(frame).cwiseAbs().maxCoeff(),std::abs(equation[3])/norm});
    return {mesh,M4(frame),equation/norm,64*std::numeric_limits<double>::epsilon()*scale,lines,capacity};
}
}
int af_section_contours(uint64_t handle,const double* frame,const double* plane,int capacity,double* lines,int64_t* counts,uint64_t cancel) {
    try {
        const auto mesh=af::mesh(handle); auto query=af::section::query(*mesh,frame,plane,capacity,lines);
        for(int face=0;face<mesh->triangles.rows();++face) {
            af::check_cancel(cancel); af::section::triangle(query,face); if(query.truncated) break;
        }
        if(!query.truncated) af::section::flat_boundaries(query,cancel);
        counts[0]=query.count; counts[1]=query.coplanar; counts[2]=query.truncated; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
