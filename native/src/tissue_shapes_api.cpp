// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_shapes.hpp"
#include <algorithm>
#include <cmath>

int af_tissue_field_edit(const double* source,int64_t count,const int64_t* indices,int64_t selected,double weight,double* output) {
    try {
        if(count<1||selected<0||!output||!std::isfinite(weight)||weight<0||weight>1||(selected&&!indices))
            throw std::runtime_error("Invalid tissue field assignment.");
        if(source) std::copy(source,source+count,output);
        else std::fill(output,output+count,weight);
        for(int64_t i=0;i<selected;++i) {
            if(indices[i]<0||indices[i]>=count) throw std::runtime_error("Field selection is outside its material domain.");
            output[indices[i]]=weight;
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}

static void valid(const AfTissueShape* settings,uint64_t cancel) {
    af::check_cancel(cancel);
    if(!settings) throw std::runtime_error("Missing tissue shape settings.");
    af::tissue::validate_shape(*settings);
}
uint64_t af_tissue_normal_shell(uint64_t source,const AfTissueShape* settings,const double* weights,int64_t count,uint64_t cancel) {
    try {
        valid(settings,cancel);
        return af::retain(af::tissue::normal_shell(*af::mesh(source),*settings,weights,count,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_tissue_profile_sweep(const double* samples,int count,int closed,const AfTissueShape* settings,uint64_t cancel) {
    try {
        valid(settings,cancel);
        return af::retain(af::tissue::profile_sweep(samples,count,closed!=0,*settings,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_tissue_radial(const double* frame,const AfTissueShape* settings,int resolution,uint64_t cancel) {
    try {
        valid(settings,cancel); if(!frame) throw std::runtime_error("Missing radial tissue frame.");
        return af::retain(af::tissue::radial(Eigen::Map<const af::M4>(frame),*settings,resolution,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
