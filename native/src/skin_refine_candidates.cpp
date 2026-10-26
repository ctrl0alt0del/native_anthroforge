#include "skin_quads.hpp"
namespace af::skin_quads {
static Vertices centers(const Quads& source,uint64_t cancel) {
    Vertices result(source.faces.size(),3);
    for(size_t i=0;i<source.faces.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        V3 center=V3::Zero(); for(auto v:source.faces[i]) center+=source.points[v];
        result.row(i)=center*.25;
    }
    return result;
}
static V3 plane_normal(const double* plane) {
    const V3 normal(plane+3);
    if(!normal.allFinite()||!V3(plane).allFinite()||normal.norm()<1e-12) throw std::runtime_error("Invalid refinement symmetry plane.");
    return normal.normalized();
}
static std::map<std::pair<int,int>,double> paired(const Quads& source,const std::vector<double>& scores,const double* plane,uint64_t cancel) {
    const auto points=centers(source,cancel); std::vector<int> ids(source.faces.size());
    for(size_t i=0;i<ids.size();++i) ids[i]=int(i);
    const skin_ownership::PointIndex tree(points,ids,cancel); const V3 normal=plane_normal(plane),origin(plane);
    std::map<std::pair<int,int>,double> result;
    for(size_t i=0;i<ids.size();++i) {
        if(i%1024==0) check_cancel(cancel);
        if(scores[i]<=1.35||source.regions[i]!=0) continue;
        const V3 p=points.row(i),reflected=p-2*(p-origin).dot(normal)*normal;
        const int other=tree.nearest(points,reflected).first; const std::pair<int,int> pair=std::minmax(int(i),other);
        if(scores[pair.second]>1.35&&source.regions[pair.second]==0) result[pair]=std::max(scores[i],scores[other]);
    }
    return result;
}
std::vector<std::vector<int>> candidates(const Quads& source,const std::vector<double>& scores,const double* plane,uint64_t cancel) {
    std::vector<std::pair<std::vector<int>,double>> values;
    if(plane) {
        for(const auto& entry:paired(source,scores,plane,cancel)) values.push_back({{entry.first.first,entry.first.second},entry.second});
    } else for(size_t i=0;i<scores.size();++i) if(scores[i]>1.35&&source.regions[i]==0) values.push_back({{int(i)},scores[i]});
    std::stable_sort(values.begin(),values.end(),[](const auto& a,const auto& b){return a.second>b.second;});
    std::vector<std::vector<int>> result;
    for(auto& entry:values) result.push_back(std::move(entry.first));
    return result;
}
static bool consume_boundaries(std::set<Edge> pending,const std::map<int64_t,std::set<int64_t>>& linked,uint64_t cancel) {
    while(!pending.empty()) {
        check_cancel(cancel); const auto edge=*pending.begin(); pending.erase(edge);
        auto previous=edge.first,current=edge.second; size_t count=1;
        while(current!=edge.first) {
            check_cancel(cancel); const auto& next=linked.at(current); const auto following=*next.begin()==previous?*next.rbegin():*next.begin();
            if(!pending.erase(std::minmax(current,following))) return false;
            previous=current; current=following; ++count;
        }
        if(count%2) return false;
    }
    return true;
}
bool even_boundaries(const Quads& source,uint64_t cancel) {
    std::map<Edge,int> counts;
    for(size_t i=0;i<source.faces.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        for(const auto& e:edges(source.faces[i])) ++counts[e];
    }
    std::map<int64_t,std::set<int64_t>> linked; std::set<Edge> pending;
    for(const auto& entry:counts) if(entry.second==1) { const auto e=entry.first; pending.insert(e); linked[e.first].insert(e.second); linked[e.second].insert(e.first); }
    for(const auto& entry:linked) if(entry.second.size()!=2) return false;
    return consume_boundaries(std::move(pending),linked,cancel);
}
}
