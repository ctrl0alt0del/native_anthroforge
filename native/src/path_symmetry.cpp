// SPDX-License-Identifier: GPL-3.0-or-later
#include "path_internal.hpp"
#include <Eigen/LU>

namespace af {
static V3 reflected_point(const M4& plane,const V3& value) {
    return plane.topLeftCorner<3,3>()*value+plane.topRightCorner<3,1>();
}
static double seam_tolerance(const Samples& samples) {
    V3 lo=samples.front().position,hi=lo;
    for(const auto& sample:samples) { lo=lo.cwiseMin(sample.position); hi=hi.cwiseMax(sample.position); }
    return 1e-8*std::max(1.,(hi-lo).norm());
}
static void require_seams(const Samples& samples,const M4& plane,double tolerance) {
    for(const auto index:{size_t(0),samples.size()-1})
        if((reflected_point(plane,samples[index].position)-samples[index].position).norm()>tolerance)
            throw std::runtime_error("Both symmetric-loop endpoints must lie on the mirror plane.");
}
static void require_half(const Samples& samples,const M4& plane,uint64_t cancel) {
    if(samples.size()<3||!plane.allFinite()||!plane.fullPivLu().isInvertible())
        throw std::runtime_error("A symmetric loop needs an invertible plane and an off-plane interior.");
    const double tolerance=seam_tolerance(samples); require_seams(samples,plane,tolerance);
    V3 side=V3::Zero();
    for(size_t i=1;i+1<samples.size();++i) {
        check_cancel(cancel); const V3 delta=reflected_point(plane,samples[i].position)-samples[i].position;
        if(delta.norm()<=tolerance) throw std::runtime_error("Symmetric-loop interior must stay off the plane.");
        if(side.norm()==0) side=delta;
        if(delta.dot(side)<=0) throw std::runtime_error("Symmetric-loop interior must stay on one side.");
    }
}
static CurveSample reflected_sample(const CurveSample& input,const M4& plane) {
    CurveSample sample=input;
    sample.position=reflected_point(plane,input.position);
    sample.tangent=-(plane.topLeftCorner<3,3>()*input.tangent).normalized();
    const V3 normal=plane.topLeftCorner<3,3>().inverse().transpose()*input.normal;
    sample.normal=(normal-sample.tangent*normal.dot(sample.tangent)).normalized();
    sample.tilt=-input.tilt; return sample;
}
static EvaluatedPath symmetric_half(const Path& input,const M4& plane,uint64_t cancel) {
    if(input.closed) throw std::runtime_error("Symmetric-loop expansion requires the open authored half.");
    EvaluatedPath result{read_samples(input.samples.data(),int(input.parameters.size())),input.parameters};
    require_half(result.samples,plane,cancel);
    const size_t count=result.samples.size(); const double end=input.parameters.back();
    if(end<=0) throw std::runtime_error("Symmetric-loop parameters must span a positive interval.");
    for(size_t i=count-2;i>0;--i) {
        check_cancel(cancel); result.samples.push_back(reflected_sample(result.samples[i],plane));
        result.parameters.push_back(end+(end-input.parameters[i])/end);
    }
    return result;
}
}
uint64_t af_path_symmetric(uint64_t handle,const double* reflection,uint64_t cancel) {
    try {
        if(!reflection) throw std::runtime_error("Symmetric-loop reflection is missing.");
        const auto input=af::path(handle); const af::M4 plane=Eigen::Map<const af::M4>(reflection);
        return af::retain_path(af::make_path(af::symmetric_half(*input,plane,cancel),true,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
