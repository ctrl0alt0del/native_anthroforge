#pragma once
#include "path_internal.hpp"
#include "anthroforge/curve_surface.h"

namespace af::curve_surface {
constexpr size_t max_stations=16384,max_vertices=262144,max_triangles=524288;
struct Row {
    Points points;
    std::vector<double> parameters;
    std::vector<double> material_stations;
    bool closed=false;
    double extent=0;
    int direction=1;
};
using Rows=std::vector<Row>;
void budget(size_t vertices,size_t triangles);
std::vector<double> stations(const Row& row);
std::vector<double> unique_stations(std::vector<double> values);
V3 sample(const Row& row,const std::vector<double>& positions,double factor);
Rows inputs(const AfSurfaceRow* rows,int count,bool exact,uint64_t cancel);
Rows common_stations(const Rows& rows,uint64_t cancel);
std::vector<int> density(const Rows& rows,int strips,bool exact);
void align(Rows& rows,double* output,uint64_t cancel);
std::shared_ptr<Mesh> loft(const Rows& rows,const int* across,bool close_across,bool flip,uint64_t cancel);
std::shared_ptr<Mesh> patch(const Row& row,int resolution,bool flip,uint64_t cancel);
}
