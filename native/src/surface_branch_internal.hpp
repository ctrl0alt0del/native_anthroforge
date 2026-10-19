#pragma once
#include "curve_surface_internal.hpp"

namespace af::curve_surface {
struct Branch {
    int boundary=0;
    std::vector<int> rows;
    std::vector<double> roots;
};
struct Grid {
    Points points;
    size_t rows=0,columns=0;
};
struct Assembly {
    Grid main;
    std::vector<double> along;
    Points points;
    Faces faces;
    std::vector<int64_t> material;
    bool flip=false;
};
std::vector<double> merged_stations(const Rows& rows,bool exact,int minimum,int samples);
std::vector<double> unique_stations(std::vector<double> values);
Grid sampled_grid(const Rows& rows,const std::vector<double>& along,uint64_t cancel);
Grid across_grid(const Grid& grid,const std::vector<double>& source,const std::vector<double>& target,uint64_t cancel);
std::vector<double> uniform_stations(size_t count);
std::vector<Branch> branch_inputs(const Rows& rows,int main_count,const AfSurfaceBranch* data,int count);
Assembly main_assembly(const Rows& rows,const std::vector<Branch>& branches,bool exact,int strips,int samples,uint64_t cancel);
void append_branch(Assembly& assembly,const Rows& rows,const Branch& branch,bool exact,int samples,uint64_t cancel);
void append_faces(Assembly& assembly,const std::vector<uint32_t>& mapping,size_t rows,size_t columns,bool flip);
}
