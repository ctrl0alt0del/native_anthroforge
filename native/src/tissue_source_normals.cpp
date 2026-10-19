// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_relaxation.hpp"

namespace af::tissue {
static Vertices source_field(const Mesh& rest,const AfTissueSource& source,uint64_t cancel) {
    const int64_t count=rest.tissue.source_count; Vertices normals(count,3);
    if(rest.tissue.kind==1) { normals.row(0)=unit(Eigen::Map<const M4>(source.frame).block<3,1>(0,2)); return normals; }
    if(rest.tissue.kind==2) {
        std::vector<double> values(size_t(count)*11);
        if(af_path_sample(source.path,int(count),0,1,source.frame,0,values.data(),cancel))
            throw std::runtime_error("Accepted tissue curve frames could not resolve.");
        for(int64_t i=0;i<count;++i) normals.row(i)=unit(V3(values.data()+i*11+6));
    } else {
        const auto base=mesh(source.mesh);
        if(base->vertices.rows()!=count) throw std::runtime_error("Tissue base correspondence no longer resolves.");
        normals=surface_normals(*base,mesh_faces(*base),cancel);
    }
    return normals;
}
Vertices source_normals(const Mesh& rest,const AfTissueSource& source,uint64_t cancel) {
    const auto normals=source_field(rest,source,cancel); const auto& d=rest.tissue;
    Vertices output=Vertices::Zero(rest.vertices.rows(),3);
    for(size_t i=0;i<d.sides.size();++i) {
        check_cancel(cancel);
        for(auto j=d.offsets[i];j<d.offsets[i+1];++j) output.row(i)+=d.weights[size_t(j)]*normals.row(d.indices[size_t(j)]);
        output.row(i)=unit(output.row(i));
    }
    return output;
}
}
