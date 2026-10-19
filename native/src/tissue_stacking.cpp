// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_stacking.hpp"

namespace af::tissue::stacking {
static void validate(const AfTissueStackSource& s) {
    if(s.parts<1||s.parts>256||!s.inflation||s.side<1||s.side>2)
        throw std::runtime_error("Stacking preparation requires material part settings and side A/B.");
    if(s.region_count<0||s.region_count>256||(s.region_count&&!s.regions)||s.pin_count<0||s.pin_count>262144)
        throw std::runtime_error("Invalid stacking constraint count.");
    if(s.pin_count&&(!s.pins||!s.pin_weights)) throw std::runtime_error("Missing exact stacking attachment data.");
    const M4 frame=Eigen::Map<const M4>(s.frame);
    if(!frame.allFinite()||std::abs(frame.determinant())<1e-18) throw std::runtime_error("Stacking requires an invertible finite world frame.");
}
static std::unique_ptr<Prepared> prepare(const AfTissueStackSource& s,uint64_t cancel) {
    validate(s); auto p=std::make_unique<Prepared>(); p->base=mesh(s.base); p->rest=mesh(s.rest); p->own=mesh(s.own);
    const auto kind=p->own->tissue.kind;
    if(kind<3||kind>5||p->own->tissue.source_count!=p->base->vertices.rows()||p->rest->tissue.kind!=kind)
        throw std::runtime_error("Stacking requires matching accepted surface-based tissue stages.");
    if(s.side==2&&kind!=5) throw std::runtime_error("Only an envelope provides a second stacking side.");
    p->frame=Eigen::Map<const M4>(s.frame); p->side=s.side; p->reverse=s.reverse!=0;
    p->visible=visible_material(*p->base,*p->rest,s,cancel);
    pack_geometry(*p,s,cancel); pack_material(*p,cancel); pack_constraints(*p,s,cancel); return p;
}
static AfStackMaterial material(const Prepared& p) {
    return {p.material.data(),p.weights.data(),p.constraint_weights.data(),p.material_faces.data(),p.interpolation.data(),p.fixed.data(),p.constraints.data(),
        int(p.material.rows()),int(p.material_faces.size()/3),int(p.selected.size()),4,int(p.fixed.size()),int(p.constraints.size()/4)};
}
}
uint64_t af_tissue_stack_prepare(const AfTissueStackSource* source,uint64_t cancel) {
    try {
        if(!source) throw std::runtime_error("Missing stacking source.");
        return reinterpret_cast<uint64_t>(af::tissue::stacking::prepare(*source,cancel).release());
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_tissue_stack_release(uint64_t handle) { delete reinterpret_cast<af::tissue::stacking::Prepared*>(handle); }
int af_tissue_stack_domain(uint64_t handle,AfStackDomain* domain) {
    try {
        if(!handle||!domain) throw std::runtime_error("Missing prepared stacking domain.");
        const auto& p=*reinterpret_cast<af::tissue::stacking::Prepared*>(handle);
        domain->base=p.reference.data(); domain->own=p.positions.data(); domain->direction=p.directions.data();
        domain->faces=p.faces.data(); domain->parts=p.parts.data(); domain->sources=p.sources.data();
        domain->vertices=int(p.selected.size()); domain->triangles=int(p.faces.size()/3); domain->side=p.side-1;
        domain->material=af::tissue::stacking::material(p); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
uint64_t af_tissue_stack_apply(uint64_t first,uint64_t second,const double* a,int acount,const double* b,int bcount,uint64_t cancel) {
    try {
        if(!first) throw std::runtime_error("Missing stacking material lease.");
        const auto* p=reinterpret_cast<const af::tissue::stacking::Prepared*>(first);
        const auto* q=reinterpret_cast<const af::tissue::stacking::Prepared*>(second);
        return af::retain(af::tissue::stacking::assemble(*p,q,a,acount,b,bcount,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
