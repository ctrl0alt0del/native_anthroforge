// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_shapes.hpp"
#include "../migration/tissue/unit_spheres.hpp"

namespace af::tissue {
template<size_t N,size_t F>
static std::shared_ptr<Mesh> radial_mesh(const double (&p)[N][3],const int64_t (&f)[F][3],const M4& frame,const AfTissueShape& s,uint64_t cancel) {
    Points points; Faces faces; const V3 scales=V3(s.scale)*(s.enabled?s.amount:0);
    for(const auto& v:p) { check_cancel(cancel); points.push_back(point(frame,V3(v).cwiseProduct(scales))); }
    for(const auto& face:f) faces.push_back({face[0],face[1],face[2]});
    auto result=make_mesh(points,faces,cancel,true);
    result->tissue=tissue_identity(1,N,F); result->tissue.source_count=1;
    std::fill(result->tissue.indices.begin(),result->tissue.indices.end(),0);
    std::fill(result->tissue.faces.begin(),result->tissue.faces.end(),-1);
    return result;
}
std::shared_ptr<Mesh> radial(const M4& frame,const AfTissueShape& s,int resolution,uint64_t cancel) {
    if(resolution<3||resolution>256||!frame.allFinite()) throw std::runtime_error("Invalid radial tissue inputs.");
    if(resolution>=128) return radial_mesh(sphere_4_points,sphere_4_faces,frame,s,cancel);
    if(resolution>=64) return radial_mesh(sphere_3_points,sphere_3_faces,frame,s,cancel);
    if(resolution>=24) return radial_mesh(sphere_2_points,sphere_2_faces,frame,s,cancel);
    return radial_mesh(sphere_1_points,sphere_1_faces,frame,s,cancel);
}
}
