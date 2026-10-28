#include "blender_mesh.hpp"
#include "bmesh_decimate.hh"
namespace af::blender_mesh {
std::shared_ptr<Mesh> decimate(const Mesh& source,int target,uint64_t cancel,float minimum) {
    Owned mesh(source,cancel); input_normals(mesh,cancel); check_cancel(cancel);
    const auto fraction=minimum==0?float(double(target)/double(mesh.value->totface)):float(target)/float(mesh.value->totface);
    const auto ratio=std::max(minimum,std::min(1.f,fraction));
    BM_mesh_decimate_collapse(mesh.value,ratio,nullptr,1.f,false,-1,.00002f);
    return result(mesh.value,cancel);
}
}
