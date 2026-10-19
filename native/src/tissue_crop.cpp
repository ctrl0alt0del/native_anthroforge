// SPDX-License-Identifier: GPL-3.0-or-later
// Material half-space clipping from core/vcp/muscle_domain_clip.py; canonical triangles retained.
#include "tissue_crop.hpp"
#include "tissue_envelope.hpp"
#include "anthroforge/tissue.h"
#include <limits>

namespace af::tissue {
static MaterialRow interpolate(const MaterialRow& a,const MaterialRow& b,double t) {
    MaterialRow result;
    for(const auto& [index,weight]:a) result[index]+=(1-t)*weight;
    for(const auto& [index,weight]:b) result[index]+=t*weight;
    return result;
}
static int64_t intersection(CropState& s,int64_t first,int64_t last) {
    const auto edge=std::minmax(first,last); const auto found=s.intersections.find(edge);
    if(found!=s.intersections.end()) return found->second;
    const auto a=size_t(edge.first),b=size_t(edge.second); const auto index=int64_t(s.own.size());
    const double t=s.distances[a]/(s.distances[a]-s.distances[b]);
    s.base.push_back(s.base[a]+t*(s.base[b]-s.base[a]));
    s.own.push_back(s.own[a]+t*(s.own[b]-s.own[a]));
    s.material.push_back(interpolate(s.material[a],s.material[b],t));
    s.sides.push_back(std::max(s.sides[a],s.sides[b])); s.intersections[edge]=index;
    return index;
}
static std::vector<int64_t> clip(CropState& s,const Eigen::Vector3i& triangle) {
    std::vector<int64_t> polygon;
    for(int i=0;i<3;++i) {
        const auto first=triangle[i],last=triangle[(i+1)%3];
        const double a=s.distances[size_t(first)],b=s.distances[size_t(last)];
        if(a>=0) polygon.push_back(first);
        if((a<0&&b>0)||(b<0&&a>0)) polygon.push_back(intersection(s,first,last));
    }
    return polygon;
}
static bool nondegenerate(const CropState& s,const std::vector<int64_t>& face) {
    const V3 a=s.base[size_t(face[1])]-s.base[size_t(face[0])],b=s.base[size_t(face[2])]-s.base[size_t(face[0])];
    const double scale=std::max(a.cwiseAbs().maxCoeff(),b.cwiseAbs().maxCoeff());
    return a.cross(b).norm()>std::numeric_limits<double>::epsilon()*scale*scale*32;
}
static void emit(CropState& s,const Mesh& own,int triangle) {
    const auto polygon=clip(s,own.triangles.row(triangle)); const auto face=size_t(own.polygons[size_t(triangle)]);
    for(size_t i=1;i+1<polygon.size();++i) {
        std::vector<int64_t> ids{polygon[0],polygon[i],polygon[i+1]};
        if(!nondegenerate(s,ids)) continue;
        s.faces.push_back(std::move(ids)); s.parts.push_back(own.tissue.parts[face]);
        s.sources.push_back(own.tissue.faces[face]);
    }
}
std::shared_ptr<Mesh> crop_material(const Mesh& base,const Mesh& own,const double* plane,uint64_t cancel) {
    if(own.tissue.kind==5) return crop_envelope(base,own,plane,cancel);
    auto state=crop_inputs(base,own,plane,cancel);
    for(int i=0;i<own.triangles.rows();++i) { check_cancel(cancel); emit(state,own,i); }
    return crop_output(state,own.tissue,cancel);
}
}
uint64_t af_tissue_crop(uint64_t base,uint64_t own,const double* plane,uint64_t cancel) {
    try { return af::retain(af::tissue::crop_material(*af::mesh(base),*af::mesh(own),plane,cancel)); }
    catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
