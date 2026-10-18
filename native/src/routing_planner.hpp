#pragma once
#include "routing_internal.hpp"

namespace af::routing {
using Route=std::vector<Vec>;
struct Planning {
    World& world;
    const Input& input;
    int first,last;
    Vec start,end;
    double span,threshold;
};
bool clear(const Planning& plan,Vec a,Vec b,int first=0,int last=0);
Route shortcut(const Planning& plan,const Route& route);
Route compatibility(const Planning& plan);
Route search(const Planning& plan,const Route& points,int limit);
Route surface_route(const Planning& plan);
void unique_adjacent(Route& points);
Route sampled(const Route& points,int count);
Route bounds_shell(const kernel::Bounds& bounds,double padding,bool dense);
Route resample(const Route& points,int count);
std::vector<Route> handoff(std::vector<Route> routes,const Input& input,World& world);
void prepare_routes(const Input& input,World& world,const Reference& reference,std::vector<Span>& spans);
}
