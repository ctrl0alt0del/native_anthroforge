#include "skin_stitch.hpp"
#include <numeric>
#include <tuple>
namespace af::skin_stitch {
static std::vector<std::tuple<double,int,int>> events(const Vertices& points,int side,bool closed) {
    const int count=int(points.rows())-(closed?0:1); std::vector<double> lengths(count); double total=0;
    for(int i=0;i<count;++i) { total+=(points.row((i+1)%points.rows())-points.row(i)).norm(); lengths[i]=total; }
    if(total<1e-12) throw std::runtime_error("Skin transition has zero perimeter.");
    std::vector<std::tuple<double,int,int>> result;
    for(int i=0;i<count;++i) result.emplace_back(std::nearbyint(lengths[i]/total*1e12)/1e12,side,i);
    return result;
}
std::vector<int> moves(const Vertices& first,const Vertices& second,bool closed) {
    auto values=events(first,1,closed); const auto other=events(second,2,closed);
    values.insert(values.end(),other.begin(),other.end()); std::sort(values.begin(),values.end());
    std::vector<int> result; for(const auto& [fraction,side,index]:values) result.push_back(side); return result;
}
std::vector<Triangle> zipper(const std::vector<int64_t>& first,const std::vector<int64_t>& second,const std::vector<int>& values,bool closed) {
    std::vector<Triangle> result; int a=0,b=0;
    for(const int move:values) {
        const int64_t current_a=first[closed?a%first.size():a],current_b=second[closed?b%second.size():b];
        if(move==1) { result.push_back({current_a,first[closed?(a+1)%first.size():a+1],current_b}); ++a; }
        else { result.push_back({current_a,second[closed?(b+1)%second.size():b+1],current_b}); ++b; }
    }
    return result;
}
Quad join(const Triangle& a,const Triangle& b) {
    std::map<Edge,int> counts; std::map<int64_t,std::vector<int64_t>> graph;
    for(const auto& triangle:{a,b}) for(int i=0;i<3;++i) ++counts[std::minmax(triangle[i],triangle[(i+1)%3])];
    for(const auto& [edge,count]:counts) if(count==1) { graph[edge.first].push_back(edge.second); graph[edge.second].push_back(edge.first); }
    if(graph.size()!=4) throw std::runtime_error("Skin zipper triangles do not form a quad.");
    Quad result; int64_t current=graph.begin()->first,previous=-1;
    for(int i=0;i<4;++i) {
        result[i]=current; const auto& neighbors=graph.at(current);
        if(neighbors.size()!=2) throw std::runtime_error("Skin zipper quad has ambiguous connectivity.");
        const int64_t next=neighbors[0]==previous?neighbors[1]:neighbors[0]; previous=current; current=next;
    }
    if(current!=result[0]) throw std::runtime_error("Skin zipper quad is open.");
    return result;
}
std::vector<Quad> paired(const std::vector<Triangle>& triangles) {
    if(triangles.size()%2) throw std::runtime_error("Skin transition triangle count must be even.");
    std::vector<Quad> result;
    for(size_t i=0;i<triangles.size();i+=2) result.push_back(join(triangles[i],triangles[i+1]));
    return result;
}
std::vector<Quad> regular_faces(const Vertices& first,const Vertices& second) {
    std::vector<int64_t> a(first.rows()),b(second.rows());
    std::iota(a.begin(),a.end(),0); std::iota(b.begin(),b.end(),first.rows());
    auto result=paired(zipper(a,b,moves(first,second,true),true));
    validate(result,int(first.rows()),int(second.rows())); return result;
}
}
