// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_stacking.hpp"
#include <numeric>

namespace af::tissue::stacking {
static bool enabled(const Prepared& p,const AfTissueStackSource& config,size_t face) {
    const auto part=p.visible->tissue.parts[face];
    if(part<0||part>=config.parts) throw std::runtime_error("Stacking face has no inflation part.");
    return config.inflation[part].enabled!=0;
}
static void select(Prepared& p,const AfTissueStackSource& config,uint64_t cancel) {
    std::vector<int64_t> mapping(size_t(p.visible->vertices.rows()),-1);
    const auto faces=mesh_faces(*p.visible);
    for(size_t f=0;f<faces.size();++f) if(enabled(p,config,f)) {
        check_cancel(cancel);
        for(auto v:faces[f]) mapping[size_t(v)]=0;
    }
    for(size_t i=0;i<mapping.size();++i) if(mapping[i]==0) { mapping[i]=int64_t(p.selected.size()); p.selected.push_back(int64_t(i)); }
    for(size_t f=0;f<faces.size();++f) if(enabled(p,config,f)) for(size_t j=1;j+1<faces[f].size();++j) {
        p.faces.insert(p.faces.end(),{mapping[size_t(faces[f][0])],mapping[size_t(faces[f][j])],mapping[size_t(faces[f][j+1])]});
        p.parts.push_back(p.visible->tissue.parts[f]); p.sources.push_back(p.visible->tissue.faces[f]);
    }
}
static V3 direction(const Prepared& p,const Vertices& own,const Vertices& fallback,int64_t i) {
    V3 delta=V3(own.row(i))-V3(p.visible->vertices.row(i));
    if(delta.norm()<1e-12) {
        delta.setZero();
        for(const auto& [index,weight]:row(p.visible->tissue,size_t(i))) delta+=weight*V3(fallback.row(index));
    }
    const V3 world=p.frame.topLeftCorner<3,3>()*delta;
    if(world.norm()<1e-12||!world.allFinite()) throw std::runtime_error("Stacking limiting direction is degenerate.");
    return world.normalized();
}
static void orient(Prepared& p,uint64_t cancel) {
    std::vector<double> signs;
    for(size_t i=0;i<p.faces.size();i+=3) {
        check_cancel(cancel); const auto a=p.faces[i],b=p.faces[i+1],c=p.faces[i+2];
        const V3 ab=p.reference.row(b)-p.reference.row(a),ac=p.reference.row(c)-p.reference.row(a);
        signs.push_back(ab.cross(ac).dot(V3(p.directions.row(a)+p.directions.row(b)+p.directions.row(c))));
    }
    if(signs.empty()) return;
    auto middle=signs.begin()+signs.size()/2; std::nth_element(signs.begin(),middle,signs.end());
    const double median=signs.size()%2?*middle:(*middle+*std::max_element(signs.begin(),middle))*.5;
    if(median<0) for(size_t i=0;i<p.faces.size();i+=3) std::swap(p.faces[i],p.faces[i+2]);
}
void pack_geometry(Prepared& p,const AfTissueStackSource& config,uint64_t cancel) {
    select(p,config,cancel);
    const auto own=resolved_side(*p.visible,*p.own,p.side,cancel),fallback=limiting(*p.base,config,cancel);
    const auto count=int64_t(p.selected.size()); p.reference.resize(count,3); p.positions.resize(count,3); p.directions.resize(count,3);
    for(int64_t j=0;j<count;++j) {
        check_cancel(cancel); const auto i=p.selected[size_t(j)];
        p.reference.row(j)=point(p.frame,p.visible->vertices.row(i));
        p.positions.row(j)=point(p.frame,own.row(i));
        p.directions.row(j)=direction(p,own,fallback,i);
    }
    orient(p,cancel);
}
}
