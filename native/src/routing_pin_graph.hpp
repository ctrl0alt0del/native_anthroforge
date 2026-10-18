#pragma once
#include "routing_pin_tree.hpp"
#include <map>

namespace af::routing {
struct Component { std::vector<int> order,parents; };
using Groups=std::array<Component,2>;
using EdgeCache=std::map<std::pair<int,int>,bool>;
Groups groups(const Planning& plan,const Route& points,const Graph& graph,EdgeCache& cache);
std::vector<int> goal_indices(const Component& component);
Route goal_points(const Route& points,const std::vector<int>& indices);
Route join(const Planning& plan,const Route& points,const Groups& groups,int side,const Connection& connection);
}
