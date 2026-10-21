#include "anthroforge/inspection.h"
#include "inspection_internal.hpp"
#include "tissue_relaxation.hpp"
#include "material_domain.hpp"
#include <set>

namespace af::inspection {
static Vertices source_flags(const Mesh& base) {
    Vertices flags=Vertices::Zero(base.vertices.rows(),3);
    for(const auto& [edge,value]:tissue::boundary_topology(mesh_faces(base),0))
        if(value.count==1) flags(edge.first,0)=flags(edge.second,0)=1;
    std::vector<std::set<size_t>> owners(size_t(base.vertices.rows())); const auto grids=material_grids(base);
    for(size_t i=0;i<grids.size();++i) for(auto vertex:grids[i].indices) owners[size_t(vertex)].insert(i);
    for(size_t i=0;i<owners.size();++i) if(owners[i].size()>1) flags(int64_t(i),1)=1;
    return flags;
}
static double zero_height(const Mesh& mesh,const Mesh& rest,const Mesh& base,int triangle,const V3& bary,uint64_t cancel) {
    Vertices field=Vertices::Zero(rest.vertices.rows(),3);
    for(int64_t i=0;i<field.rows();++i) {
        check_cancel(cancel); field(i,0)=(V3(rest.vertices.row(i))-source_point(rest,base,i)).norm()==0?1.:0.;
    }
    return mapped_sample(rest,mesh,field,false,triangle,bary,cancel).x();
}
static void point_flags(const Mesh& mesh,const Mesh* base,const Mesh* rest,int triangle,const V3& bary,double* out,uint64_t cancel) {
    std::fill(out,out+4,0.); const auto& d=mesh.tissue;
    if(!d.kind) return;
    if(base) {
        const V3 p=mapped_sample(*base,mesh,source_flags(*base),true,triangle,bary,cancel); out[0]=p.x(); out[1]=p.y();
        if(rest) out[2]=zero_height(mesh,*rest,*base,triangle,bary,cancel);
    }
    for(int j=0;j<3;++j) {
        const auto id=mesh.triangles(triangle,j);
        if(d.kind==3&&d.sides[size_t(id)]==2) out[3]+=bary[j];
    }
}
static bool boundary(const Mesh& mesh,int triangle) {
    const auto ids=mesh.triangles.row(triangle); const auto edges=tissue::boundary_topology(mesh_faces(mesh),0);
    for(int j=0;j<3;++j) {
        const auto found=edges.find(std::minmax(int64_t(ids[j]),int64_t(ids[(j+1)%3])));
        if(found!=edges.end()&&found->second.count==1) return true;
    }
    return false;
}
static void point_row(const Mesh& mesh,const Mesh* base,int triangle,const V3& bary,double* out) {
    const V3 p=sample(mesh,mesh.vertices,triangle,bary); V3 source=p;
    if(base) { source.setZero(); for(int j=0;j<3;++j) source+=source_point(mesh,*base,mesh.triangles(triangle,j))*bary[j]; }
    const V3 delta=p-source,normal=surface_normal(mesh,M4::Identity(),triangle);
    int offset=0; for(const auto& v:std::array<V3,4>{p,source,delta,normal}) { std::copy(v.data(),v.data()+3,out+offset); offset+=3; }
    const auto face=mesh.polygons[size_t(triangle)]; const auto& d=mesh.tissue;
    out[12]=d.kind?double(d.parts[size_t(face)]):-1; out[13]=d.kind?double(d.faces[size_t(face)]):double(face);
    std::set<int64_t> sides; if(d.kind) for(int j=0;j<3;++j) sides.insert(d.sides[size_t(mesh.triangles(triangle,j))]);
    out[14]=sides.size()==1?double(*sides.begin()):-1; out[15]=boundary(mesh,triangle)?1:0;
}
static V3 region_sample(const Mesh& target,const Mesh& rest,const Mesh* base,const AfTissueRelax& settings,
                        const AfTissueRegion& region,int triangle,const V3& bary,uint64_t cancel) {
    const auto core=tissue::region_mask(rest,base,settings,region,cancel);
    const auto weights=tissue::feather(rest,core,region.feather,cancel); Vertices field(rest.vertices.rows(),3);
    for(int64_t i=0;i<field.rows();++i) field.row(i)=V3(core[size_t(i)],weights[size_t(i)],region.mode==0&&core[size_t(i)]>0?1:0);
    return mapped_sample(rest,target,field,false,triangle,bary,cancel);
}
}
int af_inspection_point(uint64_t target,uint64_t base,uint64_t rest,int triangle,const double* bary,double* row,uint64_t cancel) {
    try {
        const auto mesh=af::mesh(target),source=base?af::mesh(base):nullptr;
        const auto inflated=rest?af::mesh(rest):nullptr; af::check_cancel(cancel);
        af::inspection::witness(*mesh,triangle,af::V3(bary));
        af::inspection::point_row(*mesh,source.get(),triangle,af::V3(bary),row);
        af::inspection::point_flags(*mesh,source.get(),inflated.get(),triangle,af::V3(bary),row+16,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_inspection_point_lines(uint64_t target,const double* frame,const double* row,double* lines) {
    try {
        const auto mesh=af::mesh(target); const af::M4 m(frame); const af::V3 p=af::point(m,af::V3(row));
        const double size=std::max(1e-6,(mesh->vertices.colwise().maxCoeff()-mesh->vertices.colwise().minCoeff()).norm()*.015);
        for(int i=0;i<6;++i) { const af::V3 v=p+af::V3::Unit(i/2)*size*(i%2?1:-1); std::copy(v.data(),v.data()+3,lines+3*i); }
        const af::V3 base=af::point(m,af::V3(row+3)),normal=p+m.topLeftCorner<3,3>().inverse().transpose()*af::V3(row+9)*size*4;
        const std::array<af::V3,4> vector{base,p,p,normal}; int i=18;
        for(const auto& v:vector) { std::copy(v.data(),v.data()+3,lines+i); i+=3; }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_inspection_regions(uint64_t target,uint64_t rest,uint64_t base,int triangle,const double* bary,
    const AfTissueRelax* settings,const AfTissueRegion* regions,int count,double* rows,uint64_t cancel) {
    try {
        if(count<0||count>1024||!settings||(count&&(!regions||!rows))) throw std::runtime_error("Invalid constraint inspection inputs.");
        const auto mesh=af::mesh(target),reference=af::mesh(rest),source=base?af::mesh(base):nullptr;
        for(int i=0;i<count;++i) {
            af::check_cancel(cancel); const auto value=af::inspection::region_sample(*mesh,*reference,source.get(),*settings,regions[i],triangle,af::V3(bary),cancel);
            std::copy(value.data(),value.data()+3,rows+4*i); rows[4*i+3]=value.y()*regions[i].strength;
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
