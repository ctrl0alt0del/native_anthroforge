// SPDX-License-Identifier: GPL-3.0-or-later
// Source goals, fixed cores, soft feathering and exact backing are distinct contracts.
#include "tissue_relaxation.hpp"

namespace af::tissue {
static void fixed(Constraints& c,size_t index,const V3& goal) {
    if(!c.mass[index]&&(c.goals.row(index).transpose()-goal).norm()>1e-9)
        throw std::runtime_error("Contradictory fixed tissue goals; resolve the overlapping regions or backing offset.");
    c.mass[index]=0; c.goals.row(index)=goal;
}
static void assign(Constraints& c,size_t index,const V3& goal,bool exact,double strength) {
    if(!goal.allFinite()) throw std::runtime_error("Tissue constraint goal is not finite.");
    if(exact) fixed(c,index,goal);
    else c.tethers.insert(c.tethers.end(),{double(index),goal.x(),goal.y(),goal.z(),0,strength});
}
static void region_goals(const Mesh& rest,Constraints& c,const AfTissueRegion& region,const WeightField& mask,uint64_t cancel) {
    const auto weights=feather(rest,mask,region.feather,cancel);
    for(size_t i=0;i<weights.size();++i) {
        check_cancel(cancel); if(weights[i]<=1e-8) continue;
        const V3 anchor=region.goals?V3(region.goals+3*i):V3(rest.vertices.row(i));
        const V3 normal=c.normals.row(i); const bool exact=region.mode==0&&mask[i]>0;
        assign(c,i,anchor+region.offset*normal,exact,region.strength*(exact?1:weights[i]));
    }
}
static void validate(const AfTissueRegion& r) {
    if(r.mode<0||r.mode>1||r.domain<0||r.domain>1||r.count<0||r.count>262144)
        throw std::runtime_error("Invalid tissue region definition.");
    if(!std::isfinite(r.strength)||r.strength<0||r.strength>1||!std::isfinite(r.feather)||r.feather<0||r.feather>1||!std::isfinite(r.offset))
        throw std::runtime_error("Invalid tissue region strength, feather or offset.");
}
Constraints prepare_constraints(const Mesh& rest,const AfTissueSource& source,const AfTissueRelax& settings,const AfTissueRegion* regions,int count,uint64_t cancel) {
    Constraints c{rest.vertices,source_normals(rest,source,cancel),WeightField(size_t(rest.vertices.rows()),1),{}};
    if(rest.tissue.kind==3) for(size_t i=0;i<c.mass.size();++i) if(rest.tissue.sides[i]==2) c.mass[i]=0;
    const auto base=source.mesh?mesh(source.mesh):nullptr;
    for(int i=0;i<count;++i) {
        validate(regions[i]);
        const auto mask=region_mask(rest,base.get(),settings,regions[i],cancel);
        region_goals(rest,c,regions[i],mask,cancel);
    }
    return c;
}
void apply_constraints(Vertices& points,const Constraints& c) {
    for(size_t i=0;i<c.tethers.size();i+=6) {
        const auto index=int64_t(c.tethers[i]); if(!c.mass[size_t(index)]) continue;
        const V3 goal(c.tethers.data()+i+1),p=points.row(index); points.row(index)=p+(goal-p)*c.tethers[i+5];
    }
    for(size_t i=0;i<c.mass.size();++i) if(!c.mass[i]) points.row(i)=c.goals.row(i);
}
}
