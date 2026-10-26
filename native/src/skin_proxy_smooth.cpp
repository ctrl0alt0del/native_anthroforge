// SPDX-License-Identifier: GPL-2.0-or-later
// Algorithm: Blender 5.0.1 MOD_smooth.cc, Blender Authors (2005).
#include "construction_internal.hpp"
#include "anthroforge/skin_density.h"
#include <set>
namespace af::skin_proxy {
using Points=Eigen::Matrix<float,Eigen::Dynamic,3,Eigen::RowMajor>;
using Edge=std::pair<int64_t,int64_t>;
static std::set<Edge> edges(const Mesh& mesh,uint64_t cancel) {
    std::set<Edge> result;
    for(size_t face=0;face+1<mesh.offsets.size();++face) {
        if(face%4096==0) check_cancel(cancel);
        const auto start=mesh.offsets[face],end=mesh.offsets[face+1];
        for(auto i=start;i<end;++i) result.insert(std::minmax(mesh.corners[i],mesh.corners[i+1<end?i+1:start]));
    }
    return result;
}
static Points accumulated(const Points& points,const std::set<Edge>& edges,std::vector<int>& counts,uint64_t cancel) {
    Points result=Points::Zero(points.rows(),3); int visited=0;
    for(const auto& [a,b]:edges) {
        if(visited++%4096==0) check_cancel(cancel);
        const Eigen::Vector3f midpoint=(points.row(a)+points.row(b))*.5f;
        result.row(a)+=midpoint; result.row(b)+=midpoint; ++counts[a]; ++counts[b];
    }
    return result;
}
static void step(Points& points,const std::set<Edge>& edges,float factor,uint64_t cancel) {
    std::vector<int> counts(points.rows()); const auto sums=accumulated(points,edges,counts,cancel);
    for(int i=0;i<points.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        const float scale=counts[i]?1.f/float(counts[i]):1.f;
        points.row(i)=(1.f-factor)*points.row(i)+factor*(sums.row(i)*scale);
    }
}
static std::shared_ptr<Mesh> smooth(const Mesh& mesh,float factor,int iterations,uint64_t cancel) {
    const auto links=edges(mesh,cancel); Points points=mesh.vertices.cast<float>();
    for(int i=0;i<iterations;++i) { check_cancel(cancel); step(points,links,factor,cancel); }
    return deform_mesh(mesh,points.cast<double>(),cancel);
}
}
uint64_t af_skin_proxy_smooth(uint64_t handle,double factor,int iterations,uint64_t cancel) {
    try {
        if(!std::isfinite(factor)||factor<0||factor>1||iterations<0||iterations>100)
            throw std::runtime_error("Invalid skin proxy smoothing settings.");
        af::check_cancel(cancel); const auto mesh=af::mesh(handle);
        if(factor==0||iterations==0) return af::retain(mesh);
        return af::retain(af::skin_proxy::smooth(*mesh,float(factor),iterations,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
