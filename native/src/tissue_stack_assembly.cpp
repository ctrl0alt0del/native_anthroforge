// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_stacking.hpp"
#include "tissue_envelope.hpp"

namespace af::tissue::stacking {
static Vertices local_positions(const Prepared& p,const double* values,int count,uint64_t cancel) {
    if(count!=int(p.selected.size())||(count&&!values)) throw std::runtime_error("Stacking result does not match its retained material lease.");
    auto points=resolved_side(*p.visible,*p.own,p.side,cancel); const M4 inverse=p.frame.inverse();
    for(int i=0;i<count;++i) {
        check_cancel(cancel); const V3 value(values+3*i);
        if(!value.allFinite()) throw std::runtime_error("Stacking result contains a nonfinite position.");
        points.row(p.selected[size_t(i)])=point(inverse,value);
    }
    return points;
}
static std::shared_ptr<Mesh> side(const Prepared& p,const double* values,int count,uint64_t cancel) {
    return deform_mesh(*p.visible,local_positions(p,values,count,cancel),cancel,false);
}
static std::shared_ptr<Mesh> shell(const Prepared& p,const double* values,int count,uint64_t cancel) {
    const auto positions=local_positions(p,values,count,cancel); auto vertices=p.own->vertices;
    if(positions.rows()!=p.own->tissue.source_count) throw std::runtime_error("Normal shell material topology changed during stacking.");
    vertices.topRows(positions.rows())=positions;
    return deform_mesh(*p.own,vertices,cancel,true);
}
static bool same_source(const Prepared& a,const Prepared& b) {
    return a.base==b.base&&a.rest==b.rest&&a.own==b.own&&a.visible->corners==b.visible->corners&&a.visible->offsets==b.visible->offsets;
}
static std::shared_ptr<Mesh> preserve_topology(const Mesh& own,std::shared_ptr<Mesh> output,uint64_t cancel) {
    if(own.vertices.rows()==output->vertices.rows()&&own.corners==output->corners&&own.offsets==output->offsets)
        return deform_mesh(own,output->vertices,cancel,true);
    return output;
}
std::shared_ptr<Mesh> assemble(const Prepared& first,const Prepared* second,const double* a,int acount,const double* b,int bcount,uint64_t cancel) {
    if(first.own->tissue.kind==3) return shell(first,a,acount,cancel);
    auto output=side(first,a,acount,cancel);
    if(first.own->tissue.kind==4) return preserve_topology(*first.own,output,cancel);
    if(!second||first.side!=1||second->side!=2||!same_source(first,*second))
        throw std::runtime_error("Envelope stacking requires both sides of the same intrinsic result.");
    return preserve_topology(*first.own,compose_envelope(*output,*side(*second,b,bcount,cancel),first.reverse,cancel),cancel);
}
}
