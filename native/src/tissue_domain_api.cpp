#include "construction_internal.hpp"
#include "anthroforge/tissue.h"

int af_mesh_tissue_base_samples(uint64_t output,const double* base,int64_t count,double* xyz,int64_t vertices,uint64_t cancel) {
    try {
        const auto mesh=af::mesh(output); const auto& d=mesh->tissue;
        if(d.kind!=4 && d.kind!=5 && d.kind!=3) return 2;
        if(!base || !xyz || d.source_count!=count || mesh->vertices.rows()!=vertices)
            throw std::runtime_error("Base surface differs from accepted tissue material domain.");
        Eigen::Map<const af::Vertices> source(base,count,3); Eigen::Map<af::Vertices> dest(xyz,vertices,3);
        for(int64_t i=0;i<vertices;++i) {
            af::check_cancel(cancel); dest.row(i).setZero();
            for(auto j=d.offsets[i];j<d.offsets[i+1];++j) dest.row(i)+=d.weights[j]*source.row(d.indices[j]);
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}

int af_mesh_tissue_sizes(uint64_t source,int64_t* sizes) {
    try {
        if(!sizes) throw std::runtime_error("Missing tissue domain size buffer.");
        const auto mesh=af::mesh(source); const auto& d=mesh->tissue;
        sizes[0]=d.kind?9+int64_t(2*d.sides.size()+2*d.parts.size()+d.indices.size()):0;
        sizes[1]=int64_t(d.weights.size()); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_mesh_tissue_copy(uint64_t source,int64_t* data,int64_t count,double* weights,int64_t entries) {
    try {
        const auto mesh=af::mesh(source); const auto records=af::tissue_records(mesh->tissue);
        if(count!=int64_t(records.size())||entries!=int64_t(mesh->tissue.weights.size())||(count&&!data)||(entries&&!weights))
            throw std::runtime_error("Invalid tissue domain output buffers.");
        std::copy(records.begin(),records.end(),data);
        std::copy(mesh->tissue.weights.begin(),mesh->tissue.weights.end(),weights); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
uint64_t af_mesh_tissue_restore(uint64_t source,const int64_t* data,int64_t count,const double* weights,int64_t entries,uint64_t cancel) {
    try {
        const auto mesh=af::mesh(source);
        auto domain=af::tissue_restore(data,count,weights,entries,mesh->vertices.rows(),int64_t(mesh->offsets.size())-1);
        auto result=af::deform_mesh(*mesh,mesh->vertices,cancel,mesh->prepared);
        result->tissue=std::move(domain); return af::retain(result);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
