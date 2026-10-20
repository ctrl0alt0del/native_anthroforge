// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_relaxation.hpp"
#include "mesh_quality.hpp"
#include <chrono>

namespace af::tissue {
static void validate(const Mesh& rest,const AfTissueSource* source,const AfTissueRelax* s,const AfTissueRegion* regions,int count,double* report) {
    if(!source||!s||!report||count<0||count>1024||(count&&!regions)) throw std::runtime_error("Invalid tissue relaxation buffers.");
    tissue_validate(rest.tissue,rest.vertices.rows(),int64_t(rest.offsets.size())-1);
    if(!rest.tissue.kind||s->mode<0||s->mode>2||s->iterations<1||s->iterations>10000||s->passes<1||s->passes>100)
        throw std::runtime_error("Invalid tissue relaxation mode or iteration budget.");
    for(double v:{s->gravity[0],s->gravity[1],s->gravity[2],s->sagginess,s->limit,s->shape,s->volume,s->slack,s->tolerance,s->amount,s->minimum,s->power})
        if(!std::isfinite(v)) throw std::runtime_error("Tissue relaxation settings must be finite.");
    for(double v:{s->sagginess,s->shape,s->volume,s->slack}) if(v<0||v>1) throw std::runtime_error("Tissue material settings must be normalized.");
    if(s->limit<0||s->tolerance<=0||s->power<=0) throw std::runtime_error("Invalid tissue relaxation limit or tolerance.");
    if(s->mode&&rest.tissue.kind>3) throw std::runtime_error("Relaxation requires radial, profile or normal inflation.");
}
static std::shared_ptr<Mesh> evaluate(const Mesh& rest,const AfTissueSource& source,const AfTissueRelax& settings,const AfTissueRegion* regions,int count,double* report,uint64_t cancel) {
    const auto constraints=prepare_constraints(rest,source,settings,regions,count,cancel);
    Vertices points=rest.vertices;
    if(settings.mode==1) points=relax_geometric(rest,constraints,source,settings,report,cancel);
    else if(settings.mode==2) points=relax_static(rest,constraints,settings,report,cancel);
    if(settings.mode!=2) apply_constraints(points,constraints);
    report[3]=(points-rest.vertices).rowwise().norm().maxCoeff();
    for(size_t i=0;i<constraints.mass.size();++i) if(!constraints.mass[i])
        report[5]=std::max(report[5],(points.row(i)-constraints.goals.row(i)).norm());
    if(!points.allFinite()) throw std::runtime_error("NUMERICAL_FAILURE: tissue relaxation produced nonfinite coordinates.");
    check_cancel(cancel); return deform_mesh(rest,points,cancel,true);
}
}
uint64_t af_tissue_relax(uint64_t rest,const AfTissueSource* source,const AfTissueRelax* settings,const AfTissueRegion* regions,int count,double* report,uint64_t cancel) {
    const auto start=std::chrono::steady_clock::now();
    try {
        const auto input=af::mesh(rest); af::tissue::validate(*input,source,settings,regions,count,report);
        std::fill(report,report+7,0); af::check_cancel(cancel);
        auto output=af::tissue::evaluate(*input,*source,*settings,regions,count,report,cancel);
        af::quality::validate_tissue(*input,*output,cancel);
        report[6]=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
        return af::retain(output);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
