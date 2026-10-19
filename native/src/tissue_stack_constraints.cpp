// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_stacking.hpp"
#include <set>

namespace af::tissue::stacking {
static void boundary(Prepared& p,uint64_t cancel) {
    if(p.own->tissue.kind==3) return; // Shell backing stays exact during assembly; its outer rim may move.
    std::set<int64_t> fixed;
    for(const auto& pair:mesh_edges(mesh_faces(*p.base),cancel)) if(pair.second.count==1) {
        fixed.insert(pair.first.first); fixed.insert(pair.first.second);
    }
    p.fixed.assign(fixed.begin(),fixed.end());
}
static void regions(Prepared& p,const AfTissueStackSource& config,uint64_t cancel) {
    const auto& d=p.rest->tissue;
    for(int r=0;r<config.region_count;++r) {
        const auto& region=config.regions[r];
        if(region.mode!=0) continue;
        const auto mask=region_mask(*p.rest,p.base.get(),config.relaxation,region,cancel);
        for(size_t i=0;i<mask.size();++i) {
            check_cancel(cancel);
            if(mask[i]>0&&(d.sides[i]==0||d.sides[i]==p.side)) append_row(row(d,i),p.constraints,p.constraint_weights);
        }
    }
}
static Row pin(const AfTissueStackSource& config,int row,int64_t count) {
    Row result; double total=0;
    for(int j=0;j<4;++j) {
        const int k=4*row+j; const auto index=config.pins[k]; const double weight=config.pin_weights[k];
        if(index<0||index>=count||!std::isfinite(weight)||weight<0) throw std::runtime_error("Invalid exact stacking attachment weights.");
        if(weight) result[index]+=weight;
        total+=weight;
    }
    if(std::abs(total-1)>1e-10) throw std::runtime_error("Stacking attachment weights must sum to one.");
    return result;
}
void pack_constraints(Prepared& p,const AfTissueStackSource& config,uint64_t cancel) {
    boundary(p,cancel); regions(p,config,cancel);
    for(int i=0;i<config.pin_count;++i) {
        check_cancel(cancel); append_row(pin(config,i,p.base->vertices.rows()),p.constraints,p.constraint_weights);
    }
}
}
