#include "skin_guides.hpp"
#include "material_binding.hpp"
#include "material_domain.hpp"
#include "tissue_branches.hpp"

namespace af::skin_guides {
static void sample(Guides& out,const V3& position,const V3& along,const V3& normal,int owner) {
    const double length=along.norm(),area=normal.norm();
    if(length<=1e-12||area<=1e-12) return;
    const V3 d=along/length,n=normal/area;
    out.samples.push_back({position.x(),position.y(),position.z(),d.x(),d.y(),d.z(),n.x(),n.y(),n.z(),double(owner)});
}
static Vertices positions(const MaterialGrid& grid,const binding::Index& index,const M4& frame,uint64_t cancel) {
    Vertices result(grid.indices.size(),3);
    for(size_t i=0;i<grid.indices.size();++i) {
        check_cancel(cancel);
        const V3 p=binding::material_point(index,{{grid.indices[i],1.}},1,cancel);
        result.row(int64_t(i))=af::point(frame,p);
    }
    return result;
}
static void interior(Guides& out,const MaterialGrid& g,const Vertices& p,int owner,int sign,uint64_t cancel) {
    for(int i=1;i<g.rows-1;i+=2) for(int j=1;j<g.columns-1;j+=3) {
        check_cancel(cancel); const int k=i*g.columns+j;
        const V3 along=(p.row(k+1)-p.row(k-1))*.5;
        const V3 across=(p.row(k+g.columns)-p.row(k-g.columns))*.5;
        sample(out,p.row(k),along,sign*across.cross(along),owner);
    }
}
static void center(Guides& out,const MaterialGrid& g,const Vertices& p) {
    for(int j=0;j<g.columns;j+=3) {
        const V3 v=p.row((g.rows/2)*g.columns+j);
        out.points.insert(out.points.end(),{v.x(),v.y(),v.z()});
    }
    out.offsets.push_back(int64_t(out.points.size()/3));
}
static void frame_valid(const M4& frame) {
    if(!frame.allFinite()||std::abs(frame.block<3,3>(0,0).determinant())<1e-18)
        throw std::runtime_error("FLOW capture needs a finite nonsingular frame.");
}
Guides charts(const Mesh& base,const Mesh& current,const M4& frame,bool reverse,uint64_t cancel) {
    frame_valid(frame); const auto grids=material_grids(base);
    if(grids.empty()||current.tissue.source_count!=base.vertices.rows())
        throw std::runtime_error("Tissue has no compatible regular material charts; use explicit FLOW Fibers.");
    const auto index=binding::index(current,cancel); Guides out;
    for(size_t i=0;i<grids.size();++i) {
        const auto& g=grids[i]; const auto p=positions(g,index,frame,cancel);
        const bool flip=reverse!=tissue::grid_reversed(base,g);
        const int sign=(flip!=(frame.block<3,3>(0,0).determinant()<0))?-1:1;
        const auto before=out.samples.size(); interior(out,g,p,int(i),sign,cancel);
        if(out.samples.size()==before) throw std::runtime_error("FLOW patch has no nondegenerate interior samples.");
        if(grids.size()==1) center(out,g,p);
    }
    return out;
}
static void path_sample(Guides& out,const V3& a,const V3& b) {
    const V3 direction=(b-a)/std::max((b-a).norm(),1e-12),mid=(a+b)*.5;
    out.samples.push_back({mid.x(),mid.y(),mid.z(),direction.x(),direction.y(),direction.z(),0,0,0,0});
}
Guides path(const Path& source,const M4& frame,uint64_t cancel) {
    frame_valid(frame); Guides out; V3 previous=V3::Zero();
    for(size_t i=0;i<source.samples.size()/11;i+=3) {
        check_cancel(cancel); const V3 current=af::point(frame,V3(source.samples.data()+11*i));
        if(i) path_sample(out,previous,current);
        out.points.insert(out.points.end(),{current.x(),current.y(),current.z()}); previous=current;
    }
    if(out.points.size()<6) throw std::runtime_error("FLOW guide has fewer than two sampled points.");
    out.offsets.push_back(int64_t(out.points.size()/3)); return out;
}
}
