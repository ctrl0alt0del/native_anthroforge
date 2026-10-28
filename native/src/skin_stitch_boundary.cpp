#include "skin_stitch.hpp"
namespace af::skin_stitch {
std::set<Edge> boundary(const std::vector<Quad>& faces) {
    std::map<Edge,int> counts;
    for(const auto& face:faces) for(const auto& edge:skin_quads::edges(face)) ++counts[edge];
    std::set<Edge> result;
    for(const auto& [edge,count]:counts) if(count==1) result.insert(edge);
    return result;
}
static std::vector<int64_t> traverse(std::set<int64_t>& pending,const std::map<int64_t,std::vector<int64_t>>& graph,uint64_t cancel) {
    const auto start=*pending.begin(); int64_t current=start,previous=-1; std::vector<int64_t> result;
    do {
        check_cancel(cancel);
        if(!pending.erase(current)) throw std::runtime_error("Skin topology has an ambiguous boundary.");
        result.push_back(current); const auto& neighbors=graph.at(current);
        if(neighbors.size()!=2) throw std::runtime_error("Skin topology boundary is not a closed ring.");
        const int64_t next=neighbors[0]==previous?neighbors[1]:neighbors[0]; previous=current; current=next;
    } while(current!=start);
    if(result.size()<3) throw std::runtime_error("Skin topology boundary has fewer than three points.");
    return result;
}
std::vector<std::vector<int64_t>> boundaries(const std::vector<Quad>& faces,uint64_t cancel) {
    check_cancel(cancel); const auto edges=boundary(faces); std::set<int64_t> pending;
    std::map<int64_t,std::vector<int64_t>> graph;
    for(const auto& [a,b]:edges) { pending.insert(a); pending.insert(b); graph[a].push_back(b); graph[b].push_back(a); }
    std::vector<std::vector<int64_t>> result;
    while(!pending.empty()) result.push_back(traverse(pending,graph,cancel));
    return result;
}
void validate(const std::vector<Quad>& faces,int first,int second) {
    std::set<Edge> expected;
    for(int i=0;i<first;++i) expected.insert(std::minmax(int64_t(i),int64_t((i+1)%first)));
    for(int i=0;i<second;++i) expected.insert(std::minmax(int64_t(first+i),int64_t(first+(i+1)%second)));
    if(boundary(faces)!=expected) throw std::runtime_error("Skin transition boundary mismatch.");
}
Quads strip(const Vertices& first,const Vertices& second,std::vector<Quad> faces) {
    Quads out; out.faces=std::move(faces);
    for(int i=0;i<first.rows();++i) out.points.push_back(first.row(i));
    for(int i=0;i<second.rows();++i) out.points.push_back(second.row(i));
    out.regions.assign(out.faces.size(),skin_quads::Transition); out.guides.assign(out.faces.size(),-1); return out;
}
}
