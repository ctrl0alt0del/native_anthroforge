// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_inflation.hpp"
#include "tissue_kernel.hpp"
#include "tissue_branches.hpp"
#include "tissue_directions.hpp"
#include "tissue_profile.hpp"
#include "tissue_preparation.hpp"
#include "mesh_quality.hpp"

namespace af::tissue {
static kernel::AfMuscleInput legacy_input(const AfTissueInflation& s,const MaterialGrid& grid) {
    kernel::AfMuscleInput input{};
    input.input_rows=grid.rows; input.input_cols=grid.columns;
    input.inflation_mode=s.mode; input.inflation_enabled=s.enabled;
    input.inflation_flip=s.reverse; input.inflation_closed_v=grid.closed_v;
    input.initialize_control=s.initialize_control; input.falloff=s.falloff;
    input.amount=s.amount; input.radius=std::max(s.radius,1e-6); input.depth=s.depth;
    input.b_strength=s.boundary_strength; input.b_band=std::max(.1,s.boundary_band);
    input.b_power=s.boundary_power; input.taper=s.taper;
    std::copy(s.control,s.control+3,input.control);
    return input;
}
static kernel::AfMuscleOutput prepared(const Mesh& source,const MaterialGrid& grid,uint64_t cancel) {
    kernel::AfMuscleOutput result; result.rows=grid.rows; result.cols=grid.columns;
    for(auto index:grid.indices) {
        check_cancel(cancel); const auto p=source.vertices.row(index);
        result.base.push_back({p.x(),p.y(),p.z()});
    }
    return result;
}
static void profile(kernel::AfMuscleOutput& output,const AfTissueInflation& s,const PreparedGrid* prepared) {
    if(!s.enabled) { output.inflated=output.base; return; }
    const int status=prepared?section_profile_prepared(output.base,output.rows,output.cols,s.profile,s.reverse?-1:1,
        prepared->normals,prepared->areas,prepared->limit,output.inflated)
        :section_profile(output.base,output.rows,output.cols,s.profile,s.direction,s.reverse?-1:1,output.inflated);
    if(status)
        throw std::runtime_error("Section Profile has a degenerate material frame.");
}
static void distributed(kernel::AfMuscleOutput& out,const kernel::AfMuscleInput& input,const Vertices& directions) {
    out.inflated=out.base;
    for(int i=0;i<out.rows;++i) for(int j=0;j<out.cols;++j) {
        const int index=i*out.cols+j;
        const double fade=out.length_weights.empty()?kernel::af_muscle_length_fade(j,out.cols,input.taper):out.length_weights[index];
        const double height=input.amount*kernel::af_muscle_edge_alpha(i,j,out.rows,out.cols,input,&out)*fade;
        const V3 direction=directions.row(index);
        out.inflated[index]=kernel::add(out.base[index],kernel::mul({direction.x(),direction.y(),direction.z()},input.inflation_flip?-height:height));
    }
}
static kernel::AfMuscleOutput prepared_output(const Mesh& source,const MaterialGrid& grid,const PreparedGrid* data,uint64_t cancel) {
    if(!data) return prepared(source,grid,cancel);
    kernel::AfMuscleOutput out; out.rows=grid.rows; out.cols=grid.columns; out.base=data->base; return out;
}
static Vertices directions(const Mesh& source,const MaterialGrid& grid,const PreparedGrid* data,double distance,uint64_t cancel) {
    return data?solve_directions(*data->diffusion,distance,cancel):inflation_directions(source,grid,distance,cancel);
}
Points inflate_prepared_grid(const Mesh& source,const MaterialGrid& grid,const AfTissueInflation& settings,const InflationWeights* weights,uint64_t cancel,const PreparedGrid* data) {
    const kernel::CancelScope scope(cancel);
    validate_inflation(settings,grid);
    auto output=prepared_output(source,grid,data,cancel);
    if(weights) { output.boundary_weights=weights->edge; output.length_weights=weights->fade; }
    if(settings.mode==2) profile(output,settings,data);
    else if(settings.mode==1&&settings.enabled&&settings.amount>0)
        distributed(output,legacy_input(settings,grid),directions(source,grid,data,settings.amount,cancel));
    else kernel::af_muscle_inflate(output,legacy_input(settings,grid));
    Points points; points.reserve(output.inflated.size());
    for(auto p:output.inflated) points.emplace_back(p.x,p.y,p.z);
    check_cancel(cancel);
    return points;
}
Points inflate_grid(const Mesh& source,const MaterialGrid& grid,const AfTissueInflation& settings,uint64_t cancel) {
    return inflate_prepared_grid(source,grid,settings,nullptr,cancel);
}
static std::shared_ptr<Mesh> evaluate(const Mesh& source,const AfTissueInflation* settings,int count,uint64_t cancel) {
    const auto grids=material_grids(source.material,source.vertices.rows());
    if(count!=1||grids.size()!=1) throw std::runtime_error("Ordinary grid inflation requires one material grid.");
    const auto points=inflate_grid(source,grids.front(),settings[0],cancel);
    auto vertices=source.vertices;
    for(size_t i=0;i<points.size();++i) vertices.row(grids.front().indices[i])=points[i];
    auto result=deform_mesh(source,vertices,cancel,source.prepared);
    quality::validate_tissue(source,*result,cancel);
    result->tissue=tissue_identity(4,vertices.rows(),int64_t(result->offsets.size())-1);
    result->basis=material_basis(source);
    return result;
}
}
uint64_t af_tissue_inflate_grid(uint64_t source,const AfTissueInflation* settings,int count,uint64_t cancel) {
    try {
        if(!settings||count<1||count>256) throw std::runtime_error("Invalid tissue inflation settings.");
        return af::retain(af::tissue::evaluate(*af::mesh(source),settings,count,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_tissue_source_mesh(uint64_t source,const double* matrix,uint64_t cancel) {
    try {
        if(!matrix) throw std::runtime_error("Missing tissue source frame.");
        const auto mesh=af::mesh(source); const af::M4 frame=Eigen::Map<const af::M4>(matrix);
        af::Vertices vertices=mesh->vertices;
        for(int64_t i=0;i<vertices.rows();++i) {
            af::check_cancel(cancel); vertices.row(i)=af::point(frame,mesh->vertices.row(i));
        }
        return af::retain(af::deform_mesh(*mesh,vertices,cancel,true));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
