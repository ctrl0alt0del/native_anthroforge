// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_pins.hpp"
#include "construction_internal.hpp"

namespace af {
static void validate_pins(const Mesh& mesh,const std::vector<double>& pins,uint64_t cancel) {
    if(pins.size()%material_pin_width||pins.size()/material_pin_width>262144) throw std::runtime_error("Invalid retained structural pin storage.");
    const auto grids=material_grids(mesh);
    for(size_t i=0;i<pins.size();i+=material_pin_width) { check_cancel(cancel); material_equation(mesh,grids,pins.data()+i); }
}
}
int64_t af_mesh_material_pins(uint64_t handle,double* data,int64_t count) {
    try {
        const auto mesh=af::mesh(handle); const auto size=int64_t(mesh->material_pins.size());
        if(!data&&count==0) return size;
        if(count!=size||(count&&!data)) throw std::runtime_error("Invalid material pin copy buffer.");
        std::copy(mesh->material_pins.begin(),mesh->material_pins.end(),data); return size;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
uint64_t af_mesh_with_material_pins(uint64_t handle,const double* data,int64_t count,uint64_t cancel) {
    try {
        if(count<0||count>262144*int64_t(af::material_pin_width)||(count&&!data)) throw std::runtime_error("Invalid material pin buffer.");
        const auto source=af::mesh(handle); std::vector<double> pins;
        if(count) pins.assign(data,data+count);
        af::validate_pins(*source,pins,cancel); auto result=af::deform_mesh(*source,source->vertices,cancel,source->prepared);
        result->material_pins=std::move(pins); return af::retain(result);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_surface_material_pins(uint64_t handle,const AfSurfacePins* inputs,uint64_t cancel) {
    try {
        if(!inputs) throw std::runtime_error("Missing structural surface pins.");
        const auto source=af::mesh(handle); auto result=af::deform_mesh(*source,source->vertices,cancel,true);
        result->material_pins=af::material_capture(*result,*inputs,cancel);
        af::validate_pins(*result,result->material_pins,cancel); return af::retain(result);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
