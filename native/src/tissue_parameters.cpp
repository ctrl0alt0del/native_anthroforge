// SPDX-License-Identifier: GPL-3.0-or-later
// Default authoring values port muscle_section_profile.reset_profile and grid control initialization.
#include "tissue_inflation.hpp"

int af_tissue_profile_reset(double depth,double* profile) {
    try {
        if(!profile||!std::isfinite(depth)||depth<0||depth>10) throw std::runtime_error("Profile peak depth must be 0..10 metres.");
        for(int i=0;i<4;++i) { profile[i]=(i==0||i==3)?.5*depth:depth; profile[i+4]=.5; }
        profile[8]=1; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_tissue_profile_scale(const double* depths,double factor,double* output) {
    try {
        if(!depths||!output||!std::isfinite(factor)||factor<0) throw std::runtime_error("Profile scale must be finite and nonnegative.");
        double scaled[4];
        for(int i=0;i<4;++i) {
            scaled[i]=depths[i]*factor;
            if(!std::isfinite(depths[i])||depths[i]<0||depths[i]>10||!std::isfinite(scaled[i])||scaled[i]>10)
                throw std::runtime_error("Scaled profile depths must be 0..10 metres.");
        }
        std::copy(scaled,scaled+4,output); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_tissue_control_default(uint64_t source,int part,double* point) {
    try {
        const auto mesh=af::mesh(source); const auto grids=af::material_grids(*mesh);
        if(!point||part<0||size_t(part)>=grids.size()) throw std::runtime_error("Inflation control needs an accepted material part.");
        const auto& grid=grids[size_t(part)]; const auto index=grid.indices[size_t((grid.rows/2)*grid.columns+grid.columns/2)];
        for(int i=0;i<3;++i) point[i]=mesh->vertices(index,i);
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
