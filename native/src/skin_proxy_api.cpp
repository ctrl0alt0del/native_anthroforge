#include "blender_mesh.hpp"
#include "anthroforge/skin_density.h"
uint64_t af_skin_proxy_decimate(uint64_t handle,int target,uint64_t budget,uint64_t cancel) {
    try {
        if(target<1) throw std::runtime_error("Invalid skin proxy face target.");
        af::check_cancel(cancel); const auto mesh=af::mesh(handle);
        if(target>=mesh->triangles.rows()||mesh->triangles.rows()<=3) return af::retain(mesh);
        const auto estimate=uint64_t(mesh->triangles.rows())*2048+uint64_t(mesh->vertices.rows())*512;
        if(budget&&estimate>budget) throw std::runtime_error("Skin proxy preparation exceeds worker memory budget.");
        return af::retain(af::blender_mesh::decimate(*mesh,target,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
