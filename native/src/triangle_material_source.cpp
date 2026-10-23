// SPDX-License-Identifier: GPL-3.0-or-later
#include "construction_internal.hpp"
#include "anthroforge/attachments.h"

namespace af {
void validate_triangle_source(const TriangleMaterial& m) {
    if(m.source_positions.empty()&&m.layer_size==0) return; // Older accepted projects.
    if(m.source_count<1||m.source_count>10000000||m.layer_size<1||m.source_count%m.layer_size||
       int64_t(m.source_positions.size())!=9*m.source_count)
        throw std::runtime_error("Invalid Boolean construction chart dimensions.");
    for(double v:m.source_positions) if(!std::isfinite(v))
        throw std::runtime_error("Nonfinite Boolean construction chart.");
}
}
int64_t af_mesh_triangle_source_size(uint64_t source) {
    try { const auto m=af::mesh(source); return m->triangle_material.layer_size?int64_t(m->triangle_material.source_positions.size())+1:0; }
    catch(const std::exception& e) { af::set_error(e.what()); return -1; }
}
int af_mesh_triangle_source_copy(uint64_t source,double* output,int64_t count) {
    try {
        const auto m=af::mesh(source); const auto& p=m->triangle_material;
        if(count!=int64_t(p.source_positions.size())+(p.layer_size?1:0)||(count&&!output))
            throw std::runtime_error("Invalid Boolean construction chart buffer.");
        if(count) { output[0]=double(p.layer_size); std::copy(p.source_positions.begin(),p.source_positions.end(),output+1); }
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
uint64_t af_mesh_triangle_source_restore(uint64_t source,const double* values,int64_t count,uint64_t cancel) {
    try {
        const auto m=af::mesh(source);
        if(!values||count!=1+9*m->triangle_material.source_count||count<10||!std::isfinite(values[0])||
           values[0]<1||values[0]>m->triangle_material.source_count||values[0]!=std::floor(values[0]))
            throw std::runtime_error("Invalid saved Boolean construction chart.");
        auto result=af::deform_mesh(*m,m->vertices,cancel,m->prepared);
        auto& p=result->triangle_material; p.layer_size=int64_t(values[0]);
        p.source_positions.assign(values+1,values+count); af::validate_triangle_source(p);
        return af::retain(result);
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
