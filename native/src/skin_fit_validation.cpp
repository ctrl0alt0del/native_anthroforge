#include "skin_fit_validation.hpp"

namespace af::skin::fit {
void validate_weights(const double* data,int count,int bones) {
    Eigen::Map<const Dense> weights(data,count,bones);
    if(!weights.allFinite()||weights.minCoeff() < -1e-10||
       (weights.rowwise().sum().array()-1).abs().maxCoeff()>1e-7)
        throw std::runtime_error("Invalid fitted weight normalization.");
}
static void validate_transform(const Transform& matrix) {
    Eigen::Matrix3d linear=matrix.topLeftCorner<3,3>(),gram=linear.transpose()*linear;
    if(!matrix.allFinite()||linear.determinant()<=0)
        throw std::runtime_error("Reflected, singular or nonfinite fitted transform.");
    if((matrix.row(3)-Eigen::RowVector4d(0,0,0,1)).cwiseAbs().maxCoeff()>1e-8)
        throw std::runtime_error("Non-affine fitted transform.");
    gram.diagonal().setZero();
    if(gram.cwiseAbs().maxCoeff()>1e-7)
        throw std::runtime_error("Fitted transform contains unsupported shear.");
}
void validate_transforms(const double* matrices,int frames,int bones) {
    for(int64_t i=0;i<int64_t(frames)*bones;++i) validate_transform(Eigen::Map<const Transform>(matrices+16*i));
}
void validate_prediction(const double* vertices,int count,const double* weights,int bones,
    const double* matrices,int frames) {
    if(count<1||bones<1||bones>64||frames<2) throw std::runtime_error("Invalid fitted dimensions.");
    if(!Eigen::Map<const Vertices>(vertices,count,3).allFinite())
        throw std::runtime_error("Nonfinite fitted reference.");
    validate_weights(weights,count,bones); validate_transforms(matrices,frames,bones);
}
}
