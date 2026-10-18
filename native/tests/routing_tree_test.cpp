#include "routing_pin_tree.hpp"
#include <fstream>
#include <iostream>

using namespace af::routing;
static bool box_clear(Vec a,Vec b,int,int) {
    const double low[]{.035,-1,-1},high[]{.085,.10,1};
    const Vec delta=kernel::sub(b,a); double enter=0,leave=1;
    for(int i=0;i<3;++i) {
        const double start=(&a.x)[i],direction=(&delta.x)[i];
        if(std::abs(direction)<1e-15) { if(start<low[i]||start>high[i]) return true; continue; }
        const double first=(low[i]-start)/direction,last=(high[i]-start)/direction;
        enter=std::max(enter,std::min(first,last)); leave=std::min(leave,std::max(first,last));
    }
    return enter>leave;
}
static Connection solve(PinTree& tree) {
    auto result=connect_goals(tree,initial_exits(tree,128));
    if(result.goal>=0) return result;
    auto forest=goal_forest(tree);
    for(int batch=0;batch<64;++batch) {
        result=grow_pair(tree,forest,batch);
        if(result.goal>=0) return result;
    }
    return {};
}
static bool same_point(std::istream& input,Vec point) {
    Vec expected{}; input>>expected.x>>expected.y>>expected.z;
    return input.good()&&kernel::norm(kernel::sub(expected,point))<1e-13;
}
static bool matches(std::istream& input,const PinTree& tree,const Connection& result) {
    size_t nodes=0,count=0; int goal=-1;
    input>>nodes>>count>>goal;
    if(nodes!=tree.points.size()||count!=result.path.size()||goal!=result.goal) return false;
    for(size_t i=0;i<nodes;++i) {
        if(!same_point(input,tree.points[i])) return false;
        int parent=-2; input>>parent; if(parent!=tree.parents[i]) return false;
    }
    for(Vec point:result.path) if(!same_point(input,point)) return false;
    return true;
}
int main(int count,char** args) {
    if(count!=2) return 2;
    PinTree tree({0,0,0},1,{{.12,0,0}},box_clear,.01);
    const auto result=solve(tree); std::ifstream reference(args[1]);
    if(!matches(reference,tree,result)) {
        std::cerr<<"Pin tree differs: "<<tree.points.size()<<" nodes, "<<result.path.size()<<" path points.\n";
        return 1;
    }
    std::cout<<"Pinned addon tree: all nodes, parent identities and path agree.\n";
    return 0;
}
