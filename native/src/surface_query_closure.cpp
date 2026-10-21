// SPDX-License-Identifier: GPL-3.0-or-later
#include "surface_query.hpp"
#include <array>
#include <map>
#include <numeric>

namespace af::query {
using Edge=std::pair<int,int>;
struct Use { int count=0; Edge oriented; };
static std::vector<Edge> boundary(const Mesh& source,uint64_t cancel) {
    std::map<Edge,Use> counts;
    for(int i=0;i<source.triangles.rows();++i) {
        check_cancel(cancel);
        for(int j=0;j<3;++j) {
            const int a=source.triangles(i,j),b=source.triangles(i,(j+1)%3);
            auto& entry=counts[std::minmax(a,b)]; ++entry.count; entry.oriented={a,b};
        }
    }
    std::vector<Edge> result;
    for(const auto& [edge,use]:counts) if(use.count==1) result.push_back(use.oriented);
    return result;
}
static Vertices backing(const Mesh& source,const Mesh& base,uint64_t cancel) {
    const auto& d=source.tissue;
    if(d.source_count!=base.vertices.rows()) throw std::runtime_error("Query closure requires the matching tissue material base.");
    Vertices result=Vertices::Zero(source.vertices.rows(),3);
    for(int i=0;i<result.rows();++i) {
        check_cancel(cancel);
        for(auto j=d.offsets.at(size_t(i));j<d.offsets.at(size_t(i+1));++j)
            result.row(i)+=d.weights.at(size_t(j))*base.vertices.row(d.indices.at(size_t(j)));
    }
    return result;
}
static Input raw(const Mesh& source) {
    Input result{source.vertices,source.triangles,{}};
    result.origins.resize(source.triangles.rows());
    std::iota(result.origins.begin(),result.origins.end(),0); return result;
}
static void walls(Input& input,const std::vector<Edge>& edges,int first,int count) {
    for(size_t i=0;i<edges.size();++i) {
        const auto [a,b]=edges[i];
        input.faces.row(first+2*i)=Eigen::RowVector3i(a,a+count,b+count);
        input.faces.row(first+2*i+1)=Eigen::RowVector3i(a,b+count,b);
    }
}
static Input volume(const Mesh& source,const Vertices& base,const std::vector<Edge>& edges) {
    const int n=int(source.vertices.rows()),f=int(source.triangles.rows()); Input result;
    result.vertices.resize(2*n,3); result.vertices<<source.vertices,base;
    result.faces.resize(2*f+2*edges.size(),3); result.faces.topRows(f)=source.triangles;
    for(int i=0;i<f;++i) result.faces.row(f+i)=source.triangles.row(i).reverse().array()+n;
    walls(result,edges,2*f,n);
    result.origins.resize(result.faces.rows(),-1);
    std::iota(result.origins.begin(),result.origins.begin()+f,0); return result;
}
static std::vector<int> weld(Input& input,uint64_t cancel) {
    std::map<std::array<double,3>,int> unique; Vertices points(input.vertices.rows(),3);
    std::vector<int> indices(size_t(input.vertices.rows()));
    for(int i=0;i<input.vertices.rows();++i) {
        check_cancel(cancel);
        const std::array<double,3> key{input.vertices(i,0),input.vertices(i,1),input.vertices(i,2)};
        const auto [entry,inserted]=unique.emplace(key,int(unique.size()));
        indices[size_t(i)]=entry->second;
        if(inserted) points.row(entry->second)=input.vertices.row(i);
    }
    input.vertices=points.topRows(unique.size()); return indices;
}
static void compact(Input& input,uint64_t cancel) {
    const auto indices=weld(input,cancel); int count=0;
    for(int i=0;i<input.faces.rows();++i) {
        check_cancel(cancel); Eigen::RowVector3i face;
        for(int j=0;j<3;++j) face[j]=indices.at(size_t(input.faces(i,j)));
        const V3 ab=input.vertices.row(face[1])-input.vertices.row(face[0]);
        const V3 ac=input.vertices.row(face[2])-input.vertices.row(face[0]);
        if(ab.cross(ac).squaredNorm()==0) continue;
        input.faces.row(count)=face; input.origins[size_t(count++)]=input.origins[size_t(i)];
    }
    input.faces.conservativeResize(count,3); input.origins.resize(size_t(count));
}
Input close(const Mesh& source,const Mesh* base,uint64_t cancel) {
    const auto edges=boundary(source,cancel);
    if(edges.empty()||source.tissue.kind<3) return raw(source);
    if(!base) throw std::runtime_error("Confirmed tissue placement requires its accepted material base.");
    const auto rest=backing(source,*base,cancel);
    if((rest.array()==source.vertices.array()).all()) return raw(source);
    auto result=volume(source,rest,edges); compact(result,cancel); return result;
}
}
