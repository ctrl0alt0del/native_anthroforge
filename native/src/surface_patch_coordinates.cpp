// SPDX-License-Identifier: GPL-3.0-or-later
// Projected material positions and retained perimeter parameters; geometry is untouched.
#include "surface_patch_internal.hpp"

namespace af::curve_surface {
static double boundary_parameter(const PatchKey& key,const std::vector<double>& stations,int resolution) {
    const int count=int(stations.size())-1;
    if(key[0]==0) return key[1]<count?stations[size_t(key[1])]:-1;
    if(key[0]!=1) return -1;
    const auto a=key[1],b=key[2]; const double t=double(key[3])/resolution;
    if(b-a==1) return (1-t)*stations[size_t(a)]+t*stations[size_t(b)];
    if(a==0&&b==count-1) return t*stations[size_t(b)]+(1-t);
    return -1;
}
void patch_coordinates(Patch& patch,const Row& row,int resolution,uint64_t cancel) {
    const auto frame=projection(row.points); const auto positions=stations(row);
    double scale=0;
    for(const auto& p:row.points) scale=std::max(scale,(p-frame.origin).norm());
    if(scale<1e-12) throw std::runtime_error("Patch material boundary is degenerate.");
    for(size_t i=0;i<patch.points.size();++i) {
        check_cancel(cancel);
        const V3 offset=(patch.points[i]-frame.origin)/scale;
        patch.coordinates.emplace_back(offset.dot(frame.first),offset.dot(frame.second),boundary_parameter(patch.keys[i],positions,resolution));
    }
}
}
