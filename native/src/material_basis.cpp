// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_basis.hpp"
#include "material_domain.hpp"
#include "construction_internal.hpp"
#include "anthroforge/attachments.h"

namespace af {
MaterialBasis material_basis(const Mesh& mesh) {
    if(mesh.basis.count) return mesh.basis;
    if(mesh.material.empty()) return {};
    return {mesh.vertices.rows(),mesh.material,mesh.material_axes};
}
uint64_t basis_storage(const MaterialBasis& basis) {
    return basis.grids.capacity()*sizeof(int64_t)+basis.parameters.capacity()*sizeof(double);
}
bool same_basis(const MaterialBasis& a,const MaterialBasis& b) {
    return a.count==b.count&&a.grids==b.grids&&a.parameters==b.parameters;
}
void validate_basis(const MaterialBasis& basis) {
    if(basis.count<0||basis.count>262144) throw std::runtime_error("Invalid material basis size.");
    if(!basis.count&&(!basis.grids.empty()||!basis.parameters.empty())) throw std::runtime_error("Material basis has no source.");
    if(!basis.grids.empty()) {
        Mesh view; view.vertices.resize(basis.count,3); view.material=basis.grids; view.material_axes=basis.parameters;
        material_grids(view);
    } else if(basis.parameters.size()!=size_t(basis.count)*3)
        throw std::runtime_error("Material patch coordinates do not match their source.");
    for(double value:basis.parameters) if(!std::isfinite(value)) throw std::runtime_error("Nonfinite material coordinate.");
}
}
int af_mesh_basis_sizes(uint64_t handle,int64_t* sizes) {
    try {
        if(!sizes) throw std::runtime_error("Missing material basis sizes.");
        const auto mesh=af::mesh(handle); const auto& b=mesh->basis;
        sizes[0]=b.count?1+int64_t(b.grids.size()):0; sizes[1]=int64_t(b.parameters.size()); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_mesh_basis_copy(uint64_t handle,int64_t* records,int64_t count,double* parameters,int64_t size) {
    try {
        const auto mesh=af::mesh(handle); const auto& b=mesh->basis;
        if(count!=(b.count?1+int64_t(b.grids.size()):0)||size!=int64_t(b.parameters.size())||(count&&!records)||(size&&!parameters))
            throw std::runtime_error("Invalid material basis output buffers.");
        if(count) { records[0]=b.count; std::copy(b.grids.begin(),b.grids.end(),records+1); }
        std::copy(b.parameters.begin(),b.parameters.end(),parameters); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
uint64_t af_mesh_basis_restore(uint64_t handle,const int64_t* records,int64_t count,const double* parameters,int64_t size,uint64_t cancel) {
    try {
        if(count<1||count>1048576||size<0||size>1048576||!records||(size&&!parameters)) throw std::runtime_error("Invalid material basis buffers.");
        af::MaterialBasis b{records[0],{records+1,records+count},{parameters,parameters+size}};
        af::validate_basis(b); const auto mesh=af::mesh(handle);
        const auto expected=mesh->tissue.kind>=3?mesh->tissue.source_count:mesh->vertices.rows();
        if(b.count!=expected) throw std::runtime_error("Material basis does not match its geometry source.");
        auto output=af::deform_mesh(*mesh,mesh->vertices,cancel,mesh->prepared);
        output->basis=std::move(b); return af::retain(output);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
