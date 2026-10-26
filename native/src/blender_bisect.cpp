#include "blender_mesh.hpp"
#include "bmesh_bisect_plane.hh"
#include "BLI_math_geom.h"
#include "BLI_linklist.h"
#include "BLI_memarena.h"
#include "BLI_heap.h"
namespace af::blender_mesh {
static void triangulate(BMesh* mesh) {
    auto* arena=BLI_memarena_new(1<<14,__func__); auto* heap=BLI_heap_new_ex(1);
    BMIter iter; BMFace* face; LinkNode* duplicates=nullptr;
    BM_ITER_MESH(face,&iter,mesh,BM_FACES_OF_MESH) {
        if(face->len<4) continue;
        BM_face_triangulate(mesh,face,nullptr,nullptr,nullptr,nullptr,&duplicates,0,0,false,arena,heap);
    }
    // BMO triangulation reports duplicates; it does not remove these faces.
    BLI_linklist_free(duplicates,nullptr); BLI_memarena_free(arena); BLI_heap_free(heap,nullptr);
}
std::shared_ptr<Mesh> half(const Mesh& source,const V3& origin,const V3& normal,uint64_t cancel) {
    Owned mesh(source,cancel); float plane[4];
    const Eigen::Vector3f p=origin.cast<float>(),n=normal.cast<float>();
    plane_from_point_normal_v3(plane,p.data(),n.data()); check_cancel(cancel);
    BM_mesh_bisect_plane(mesh.value,plane,true,false,0,0,0);
    for(auto vertex=mesh.vertices.rbegin();vertex!=mesh.vertices.rend();++vertex)
        if(plane_point_side_v3(plane,(*vertex)->co)>0) BM_vert_kill(mesh.value,*vertex);
    check_cancel(cancel); triangulate(mesh.value);
    if(!mesh.value->totface) throw std::runtime_error("Skin symmetry plane leaves no source surface on the negative side.");
    return result(mesh.value,cancel);
}
}
