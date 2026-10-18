#pragma once
#include "routing_internal.hpp"

namespace af::routing {
using Route=std::vector<Vec>;
using Graph=std::vector<std::vector<int64_t>>;
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
Route roadmap_candidates(const Planning& plan,bool dense);
std::vector<const kernel::AfInstance*> nearby_colliders(const Planning& plan,bool dense);
Route collider_shell(const Planning& plan,const kernel::AfInstance& item,bool dense);
double line_distance(Vec point,Vec start,Vec end);
Route rank_points(Route points,Vec start,Vec end,int limit);
Route search(const Planning& plan,const Route& points,int limit);
Route search_graph(const Planning& plan,const Route& points,const Graph& graph);
Graph neighbors(const Route& points,int limit);
Route ordinary_roadmap(const Planning& plan);
Route access_points(const Planning& plan,bool oblique);
void append_unique(Route& points,const Route& additions);
Graph extend_graph(const Planning& plan,const Route& points,const Graph& original);
void filter_anchors(const Planning& plan,const Route& points,Graph& graph);
Route surface_route(const Planning& plan);
Route mesh_surface_route(const Planning& plan);
bool route_clear(const Planning& plan,const Route& route);
Route surface_vertices(const kernel::AfInstance& item);
Route vertex_normals(const Route& points,const std::vector<int64_t>& triangles);
double route_length(const Route& route);
void unique_adjacent(Route& points);
Route sampled(const Route& points,int count);
Route bounds_shell(const kernel::Bounds& bounds,double padding,bool dense);
Route resample(const Route& points,int count);
std::vector<Route> handoff(std::vector<Route> routes,const Input& input,World& world);
void prepare_routes(const Input& input,World& world,const Reference& reference,std::vector<Span>& spans);
}
