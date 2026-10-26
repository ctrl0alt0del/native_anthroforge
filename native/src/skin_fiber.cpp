// SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
// SPDX-License-Identifier: GPL-2.0-or-later
// Blender 5.0.1 curve_bevel.cc full circle and displist.cc rotateBevelPiece.
#include "skin_bevel.hpp"
#include "anthroforge/skin_capture.h"
#include "BLI_math_rotation.h"
#include "BLI_math_vector.h"
namespace af::skin {
constexpr int bevel_sides=12;
static void ring(Points& vertices,const BevelPoint& sample,float radius) {
    const float step=2.f*float(M_PI)/bevel_sides;
    float angle=-(bevel_sides-1)*step;
    for(int i=0;i<bevel_sides;++i,angle+=step) {
        float offset[3]={cosf(angle)*radius,sinf(angle)*radius,0},position[3];
        mul_qt_v3(sample.quat,offset); add_v3_v3v3(position,sample.vec,offset);
        vertices.emplace_back(position[0],position[1],position[2]);
    }
}
static Faces faces(int count,bool closed) {
    Faces result;
    for(int i=0;i<count-int(!closed);++i) {
        const int next=(i+1)%count;
        for(int j=0;j<bevel_sides;++j) {
            const int before=(j+bevel_sides-1)%bevel_sides;
            result.push_back({i*bevel_sides+j,next*bevel_sides+j,next*bevel_sides+before,i*bevel_sides+before});
        }
    }
    return result;
}
std::shared_ptr<Mesh> fiber_bevel(const Path& path,const M4& frame,double radius,uint64_t cancel) {
    if(!frame.allFinite()||!std::isfinite(radius)||radius<=0||path.parameters.size()<2)
        throw std::runtime_error("Fiber skin bevel needs finite coordinates and positive radius.");
    const auto samples=bevel_points(path,frame,cancel); Points vertices;
    vertices.reserve(samples.size()*bevel_sides);
    for(const auto& sample:samples) { check_cancel(cancel); ring(vertices,sample,float(radius)); }
    return make_mesh(vertices,faces(int(samples.size()),path.closed),cancel);
}
}
uint64_t af_skin_fiber_bevel(uint64_t handle,const double* frame,double radius,uint64_t cancel) {
    try {
        if(!frame) throw std::runtime_error("Missing skin Fiber transform.");
        return af::retain(af::skin::fiber_bevel(*af::path(handle),Eigen::Map<const af::M4>(frame),radius,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
