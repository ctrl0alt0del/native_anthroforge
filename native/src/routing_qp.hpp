#pragma once
#include "routing_internal.hpp"
#include <Eigen/SparseCore>

namespace af::routing::qp {
using Sparse=Eigen::SparseMatrix<double>;
using Vector=Eigen::VectorXd;
using Triplet=Eigen::Triplet<double>;
struct Problem { Sparse P,A,G; Vector q,b,lower,upper; };
Problem problem(kernel::AfV3SqpState& state);
}
