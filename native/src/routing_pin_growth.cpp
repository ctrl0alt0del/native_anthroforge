#include "routing_pin_tree.hpp"

namespace af::routing {
static Route targets(PinTree& tree,int batch) {
    const double ranges[]{8,16,32,64}; const double distance=ranges[std::min(batch/32,3)]*tree.scale;
    Route values;
    for(int i=0;i<32;++i) {
        const Vec delta{tree.random.uniform(distance),tree.random.uniform(distance),tree.random.uniform(distance)};
        values.push_back(kernel::add(tree.origin,delta));
    }
    for(int i=0;i<32;i+=4) values[i]=tree.goals[tree.random.index(uint32_t(tree.goals.size()))];
    return values;
}
static int nearest_parent(const PinTree& tree,Vec target) {
    int parent=-1; double best=INFINITY;
    for(size_t i=0;i<tree.points.size();++i) {
        const double distance=kernel::norm(kernel::sub(tree.points[i],target));
        if(distance<=tree.domains[i]&&distance<best) { best=distance; parent=int(i); }
    }
    return parent;
}
static std::vector<int> grow(PinTree& tree,int batch) {
    const double steps[]{.5,1,2,4}; Route candidates; std::vector<int> parents;
    for(Vec target:targets(tree,batch)) {
        const int parent=nearest_parent(tree,target); if(parent<0) continue;
        const Vec delta=kernel::sub(target,tree.points[parent]);
        const double step=tree.scale*((parent==0&&tree.owner)?2.5:steps[parents.size()%4]);
        const double factor=std::min(1.0,step/std::max(kernel::norm(delta),1e-15));
        candidates.push_back(kernel::add(tree.points[parent],kernel::mul(delta,factor))); parents.push_back(parent);
    }
    return accept(tree,parents,candidates);
}
static Connection assemble(const PinTree& tree,const PinTree& forest,int a,int b) {
    int root=b;
    while(forest.parents[root]!=-1) root=forest.parents[root];
    auto path=tree_path(tree,a); const auto other=tree_path(forest,b);
    path.insert(path.end(),other.rbegin(),other.rend()-1);
    return {path,root};
}
Connection grow_pair(PinTree& tree,PinTree& forest,int batch) {
    for(bool reverse:{false,true}) {
        auto& active=reverse?forest:tree; auto& other=reverse?tree:forest;
        if(other.points.size()>1) active.goals={other.points.begin()+1,other.points.end()};
        const auto added=grow(active,batch);
        const auto [first,second]=connect(active,other.points,added,int(bool(other.owner)));
        if(first>=0) return reverse?assemble(tree,forest,second,first):assemble(tree,forest,first,second);
    }
    return {};
}
}
