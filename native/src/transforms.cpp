#include "mesh_internal.hpp"

namespace af {
V3 point(const M4& matrix,const V3& value) { return matrix.block<3,3>(0,0)*value+matrix.block<3,1>(0,3); }
V3 scales(const M4& matrix) {
    V3 value;
    for(int i=0;i<3;++i) value[i]=matrix.block<3,1>(0,i).norm();
    // Blender decomposes a reflected basis with all three scales negative.
    if(matrix.block<3,3>(0,0).determinant()<0) value*=-1;
    return value;
}
M3 rotation(const M4& matrix) {
    const V3 scale=scales(matrix);
    if(scale.cwiseAbs().minCoeff()<1e-12) throw std::runtime_error("Zero scale is not supported.");
    return matrix.block<3,3>(0,0)*scale.cwiseInverse().asDiagonal();
}
M4 geometry_matrix(const double* matrix,const double* offset) {
    M4 value=Eigen::Map<const M4>(matrix);
    value.block<3,1>(0,3)=point(value,Eigen::Map<const V3>(offset));
    return value;
}
}
int af_transform(const double* trs,double* matrix) {
    try {
        Eigen::Map<af::M4> output(matrix); output.setIdentity();
        const Eigen::Map<const af::V3> translation(trs), angles(trs+3), scale(trs+6);
        if(!translation.allFinite()||!angles.allFinite()||!scale.allFinite()||scale.cwiseAbs().minCoeff()<1e-12)
            throw std::runtime_error("Transform must be finite with nonzero scale.");
        const double radians=3.141592653589793/180.;
        auto rotation=Eigen::AngleAxisd(angles.z()*radians,af::V3::UnitZ())*
            Eigen::AngleAxisd(angles.y()*radians,af::V3::UnitY())*Eigen::AngleAxisd(angles.x()*radians,af::V3::UnitX());
        output.block<3,3>(0,0)=rotation.toRotationMatrix()*scale.asDiagonal();
        output.block<3,1>(0,3)=translation; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_decompose(const double* matrix,double* trs) {
    try {
        const af::M4 value=Eigen::Map<const af::M4>(matrix);
        Eigen::Map<af::V3> translation(trs), angles(trs+3), scale(trs+6);
        translation=value.block<3,1>(0,3); scale=af::scales(value);
        const af::V3 zyx=af::rotation(value).eulerAngles(2,1,0);
        angles=af::V3(zyx.z(),zyx.y(),zyx.x())*(180./3.141592653589793); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_point(const double* matrix,const double* point,double* output) {
    Eigen::Map<af::V3> result(output);
    result=af::point(Eigen::Map<const af::M4>(matrix),Eigen::Map<const af::V3>(point));
    return result.allFinite()?0:1;
}
int af_quaternion(const double* matrix,double* output) {
    try {
        const Eigen::Quaterniond value(af::rotation(Eigen::Map<const af::M4>(matrix)));
        output[0]=value.w(); output[1]=value.x(); output[2]=value.y(); output[3]=value.z(); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_geometry_matrix(const double* matrix,const double* offset,double* output) {
    Eigen::Map<af::M4> result(output); result=af::geometry_matrix(matrix,offset); return 0;
}
int af_axis_rotation(const double* axis,double angle,double* output) {
    try {
        const af::V3 direction=Eigen::Map<const af::V3>(axis);
        if(!direction.allFinite()||direction.norm()<1e-12||!std::isfinite(angle))
            throw std::runtime_error("Rotation requires a finite angle and nonzero axis.");
        const af::M3 rotation=Eigen::AngleAxisd(angle*3.141592653589793/180.,direction.normalized()).toRotationMatrix();
        const af::V3 zyx=rotation.eulerAngles(2,1,0);
        Eigen::Map<af::V3> result(output);
        result=af::V3(zyx.z(),zyx.y(),zyx.x())*(180./3.141592653589793); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_move_origin(const double* matrix,const double* offset,const double* binding,
                   double* updated_matrix,double* updated_offset) {
    const af::M4 value=Eigen::Map<const af::M4>(matrix);
    const af::V3 anchor=Eigen::Map<const af::V3>(binding+18);
    Eigen::Map<af::M4> output(updated_matrix); output=value;
    output.block<3,1>(0,3)=af::point(value,anchor);
    Eigen::Map<af::V3> local(updated_offset); local=Eigen::Map<const af::V3>(offset)-anchor;
    return 0;
}
