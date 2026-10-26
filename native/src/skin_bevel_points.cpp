// SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
// SPDX-License-Identifier: GPL-2.0-or-later
// Blender 5.0.1 curve.cc: polyline capture, duplicate removal and endpoint directions.
#include "skin_bevel.hpp"
#include "BLI_math_vector.h"
namespace af::skin {
static void ends(BevelPoints& points) {
    sub_v3_v3v3(points.front().dir,points[1].vec,points.front().vec);
    sub_v3_v3v3(points.back().dir,points.back().vec,points[points.size()-2].vec);
    normalize_v3(points.front().dir); normalize_v3(points.back().dir);
}
static BevelPoints unique_points(const BevelPoints& points,bool closed) {
    std::vector<bool> remove(points.size());
    const size_t first=closed?points.size()-1:0;
    for(size_t step=0;step+1<points.size();++step) {
        const auto i=(first+step)%points.size(),j=(i+1)%points.size();
        remove[i]=compare_v3v3(points[i].vec,points[j].vec,.00001f/12);
    }
    BevelPoints output;
    for(size_t i=0;i<points.size();++i) if(!remove[i]) output.push_back(points[i]);
    return output;
}
BevelPoints bevel_points(const Path& path,const M4& frame,uint64_t cancel) {
    BevelPoints input(path.parameters.size());
    for(size_t i=0;i<input.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        const V3 position=point(frame,V3(path.samples.data()+11*i));
        for(int axis=0;axis<3;++axis) input[i].vec[axis]=float(position[axis]);
    }
    if(!path.closed) ends(input);
    auto output=unique_points(input,path.closed);
    if(output.size()<2) throw std::runtime_error("Fiber skin bevel needs two distinct points.");
    bevel_frames(output,path.closed);
    return output;
}
}
