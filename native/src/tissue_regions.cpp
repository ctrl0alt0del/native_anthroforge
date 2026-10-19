// SPDX-License-Identifier: GPL-3.0-or-later
#include "construction_internal.hpp"
#include "anthroforge/tissue.h"
#include <set>

namespace {
using Region=std::pair<int64_t,int64_t>;
bool selectable(const af::Mesh& mesh,int64_t face,int side) {
    const auto& d=mesh.tissue;
    if(side<1||side>2||face<0||face>=int64_t(d.faces.size())||d.faces[size_t(face)]<0) return false;
    for(auto i=mesh.offsets[size_t(face)];i<mesh.offsets[size_t(face)+1];++i) {
        const auto value=d.sides.at(size_t(mesh.corners[size_t(i)]));
        if(value!=0&&value!=side) return false;
    }
    return true;
}
std::set<Region> selected(const int64_t* data,int count) {
    if(count<0||(count&&!data)) throw std::runtime_error("Invalid material region selection.");
    std::set<Region> result;
    for(int i=0;i<count;++i) result.emplace(data[2*i],data[2*i+1]);
    return result;
}
std::vector<int64_t> matching(const af::Mesh& mesh,const std::set<Region>& regions,int side) {
    std::vector<int64_t> output;
    for(size_t f=0;f<mesh.tissue.faces.size();++f)
        if(selectable(mesh,int64_t(f),side)&&regions.count({mesh.tissue.parts[f],mesh.tissue.faces[f]}))
            output.push_back(int64_t(f));
    return output;
}
std::vector<af::V3> lines(const af::Mesh& mesh,const std::vector<int64_t>& faces,const af::M4& frame) {
    std::set<Region> edges;
    for(auto f:faces) {
        const auto begin=mesh.offsets[size_t(f)],end=mesh.offsets[size_t(f)+1];
        for(auto i=begin;i<end;++i) edges.insert(std::minmax(mesh.corners[size_t(i)],mesh.corners[size_t(i+1<end?i+1:begin)]));
    }
    std::vector<af::V3> output;
    for(const auto& [a,b]:edges) for(auto v:{a,b}) output.push_back(af::point(frame,mesh.vertices.row(v)));
    return output;
}
}

int af_tissue_region_face(uint64_t source,int64_t polygon,int side,int64_t* region) {
    try {
        if(!region) throw std::runtime_error("Missing region identity output.");
        const auto mesh=af::mesh(source);
        if(!selectable(*mesh,polygon,side)) return 0;
        region[0]=mesh->tissue.parts[size_t(polygon)]; region[1]=mesh->tissue.faces[size_t(polygon)]; return 1;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
int af_tissue_regions_check(uint64_t source,const int64_t* regions,int count,int side) {
    try {
        const auto mesh=af::mesh(source); auto remaining=selected(regions,count);
        for(auto f:matching(*mesh,remaining,side)) remaining.erase({mesh->tissue.parts[size_t(f)],mesh->tissue.faces[size_t(f)]});
        if(!remaining.empty()) throw std::runtime_error("Support selection no longer matches the covering material side; select it again.");
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
int64_t af_tissue_region_lines(uint64_t source,const int64_t* regions,int count,int side,const double* frame,double* output,int64_t capacity) {
    try {
        if(!frame) throw std::runtime_error("Missing region display frame.");
        const auto mesh=af::mesh(source); const auto faces=matching(*mesh,selected(regions,count),side);
        const auto points=lines(*mesh,faces,Eigen::Map<const af::M4>(frame)); const auto size=int64_t(points.size()*3);
        if(!output) return size;
        if(capacity!=size) throw std::runtime_error("Invalid region outline buffer.");
        for(size_t i=0;i<points.size();++i) for(int a=0;a<3;++a) output[3*i+size_t(a)]=points[i][a];
        return size;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
