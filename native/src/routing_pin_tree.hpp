#pragma once
#include "routing_planner.hpp"
#include "routing_random.hpp"
#include <functional>
#include <set>

namespace af::routing {
using PointKey=std::array<double,3>;
using EdgeCheck=std::function<bool(Vec,Vec,int,int)>;
struct Connection { Route path; int goal=-1; };
struct PinTree {
    Vec origin;
    int owner;
    Route goals,points;
    EdgeCheck check;
    double scale;
    std::vector<int> parents;
    std::vector<double> domains;
    std::set<PointKey> seen;
    Random random;
    PinTree(Vec origin,int owner,Route goals,EdgeCheck check,double scale,bool forest=false);
};
PointKey point_key(Vec point);
std::vector<int> accept(PinTree& tree,const std::vector<int>& parents,const Route& candidates);
std::vector<int> initial_exits(PinTree& tree,int directions=2048);
Route tree_path(const PinTree& tree,int node);
std::pair<int,int> connect(const PinTree& tree,const Route& goals,const std::vector<int>& added,int skip=0);
Connection connect_goals(const PinTree& tree,const std::vector<int>& added);
PinTree goal_forest(const PinTree& tree);
Connection grow_pair(PinTree& tree,PinTree& forest,int batch);
Route pin_recovery(const Planning& plan,Route points,Graph graph);
}
