// SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
// SPDX-License-Identifier: GPL-2.0-or-later
// Blender 5.0.1 mesh_normals.cc: Mesh normals supplied to the Decimate modifier.
#include "blender_mesh.hpp"
#include "BLI_math_geom.h"
#include "BLI_math_vector.hh"
namespace af::blender_mesh {
using F3=blender::float3;
namespace math=blender::math;
static F3 mesh_face_normal(const BMFace* face) {
    F3 normal(0); const BMLoop* first=BM_FACE_FIRST_LOOP(face),*loop=first;
    const float *previous=first->prev->v->co;
    do { add_newell_cross_v3_v3v3(normal,previous,loop->v->co); previous=loop->v->co; }
    while((loop=loop->next)!=first);
    if(normalize_v3(normal)==0.f) normal[2]=1.f;
    return normal;
}
static void accumulate(const BMFace* face,std::vector<F3>& sums,std::vector<bool>& used) {
    const F3 normal=mesh_face_normal(face); const BMLoop* first=BM_FACE_FIRST_LOOP(face),*loop=first;
    do {
        const F3 point(loop->v->co);
        const auto prev=math::normalize(F3(loop->prev->v->co)-point);
        const auto next=math::normalize(F3(loop->next->v->co)-point);
        const auto index=BM_elem_index_get(loop->v); used[index]=true;
        sums[index]+=normal*math::safe_acos_approx(math::dot(prev,next));
    } while((loop=loop->next)!=first);
}
void input_normals(Owned& input,uint64_t cancel) {
    std::vector<F3> sums(input.vertices.size(),F3(0)); std::vector<bool> used(input.vertices.size());
    BMIter iter; BMFace* face; size_t count=0;
    BM_ITER_MESH(face,&iter,input.value,BM_FACES_OF_MESH) {
        if(count++%4096==0) check_cancel(cancel);
        accumulate(face,sums,used);
    }
    for(size_t i=0;i<input.vertices.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        const auto normal=math::normalize(used[i]?sums[i]:F3(input.vertices[i]->co));
        copy_v3_v3(input.vertices[i]->no,normal);
    }
}
}
