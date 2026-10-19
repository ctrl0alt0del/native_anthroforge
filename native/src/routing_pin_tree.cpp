#include "routing_pin_tree.hpp"

namespace af::routing {
PointKey point_key(Vec p) {
    return {std::nearbyint(p.x*1e10)/1e10,std::nearbyint(p.y*1e10)/1e10,std::nearbyint(p.z*1e10)/1e10};
}
PinTree::PinTree(Vec point,int role,Route targets,EdgeCheck validate,double size,bool forest)
    :origin(point),owner(role),goals(std::move(targets)),points{point},check(std::move(validate)),
     scale(size),parents{-1},domains{INFINITY},seen{point_key(point)},random(forest) {}
static void append(PinTree& tree,int parent,Vec point,std::vector<int>& added) {
    if(!tree.seen.insert(point_key(point)).second) return;
    added.push_back(int(tree.points.size())); tree.points.push_back(point);
    tree.parents.push_back(parent); tree.domains.push_back(INFINITY);
}
std::vector<int> accept(PinTree& tree,const std::vector<int>& parents,const Route& candidates) {
    std::vector<int> added; std::vector<bool> passed(candidates.size());
    for(size_t i=0;i<candidates.size();++i) passed[i]=tree.check(candidates[i],candidates[i],0,0);
    for(size_t i=0;i<candidates.size();++i) {
        const int parent=parents[i],owner=parent==0?tree.owner:0;
        if(passed[i]) passed[i]=tree.check(tree.points[parent],candidates[i],owner,0);
        if(!passed[i]) tree.domains[parent]=8*tree.scale;
    }
    for(size_t i=0;i<candidates.size();++i) if(passed[i]) append(tree,parents[i],candidates[i],added);
    return added;
}
std::vector<int> initial_exits(PinTree& tree,int count) {
    Route directions,candidates;
    for(int i=0;i<count;++i) {
        const double z=1-2*(i+.5)/count,angle=i*std::acos(-1.0)*(3-std::sqrt(5.0));
        const double radial=std::sqrt(1-z*z);
        directions.push_back({radial*std::cos(angle),radial*std::sin(angle),z});
    }
    for(double factor:{2.0,2.5,4.0}) for(Vec direction:directions)
        candidates.push_back(kernel::add(tree.origin,kernel::mul(kernel::mul(direction,tree.scale),factor)));
    return accept(tree,std::vector<int>(candidates.size(),0),candidates);
}
Route tree_path(const PinTree& tree,int node) {
    Route path;
    for(int i=node;i>=0;i=tree.parents[i]) path.push_back(tree.points[i]);
    std::reverse(path.begin(),path.end()); return path;
}
static std::vector<int> nearest(const Route& goals,Vec point,int skip) {
    std::vector<int> order(goals.size()-skip); std::iota(order.begin(),order.end(),skip);
    std::stable_sort(order.begin(),order.end(),[&](int a,int b) {
        return kernel::norm(kernel::sub(goals[a],point))<kernel::norm(kernel::sub(goals[b],point));
    });
    order.resize(std::min(size_t(32),order.size())); return order;
}
std::pair<int,int> connect(const PinTree& tree,const Route& goals,const std::vector<int>& added,int skip) {
    for(int node:added) for(int target:nearest(goals,tree.points[node],skip))
        if(tree.check(tree.points[node],goals[target],0,0)) return {node,target};
    return {-1,-1};
}
Connection connect_goals(const PinTree& tree,const std::vector<int>& added) {
    const auto [node,goal]=connect(tree,tree.goals,added);
    return node<0?Connection{}:Connection{tree_path(tree,node),goal};
}
PinTree goal_forest(const PinTree& tree) {
    PinTree forest(tree.origin,0,tree.goals,tree.check,tree.scale,true);
    forest.points=tree.goals; forest.parents.assign(forest.points.size(),-1);
    forest.domains.assign(forest.points.size(),INFINITY); forest.seen.clear();
    for(Vec point:forest.points) forest.seen.insert(point_key(point));
    if(tree.points.size()>1) forest.goals={tree.points.begin()+1,tree.points.end()};
    return forest;
}
}
