// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <Eigen/Core>
#include <atomic>
#include <vector>

namespace af::boolean {
using Vertices=Eigen::Matrix<double,Eigen::Dynamic,3,Eigen::RowMajor>;
using Triangles=Eigen::Matrix<int,Eigen::Dynamic,3,Eigen::RowMajor>;
struct Exterior { Vertices vertices; Triangles faces; Eigen::VectorXi origins; };
Exterior exterior(const Vertices& vertices,const Triangles& faces,const std::atomic<bool>* cancel);
}
