// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "mesh_internal.hpp"

namespace af {
struct MaterialGrid {
    int rows=0,columns=0;
    bool closed_u=false,closed_v=false;
    std::vector<int64_t> indices;
    std::vector<double> across,along;
};
std::vector<int64_t> grid_material(int rows,int columns,bool closed_u,bool closed_v);
void append_material_grid(std::vector<int64_t>& data,const std::vector<uint32_t>& indices,size_t rows,size_t columns);
std::vector<MaterialGrid> material_grids(const std::vector<int64_t>& data,int64_t vertices);
std::vector<MaterialGrid> material_grids(const Mesh& mesh);
}
