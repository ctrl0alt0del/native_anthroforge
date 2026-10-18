#include "routing_planner.hpp"

namespace af::routing {
static Route projected(const Planning& plan,double factor) {
    const Vec delta=kernel::sub(plan.end,plan.start); const double radius=plan.input.options.radius;
    const int count=std::clamp(int(std::ceil(kernel::norm(delta)/std::max(8*radius,1e-6))),8,32);
    Route result{plan.start}; const auto& item=plan.world.collision->items[plan.first-1];
    for(int i=1;i<count;++i) {
        check_cancel(plan.input.cancel); const Vec point=kernel::add(plan.start,kernel::mul(delta,double(i)/count));
        kernel::AfNearest nearest{{},{},INFINITY,-1}; kernel::af_nearest_item(item,0,point,nearest);
        const bool inside=kernel::af_inside_instance(item,point);
        Vec normal=kernel::af_unit(inside?kernel::sub(nearest.point,point):kernel::sub(point,nearest.point));
        if(kernel::norm(normal)<=kernel::eps()) normal=kernel::af_unit(nearest.face_normal);
        result.push_back(kernel::add(nearest.point,kernel::mul(normal,radius*factor)));
    }
    result.push_back(plan.end); unique_adjacent(result); return result;
}
bool route_clear(const Planning& plan,const Route& route) {
    if(route.size()<2) return false;
    for(size_t i=1;i<route.size();++i)
        if(!clear(plan,route[i-1],route[i],i==1?plan.first:0,i+1==route.size()?plan.last:0)) return false;
    return true;
}
Route surface_route(const Planning& plan) {
    if(!plan.first||plan.first!=plan.last) return {};
    for(double factor:{1.25,1.75,2.5,4.0,8.0}) {
        const auto route=projected(plan,factor);
        if(route_clear(plan,route)) return shortcut(plan,route);
    }
    return mesh_surface_route(plan);
}
}
