#pragma once
#include "mesh_internal.hpp"

namespace af::skin::fit {
using Dense=Eigen::Matrix<double,Eigen::Dynamic,Eigen::Dynamic,Eigen::RowMajor>;
using Transform=Eigen::Matrix<double,4,4,Eigen::RowMajor>;
void validate_weights(const double* weights,int count,int bones);
void validate_transforms(const double* transforms,int frames,int bones);
void validate_prediction(const double* vertices,int count,const double* weights,int bones,
    const double* matrices,int frames);
}
