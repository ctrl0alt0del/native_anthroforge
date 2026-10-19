#include "routing_planner.hpp"
#include "path_contacts.hpp"

namespace af::routing {
struct Handoff {
    Route points;
    std::vector<int> pins;
    std::vector<double> lengths;
    std::map<int,PathContacts> contacts;
};
static Handoff joined(const std::vector<Route>& routes,bool closed) {
    Handoff result;
    for(const auto& route:routes) {
        result.pins.push_back(int(result.points.size()));
        result.points.insert(result.points.end(),route.begin(),route.end()-1);
        for(size_t i=1;i<route.size();++i) result.lengths.push_back(kernel::norm(kernel::sub(route[i],route[i-1])));
    }
    if(!closed) { result.pins.push_back(int(result.points.size())); result.points.push_back(routes.back().back()); }
    return result;
}
static void contacts(Handoff& path,const Input& input) {
    const double span=std::max(2.5*input.options.radius,1e-7);
    for(int i=0;i<input.count;++i) {
        check_cancel(input.cancel);
        if(input.owners[i]) add_contact(path.contacts[input.owners[i]],path.lengths,path.pins[i],span,input.options.closed);
    }
}
static bool node_clear(const kernel::AfInstance& item,Vec point,double threshold) {
    return kernel::af_instance_validation_row(item,point,point,0,0,0,threshold).clear!=0;
}
static bool edge_clear(const kernel::AfInstance& item,Vec a,Vec b,const Intervals& intervals,double threshold) {
    const Vec delta=kernel::sub(b,a);
    for(const auto& [low,high]:intervals) {
        const Vec start=kernel::add(a,kernel::mul(delta,low)),end=kernel::add(a,kernel::mul(delta,high));
        kernel::AfBatchResult result{0,0,0,0,INFINITY};
        if(!kernel::af_instance_clear(item,start,end,0,0,0,threshold,result)) return false;
    }
    return true;
}
static bool instance_clear(const Handoff& path,const kernel::AfInstance& item,const Input& input,double threshold) {
    const PathContacts empty; const auto found=path.contacts.find(item.owner);
    const auto& contact=found==path.contacts.end()?empty:found->second;
    for(int i=0;i<int(path.points.size());++i) {
        check_cancel(input.cancel);
        if(!contact.nodes.count(i)&&!node_clear(item,path.points[i],threshold)) return false;
        if(i<int(path.lengths.size())&&!edge_clear(item,path.points[i],path.points[(i+1)%path.points.size()],
                                                 tested_intervals(contact,i),threshold)) return false;
    }
    return true;
}
bool valid_handoff(const std::vector<Route>& routes,const Input& input,World& world,bool clearance) {
    if(routes.empty()) return false;
    auto path=joined(routes,input.options.closed); contacts(path,input);
    const double threshold=clearance?std::max(0.0,input.options.radius-world.slack):0.0;
    for(const auto& item:world.collision->items)
        if(!instance_clear(path,item,input,threshold)) return false;
    return true;
}
}
