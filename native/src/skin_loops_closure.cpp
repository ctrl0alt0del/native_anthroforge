#include "skin_loops.hpp"
namespace af::skin_flow {
std::vector<int> closure_route(const Vertices& points,const skin_loops::Graph& graph,int first,int last,uint64_t cancel);
}
namespace af::skin_loops {
static bool local_gap(const Vertices& points) {
    std::vector<double> lengths;
    for(int i=1;i<points.rows();++i) lengths.push_back((points.row(i)-points.row(i-1)).norm());
    std::sort(lengths.begin(),lengths.end()); const size_t n=lengths.size();
    const double median=.5*(lengths[n/2]+lengths[(n-1)/2]);
    return (points.row(points.rows()-1)-points.row(0)).norm()<=2*std::max(median,1e-9);
}
static void graph(Context& context) {
    context.graph.resize(context.mesh.vertices.rows());
    for(int i=0;i<context.mesh.triangles.rows();++i) {
        if(i%4096==0) check_cancel(context.cancel);
        const auto face=context.mesh.triangles.row(i);
        for(int j=0;j<3;++j) { context.graph[face[j]].push_back(face[(j+1)%3]); context.graph[face[(j+1)%3]].push_back(face[j]); }
    }
    for(auto& neighbors:context.graph) {
        std::sort(neighbors.begin(),neighbors.end()); neighbors.erase(std::unique(neighbors.begin(),neighbors.end()),neighbors.end());
    }
    std::vector<int> ids(context.mesh.vertices.rows());
    for(size_t i=0;i<ids.size();++i) ids[i]=int(i);
    context.index=std::make_unique<skin::PointIndex>(context.mesh.vertices,ids,context.cancel);
}
Vertices closure(Context& context,const Vertices& points) {
    if(local_gap(points)) return points;
    if(!context.index) graph(context);
    const int first=context.index->nearest(context.mesh.vertices,points.row(points.rows()-1)).first;
    const int last=context.index->nearest(context.mesh.vertices,points.row(0)).first;
    const auto route=skin_flow::closure_route(context.mesh.vertices,context.graph,first,last,context.cancel);
    if(route.size()<=2) return points;
    Vertices result(points.rows()+route.size()-2,3); result.topRows(points.rows())=points;
    for(size_t i=1;i+1<route.size();++i) result.row(points.rows()+i-1)=context.mesh.vertices.row(route[i]);
    return result;
}
}
