// SPDX-FileCopyrightText: 2005 Blender Authors
// Adapted for AnthroForge; see native/migration/BLENDER_PRIMITIVES.md.
// SPDX-License-Identifier: GPL-3.0-or-later
// Hook falloff and coordinate-space formulas: Blender 5.0.1 MOD_hook.cc.
#include "construction_internal.hpp"

namespace af {
static double custom_falloff(double x,const double* points,int count) {
    if(count<2) return x;
    int low=1,high=count-1;
    while(low<high) { const int middle=(low+high)/2; if(points[2*middle]<x) low=middle+1; else high=middle; }
    for(int i=low;i<count;++i) {
        const double a=points[2*(i-1)],b=points[2*i];
        if(x<=b) {
            const double t=b>a?std::clamp((x-a)/(b-a),0.0,1.0):0;
            return (1-t)*points[2*(i-1)+1]+t*points[2*i+1];
        }
    }
    return points[2*(count-1)+1];
}
static double falloff_shape(double factor,int kind,const double* custom,int count) {
    switch(kind) {
        case 1:return custom_falloff(factor,custom,count);
        case 2:return factor*factor*(3-2*factor);
        case 3:return std::sqrt(2*factor-factor*factor);
        case 4:return std::sqrt(factor);
        case 5:return factor*factor;
        default:return factor;
    }
}
static double hook_weight(const V3& distance,double radius,int kind,const double* custom,int count) {
    if(kind==0||radius==0) return 1;
    const double squared=distance.squaredNorm()/(radius*radius);
    if(squared>1) return 0;
    if(squared==0||kind==7) return 1;
    if(kind==8) return 1-squared;
    return falloff_shape(1-std::sqrt(squared),kind,custom,count);
}
}
int af_hook(double* points,int count,const double* matrix,const double* uniform,const double* center,
            double strength,double radius,int falloff,const double* weights,const double* custom,
            int custom_count,uint64_t cancel) {
    try {
        const af::M4 transform=Eigen::Map<const af::M4>(matrix),space=Eigen::Map<const af::M4>(uniform);
        for(int i=0;i<count;++i) {
            if(i%1024==0) af::check_cancel(cancel);
            Eigen::Map<af::V3> p(points+3*i);
            const af::V3 distance=space.topLeftCorner<3,3>()*(p-af::V3(center));
            const double w=strength*(weights?weights[i]:1)*af::hook_weight(distance,radius,falloff,custom,custom_count);
            p+=w*(af::point(transform,p)-p);
        }
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
