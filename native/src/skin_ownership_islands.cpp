#include "skin_ownership.hpp"
#include "skin_density.hpp"
#include <numeric>
namespace af::skin_ownership {
using Adjacency=std::vector<std::set<int>>;
static Adjacency neighbors(const Mesh& mesh,uint64_t cancel) {
    Adjacency result(mesh.vertices.rows());
    for(int i=0;i<mesh.triangles.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        for(int j=0;j<3;++j) {
            const int a=mesh.triangles(i,j),b=mesh.triangles(i,(j+1)%3);
            result[a].insert(b); result[b].insert(a);
        }
    }
    return result;
}
static std::vector<int> component(int first,const int* labels,const Adjacency& adjacency,std::vector<bool>& seen,uint64_t cancel) {
    std::vector<int> result{first}; seen[first]=true;
    for(size_t i=0;i<result.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        for(int linked:adjacency[result[i]]) if(!seen[linked]&&labels[linked]==labels[first]) {
            seen[linked]=true; result.push_back(linked);
        }
    }
    return result;
}
static void replace_component(int* labels,const std::vector<int>& group,const Adjacency& adjacency) {
    const std::set<int> members(group.begin(),group.end()); std::map<int,int> votes;
    for(int v:group) for(int linked:adjacency[v]) if(!members.count(linked)) ++votes[labels[linked]];
    int best=-1,count=0;
    for(const auto& vote:votes) if(vote.second>count) { best=vote.first; count=vote.second; }
    if(count) for(int v:group) labels[v]=best;
}
void clean(const Mesh& mesh,int* owners,double ratio,uint64_t cancel) {
    if(ratio==0) return;
    std::vector<double> areas(mesh.vertices.rows()); skin_density::areas(mesh,areas.data(),cancel);
    const double threshold=std::accumulate(areas.begin(),areas.end(),0.)*ratio;
    const auto adjacency=neighbors(mesh,cancel); std::vector<bool> seen(areas.size(),false);
    for(int first=0;first<int(areas.size());++first) {
        if(first%4096==0) check_cancel(cancel);
        if(seen[first]) continue;
        const auto group=component(first,owners,adjacency,seen,cancel); double area=0;
        for(int v:group) area+=areas[v];
        if(area<threshold) replace_component(owners,group,adjacency);
    }
}
}
