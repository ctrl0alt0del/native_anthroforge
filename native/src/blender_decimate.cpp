#include "blender_mesh.hpp"
#include "bmesh_decimate.hh"
namespace af::blender_mesh {
std::shared_ptr<Mesh> decimate(const Mesh& source,int target,uint64_t cancel) {
    Owned mesh(source,cancel); check_cancel(cancel);
    const auto ratio=std::max(.01f,std::min(1.f,float(target)/float(mesh.value->totface)));
    BM_mesh_decimate_collapse(mesh.value,ratio,nullptr,1.f,false,-1,.00002f);
    return result(mesh.value,cancel);
}
}
