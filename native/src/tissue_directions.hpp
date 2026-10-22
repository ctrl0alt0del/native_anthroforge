// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "tissue_inflation.hpp"
#include <Eigen/SparseCore>

namespace af::tissue {
struct DirectionOperators {
    Eigen::SparseMatrix<double> stiffness,mass;
    Vertices normals;
};
DirectionOperators prepare_directions(const Mesh& source,const MaterialGrid& grid,uint64_t cancel);
Vertices solve_directions(const DirectionOperators& prepared,double distance,uint64_t cancel);
Vertices inflation_directions(const Mesh& source,const MaterialGrid& grid,double distance,uint64_t cancel);
}
