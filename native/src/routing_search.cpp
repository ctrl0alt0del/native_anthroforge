#include "routing_planner.hpp"

namespace af::routing {
using Heap=std::priority_queue<std::pair<double,int>,std::vector<std::pair<double,int>>,
                               std::greater<std::pair<double,int>>>;
struct Link { int next; double length; size_t proof; };
struct SearchGraph {
    std::vector<std::vector<Link>> rows;
    std::vector<int8_t> proofs;
    std::vector<double> heuristic;
};
static uint64_t key(int a,int b) {
    return (uint64_t(std::min(a,b))<<32)|uint32_t(std::max(a,b));
}
static SearchGraph capture(const Planning& plan,const Route& points,const Graph& rows) {
    SearchGraph graph{std::vector<std::vector<Link>>(points.size()),{}, {}};
    std::unordered_map<uint64_t,size_t> proofs;
    for(int i=0;i<int(points.size());++i) {
        check_cancel(plan.input.cancel); graph.heuristic.push_back(kernel::norm(kernel::sub(points[i],points[1])));
        for(int64_t j:rows[i]) {
            const auto [found,inserted]=proofs.emplace(key(i,int(j)),graph.proofs.size());
            if(inserted) graph.proofs.push_back(0);
            graph.rows[i].push_back({int(j),kernel::norm(kernel::sub(points[i],points[j])),found->second});
        }
    }
    return graph;
}
static void expand(const SearchGraph& graph,int node,std::vector<double>& distances,
                   std::vector<int>& parents,Heap& heap) {
    for(const auto& edge:graph.rows[node]) {
        if(graph.proofs[edge.proof]<0) continue;
        const double cost=distances[node]+edge.length;
        if(cost<distances[edge.next]) {
            distances[edge.next]=cost; parents[edge.next]=node;
            heap.emplace(cost+graph.heuristic[edge.next],edge.next);
        }
    }
}
static std::vector<int> path(const std::vector<int>& parents) {
    std::vector<int> nodes{1};
    while(parents[nodes.back()]>=0) nodes.push_back(parents[nodes.back()]);
    std::reverse(nodes.begin(),nodes.end()); return nodes;
}
static std::vector<int> astar(const Planning& plan,const SearchGraph& graph) {
    Heap heap; heap.emplace(0,0);
    std::vector<double> distances(graph.rows.size(),INFINITY); distances[0]=0;
    std::vector<int> parents(graph.rows.size(),-1); std::vector<bool> seen(graph.rows.size(),false);
    while(!heap.empty()) {
        check_cancel(plan.input.cancel); const int node=heap.top().second; heap.pop();
        if(node==1) return path(parents);
        if(seen[node]) continue;
        seen[node]=true; expand(graph,node,distances,parents,heap);
    }
    return {};
}
static bool validate(const Planning& plan,const Route& points,SearchGraph& graph,const std::vector<int>& path) {
    bool valid=true;
    for(size_t i=1;i<path.size();++i) {
        check_cancel(plan.input.cancel); const int a=path[i-1],b=path[i];
        const auto& row=graph.rows[a];
        const auto edge=std::find_if(row.begin(),row.end(),[b](const Link& link){return link.next==b;});
        auto& proof=graph.proofs[edge->proof];
        if(!proof) proof=clear(plan,points[a],points[b],a==0?plan.first:a==1?plan.last:0,
                                  b==0?plan.first:b==1?plan.last:0)?1:-1;
        valid=valid&&proof>0;
    }
    return valid;
}
Route search_graph(const Planning& plan,const Route& points,const Graph& rows) {
    auto graph=capture(plan,points,rows);
    for(int trial=0;trial<512;++trial) {
        const auto nodes=astar(plan,graph); if(nodes.empty()) return {};
        if(validate(plan,points,graph,nodes)) {
            Route result; for(int node:nodes) result.push_back(points[node]); return result;
        }
    }
    return {};
}
}
