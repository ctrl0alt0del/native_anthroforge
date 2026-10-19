// SPDX-License-Identifier: GPL-3.0-or-later
// Port of soft_tissue_surface_field.py and source_surface_normals.py.
#include "tissue_shapes.hpp"
#include <queue>
#include <limits>

namespace af::tissue {
V3 unit(const V3& value) {
    if(!value.allFinite()||value.norm()<=1e-12) throw std::runtime_error("Tissue has a degenerate source frame.");
    return value.normalized();
}
static void add_edge(Edges& edges,int64_t a,int64_t b) {
    auto& use=edges[std::minmax(a,b)];
    if(a==b||use.count>=2||(use.count==1&&use.oriented!=Edge(b,a)))
        throw std::runtime_error("Tissue source requires consistent manifold winding.");
    if(!use.count) use.oriented={a,b};
    ++use.count;
}
Edges boundary_topology(const Faces& faces,uint64_t cancel) {
    Edges edges;
    for(const auto& face:faces) {
        check_cancel(cancel);
        for(size_t i=0;i<face.size();++i) add_edge(edges,face[i],face[(i+1)%face.size()]);
    }
    return edges;
}
static V3 area(const Vertices& points,const std::vector<int64_t>& face) {
    V3 value=V3::Zero(); const V3 origin=points.row(face[0]);
    for(size_t i=0;i<face.size();++i) {
        const V3 a=points.row(face[i]),b=points.row(face[(i+1)%face.size()]);
        value+=(a-origin).cross(b-origin);
    }
    return value;
}
Vertices surface_normals(const Mesh& source,const Faces& faces,uint64_t cancel) {
    Vertices normals=Vertices::Zero(source.vertices.rows(),3);
    for(const auto& face:faces) {
        check_cancel(cancel); const V3 normal=area(source.vertices,face);
        for(auto index:face) normals.row(index)+=normal.transpose();
    }
    for(int64_t i=0;i<normals.rows();++i) normals.row(i)=unit(normals.row(i));
    return normals;
}
using Neighbors=std::vector<std::vector<std::pair<int64_t,double>>>;
using Queue=std::priority_queue<std::pair<double,int64_t>,std::vector<std::pair<double,int64_t>>,std::greater<>>;
static Neighbors adjacency(const Mesh& mesh,const Edges& edges) {
    Neighbors graph(size_t(mesh.vertices.rows()));
    for(const auto& pair:edges) {
        const auto [a,b]=pair.first;
        const double length=(mesh.vertices.row(a)-mesh.vertices.row(b)).norm();
        graph[size_t(a)].emplace_back(b,length); graph[size_t(b)].emplace_back(a,length);
    }
    return graph;
}
static void walk(Queue& queue,const Neighbors& graph,std::vector<double>& distances,uint64_t cancel) {
    while(!queue.empty()) {
        check_cancel(cancel); const auto [distance,index]=queue.top(); queue.pop();
        if(distance>distances[size_t(index)]) continue;
        for(const auto& [neighbor,weight]:graph[size_t(index)]) {
            if(distance+weight>=distances[size_t(neighbor)]) continue;
            distances[size_t(neighbor)]=distance+weight;
            queue.emplace(distance+weight,neighbor);
        }
    }
}
std::vector<double> boundary_weights(const Mesh& mesh,const Edges& edges,uint64_t cancel) {
    std::vector<double> distances(size_t(mesh.vertices.rows()),std::numeric_limits<double>::infinity()); Queue queue;
    for(const auto& pair:edges) if(pair.second.count==1) for(auto i:{pair.first.first,pair.first.second}) {
        distances[size_t(i)]=0; queue.emplace(0,i);
    }
    if(queue.empty()) return std::vector<double>(distances.size(),1);
    walk(queue,adjacency(mesh,edges),distances,cancel);
    double maximum=0;
    for(double d:distances) if(std::isfinite(d)) maximum=std::max(maximum,d);
    for(double& d:distances) { const double x=maximum>0?d/maximum:0; d=std::isfinite(d)?x*x*(3-2*x):1; }
    return distances;
}
void validate_shape(const AfTissueShape& s) {
    for(double value:{s.amount,s.minimum,s.power,s.width,s.endpoint_taper,s.scale[0],s.scale[1],s.scale[2]})
        if(!std::isfinite(value)) throw std::runtime_error("Tissue shape settings must be finite.");
    if(s.amount<0||s.minimum<0||s.minimum>s.amount||s.power<=0||s.width<=0||s.endpoint_taper<0||s.endpoint_taper>1)
        throw std::runtime_error("Invalid tissue thickness, profile or taper.");
    if(s.segments<3||s.segments>256||s.scale[0]<=0||s.scale[1]<=0||s.scale[2]<=0)
        throw std::runtime_error("Invalid tissue resolution or radial scale.");
}
}
