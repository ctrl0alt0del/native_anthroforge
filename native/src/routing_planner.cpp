#include "routing_planner.hpp"

namespace af::routing {
static bool owner_inside(const Planning& plan,Vec point,int owner) {
    if(!owner) return false;
    const auto nearest=kernel::af_nearest_world(*plan.world.collision,point);
    if(nearest.instance<0) return false;
    const auto& item=plan.world.collision->items[nearest.instance];
    return item.owner==owner&&kernel::af_inside_instance(item,point);
}
static bool owner_chord(const Planning& plan,Vec a,Vec b,int first,int last) {
    const Vec delta=kernel::sub(b,a); const double length=std::max(kernel::norm(delta),1e-12);
    const double low=first?plan.span/length:0,high=last?1-plan.span/length:1;
    if(low>=high) return false;
    const double offset=std::min((high-low)*0.1,std::max(1e-9,plan.threshold/length));
    return owner_inside(plan,kernel::add(a,kernel::mul(delta,low+offset)),first)||
           owner_inside(plan,kernel::add(a,kernel::mul(delta,high-offset)),last);
}
bool clear(const Planning& plan,Vec a,Vec b,int first,int last) {
    check_cancel(plan.input.cancel); const Vec points[]{a,b}; const int64_t edge[]{0,1};
    int allowed=0,blocker=-1; double minimum=0; kernel::AfBatchResult result{};
    kernel::af_world_validate_edges(plan.world.collision.get(),reinterpret_cast<const double*>(points),
        edge,&first,&last,1,plan.span,plan.threshold,&allowed,&blocker,&minimum,&result);
    return allowed&&!owner_chord(plan,a,b,first,last);
}
Route shortcut(const Planning& plan,const Route& route) {
    if(route.empty()) return {};
    Route output{route.front()}; size_t current=0;
    while(current+1<route.size()) {
        size_t next=route.size()-1;
        while(next>current+1&&!clear(plan,route[current],route[next],current==0?plan.first:0,
                                   next+1==route.size()?plan.last:0)) --next;
        output.push_back(route[next]); current=next;
    }
    return output;
}
static void graph_row(const Route& points,int index,int limit,std::vector<int64_t>& links) {
    const int count=int(points.size());
    if(limit>=count) { for(int j=0;j<count;++j) if(j!=index) links.push_back(j); return; }
    std::vector<int> order(count); std::iota(order.begin(),order.end(),0);
    std::stable_sort(order.begin(),order.end(),[&](int a,int b) {
        return kernel::norm(kernel::sub(points[a],points[index]))<kernel::norm(kernel::sub(points[b],points[index]));
    });
    links.push_back(1); links.push_back(0); int used=0;
    for(int j:order) if(j!=index&&used++<limit&&j>1) links.push_back(j);
}
Graph neighbors(const Route& points,int limit) {
    Graph graph(points.size());
    for(int i=0;i<int(points.size());++i) graph_row(points,i,limit,graph[i]);
    return graph;
}
Route search(const Planning& plan,const Route& points,int limit) {
    return shortcut(plan,search_graph(plan,points,neighbors(points,limit)));
}
static Route corridor(const Planning& plan) {
    if(clear(plan,plan.start,plan.end,plan.first,plan.last)) return {plan.start,plan.end};
    const auto surface=surface_route(plan);
    if(!surface.empty()) return surface;
    return ordinary_roadmap(plan);
}
static std::vector<Route> corridors(const Input& input,const World& world,const Reference& reference) {
    std::vector<Route> routes;
    for(size_t i=1;i<reference.pins.size();++i) {
        Planning plan{world,input,input.owners[i-1],input.owners[i%input.count],
            reference.points[reference.pins[i-1]],reference.points[reference.pins[i]],
            std::max(2.5*input.options.radius,1e-7),input.options.radius-world.slack};
        if(!clear(plan,plan.start,plan.start,plan.first,plan.first)||!clear(plan,plan.end,plan.end,plan.last,plan.last))
            throw std::runtime_error("A structural routing point intersects an unrelated surface.");
        auto route=corridor(plan); if(route.empty()) return {};
        routes.push_back(std::move(route));
    }
    return routes;
}
void prepare_routes(const Input& input,const World& world,const Reference& reference,std::vector<Span>& spans) {
    const auto routes=handoff(corridors(input,world,reference),input,world);
    if(routes.empty()) return; // Production SQP still attempts feasibility from the direct reference.
    for(size_t i=0;i<routes.size();++i) {
        auto points=resample(routes[i],int(reference.pins[i+1]-reference.pins[i])+1);
        if(!input.options.closed) spans[i].seed=std::move(points);
        else std::copy(points.begin(),points.end(),spans.front().seed.begin()+reference.pins[i]);
    }
}
}
