// SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
// Adapted for AnthroForge; see native/migration/BLENDER_PRIMITIVES.md.
// SPDX-License-Identifier: GPL-3.0-or-later
// Blender 5.0.1 curve.cc minimum-twist bevel frames and math_rotation_c.cc vec_to_quat.
#include "construction_internal.hpp"

namespace af {
static V3 initial_normal(const V3& direction) {
    V3 axis(-direction.y(),direction.x(),0);
    if(std::abs(direction.x())+std::abs(direction.y())<1e-4) axis=V3::UnitX();
    const Eigen::Quaterniond initial(Eigen::AngleAxisd(std::acos(std::clamp(direction.z(),-1.0,1.0)),axis.normalized()));
    const V3 up=initial.toRotationMatrix().col(2);
    const double angle=-std::atan2(-up.x(),-up.y());
    return Eigen::AngleAxisd(angle,direction)*(initial*V3::UnitX());
}
static V3 transported(const CurveSample& from,const CurveSample& to) {
    return Eigen::Quaterniond::FromTwoVectors(from.tangent,to.tangent)*from.normal;
}
static void bisectors(Samples& samples,bool closed) {
    const auto count=samples.size();
    for(size_t i=closed?0:1;i<count-(closed?0:1);++i) {
        const V3 before=samples[i].position-samples[(i+count-1)%count].position;
        const V3 after=samples[(i+1)%count].position-samples[i].position;
        const V3 sum=before.normalized()+after.normalized();
        if(sum.norm()>1e-12) samples[i].tangent=sum.normalized();
    }
}
static void close_twist(Samples& samples) {
    const auto count=samples.size(); const auto& last=samples.back();
    const V3 aligned=transported(samples[count-2],last);
    const double angle=-std::atan2(last.tangent.dot(last.normal.cross(aligned)),last.normal.dot(aligned));
    for(size_t step=0;step<count;++step) {
        auto& sample=samples[(step+count-1)%count];
        sample.normal=Eigen::AngleAxisd(angle*(step+1)/count,sample.tangent)*sample.normal;
    }
}
static void propagate_frames(Samples& samples,bool closed) {
    samples.back().normal=initial_normal(samples.back().tangent);
    for(size_t i=0;i+1<samples.size();++i)
        samples[i].normal=i==0&&!closed?initial_normal(samples[i].tangent):transported(samples[(i+samples.size()-1)%samples.size()],samples[i]);
    if(closed) close_twist(samples);
    else {
        samples.front().normal=transported(samples[1],samples.front());
        samples.back().normal=transported(samples[samples.size()-2],samples.back());
    }
}
void curve_frames(Samples& samples,bool closed,uint64_t cancel) {
    check_cancel(cancel); bisectors(samples,closed); propagate_frames(samples,closed);
    for(auto& sample:samples)
        sample.normal=Eigen::AngleAxisd(sample.tilt,sample.tangent)*sample.normal;
    check_cancel(cancel);
}
}
