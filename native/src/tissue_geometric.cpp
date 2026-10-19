// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_relaxation.hpp"

namespace af::tissue {
static V3 gravity(const AfTissueRelax& s) {
    const V3 direction(s.gravity); return direction.norm()>1e-12?V3(direction.normalized()):V3::Zero();
}
static Vertices sweep_relaxation(const Mesh& rest,const Constraints& c,const AfTissueRelax& s,uint64_t cancel) {
    Vertices output=rest.vertices; const int64_t size=rest.tissue.ring_size;
    double amount=s.sagginess*s.amount; if(s.limit>0) amount=std::min(amount,s.limit);
    const V3 direction=gravity(s);
    for(int64_t i=0;i<output.rows();++i) {
        check_cancel(cancel); if(!c.mass[size_t(i)]) continue;
        const double phase=double(i%size)/double(size-1),bulge=std::max(0.,1-std::abs(phase*2-1));
        output.row(i)+=(direction*(amount*bulge)).transpose();
    }
    return output;
}
static Vertices shell_relaxation(const Mesh& rest,const Constraints& c,const AfTissueRelax& s,uint64_t cancel) {
    Vertices output=rest.vertices; const auto count=rest.tissue.source_count; const V3 direction=gravity(s);
    for(int64_t i=0;i<count;++i) {
        check_cancel(cancel); if(!c.mass[size_t(i)]) continue;
        const V3 delta=rest.vertices.row(i)-rest.vertices.row(i+count);
        const V3 normal=delta.norm()>1e-12?V3(delta.normalized()):V3::UnitZ();
        V3 tangent=direction-normal*direction.dot(normal); if(tangent.norm()>1e-12) tangent.normalize();
        double amount=s.sagginess*delta.norm(); if(s.limit>0) amount=std::min(amount,s.limit);
        output.row(i)+=(tangent*amount).transpose();
    }
    return output;
}
Vertices relax_geometric(const Mesh& rest,const Constraints& c,const AfTissueSource& source,const AfTissueRelax& s,double* report,uint64_t cancel) {
    if(rest.tissue.kind==1) return relax_point(rest,c,source,s,report,cancel);
    if(rest.tissue.kind==2) return sweep_relaxation(rest,c,s,cancel);
    if(rest.tissue.kind==3) return shell_relaxation(rest,c,s,cancel);
    throw std::runtime_error("Geometric relaxation requires radial, profile or normal inflation.");
}
}
