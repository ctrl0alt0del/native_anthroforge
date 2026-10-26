#include "blender_mesh.hpp"
#include <cmath>
namespace af::blender_mesh {
static void fill_vertices(Owned& output,const Mesh& source,uint64_t cancel) {
    output.vertices.reserve(source.vertices.rows());
    for(int i=0;i<source.vertices.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        const Eigen::Vector3f point=source.vertices.row(i).cast<float>();
        if(!point.allFinite()) throw std::runtime_error("Skin coordinates exceed Blender float range.");
        output.vertices.push_back(BM_vert_create(output.value,point.data(),nullptr,BM_CREATE_NOP));
    }
}
static void fill_faces(Owned& output,const Mesh& source,uint64_t cancel) {
    for(int i=0;i<source.triangles.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        const auto face=source.triangles.row(i);
        BM_face_create_quad_tri(output.value,output.vertices.at(face[0]),output.vertices.at(face[1]),
            output.vertices.at(face[2]),nullptr,nullptr,BM_CREATE_NOP);
    }
}
Owned::Owned(const Mesh& source,uint64_t cancel) {
    BMeshCreateParams params{}; value=BM_mesh_create(&bm_mesh_allocsize_default,&params);
    try {
        fill_vertices(*this,source,cancel); size_t i=0;
        for(const auto& edge:edge_order(source,cancel)) {
            if(i++%4096==0) check_cancel(cancel);
            BM_edge_create(value,vertices.at(edge[0]),vertices.at(edge[1]),nullptr,BM_CREATE_NOP);
        }
        fill_faces(*this,source,cancel); BM_mesh_normals_update(value);
        BM_mesh_elem_index_ensure(value,BM_VERT|BM_EDGE|BM_FACE);
    } catch(...) { BM_mesh_free(value); throw; }
}
static Faces faces(BMesh* mesh) {
    Faces result; BMIter iter; BMFace* face;
    BM_ITER_MESH(face,&iter,mesh,BM_FACES_OF_MESH) {
        auto& row=result.emplace_back(); BMLoop* loop=BM_FACE_FIRST_LOOP(face);
        do { row.push_back(BM_elem_index_get(loop->v)); } while((loop=loop->next)!=BM_FACE_FIRST_LOOP(face));
    }
    return result;
}
std::shared_ptr<Mesh> result(BMesh* mesh,uint64_t cancel) {
    check_cancel(cancel); BM_mesh_elem_index_ensure(mesh,BM_VERT|BM_EDGE|BM_FACE);
    Points points; points.reserve(mesh->totvert); BMIter iter; BMVert* vertex;
    BM_ITER_MESH(vertex,&iter,mesh,BM_VERTS_OF_MESH) points.emplace_back(vertex->co[0],vertex->co[1],vertex->co[2]);
    auto output=make_mesh(points,faces(mesh),cancel); BMEdge* edge;
    output->ordered_edges.reserve(mesh->totedge);
    BM_ITER_MESH(edge,&iter,mesh,BM_EDGES_OF_MESH)
        output->ordered_edges.push_back({BM_elem_index_get(edge->v1),BM_elem_index_get(edge->v2)});
    return output;
}
}
