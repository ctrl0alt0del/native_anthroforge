#include "mesh_internal.hpp"
#include <mapbox/earcut.hpp>
#include <array>
#include <set>

namespace af {
// Blender 5.0.1 mesh_tessellate.cc / is_quad_flip_v3_first_third_fast,
// NaN Holding BV / Blender Authors, GPL-2.0-or-later; initial connectivity only.
static std::vector<uint32_t> quad_triangles(const Mesh& mesh,const std::vector<int64_t>& face) {
    const V3 origin=mesh.vertices.row(face[0]);
    const V3 a=mesh.vertices.row(face[1])-origin.transpose();
    const V3 b=mesh.vertices.row(face[2])-origin.transpose();
    const V3 c=mesh.vertices.row(face[3])-origin.transpose();
    if(a.cross(b).dot(c.cross(b))>0) return {0,1,3,1,2,3};
    return {0,1,2,0,2,3};
}
static V3 polygon_normal(const Mesh& mesh,const std::vector<int64_t>& face) {
    V3 normal=V3::Zero();
    const V3 anchor=mesh.vertices.row(face[0]);
    for(size_t i=1;i+1<face.size();++i) {
        const V3 a=mesh.vertices.row(face[i]), b=mesh.vertices.row(face[i+1]);
        normal+=(a-anchor).cross(b-anchor);
    }
    if(normal.norm()<=1e-20) throw std::runtime_error("Degenerate polygon.");
    return normal.normalized();
}
static void validate_face(const Mesh& mesh,const std::vector<int64_t>& face) {
    if(face.size()<3) throw std::runtime_error("A polygon needs at least three corners.");
    std::set<int64_t> indices;
    for(auto index:face) {
        if(index<0||index>=mesh.vertices.rows()) throw std::runtime_error("Invalid polygon vertex index.");
        if(!indices.insert(index).second) throw std::runtime_error("Repeated polygon vertex index.");
    }
}
static std::vector<uint32_t> triangulate(const Mesh& mesh,const std::vector<int64_t>& face) {
    if(mesh.generated&&face.size()==3) return {0,1,2};
    if(mesh.generated&&face.size()==4) return quad_triangles(mesh,face);
    const V3 normal=polygon_normal(mesh,face);
    if(face.size()==3) return {0,1,2};
    Eigen::Index dropped; normal.cwiseAbs().maxCoeff(&dropped);
    const int a=(int(dropped)+1)%3, b=(int(dropped)+2)%3;
    std::vector<std::vector<std::array<double,2>>> polygon(1);
    for(auto index:face) polygon[0].push_back({mesh.vertices(index,a),mesh.vertices(index,b)});
    auto indices=mapbox::earcut<uint32_t>(polygon);
    if(indices.size()!=3*(face.size()-2)) throw std::runtime_error("Polygon cannot be triangulated safely.");
    if(normal[dropped]<0)
        for(size_t i=0;i<indices.size();i+=3) std::swap(indices[i+1],indices[i+2]);
    return indices;
}
static void add_face(Mesh& mesh,const std::vector<int64_t>& face,std::vector<Eigen::Vector3i>& tris,int id) {
    validate_face(mesh,face);
    const auto indices=triangulate(mesh,face);
    for(size_t i=0;i<indices.size();i+=3) {
        tris.emplace_back(int(face[indices[i]]),int(face[indices[i+1]]),int(face[indices[i+2]]));
        mesh.polygons.push_back(id);
    }
    mesh.corners.insert(mesh.corners.end(),face.begin(),face.end());
    mesh.offsets.push_back(int64_t(mesh.corners.size()));
}
static void append_triangle(const Mesh& mesh,int index,std::vector<float>& output) {
    const V3 a=mesh.vertices.row(mesh.triangles(index,0)), b=mesh.vertices.row(mesh.triangles(index,1));
    const V3 c=mesh.vertices.row(mesh.triangles(index,2));
    V3 normal=(b-a).cross(c-a);
    if(normal.norm()>1e-20) normal.normalize();
    else if(mesh.generated) normal=V3::Zero();
    else throw std::runtime_error("Degenerate render triangle.");
    for(const V3& point:{a,b,c}) {
        for(int axis=0;axis<3;++axis) output.push_back(float(point[axis]));
        for(int axis=0;axis<3;++axis) output.push_back(float(normal[axis]));
    }
}
static void render_chunks(Mesh& mesh,uint64_t cancel) {
    constexpr int triangles_per_chunk=16384;
    for(int first=0;first<mesh.triangles.rows();first+=triangles_per_chunk) {
        check_cancel(cancel);
        auto& chunk=mesh.chunks.emplace_back();
        const int last=std::min(first+triangles_per_chunk,int(mesh.triangles.rows()));
        chunk.reserve(size_t(last-first)*18);
        for(int i=first;i<last;++i) append_triangle(mesh,i,chunk);
    }
}
void rebuild_mesh(Mesh& mesh,uint64_t cancel) {
    mesh.chunks.clear();
    std::fill(mesh.bounds,mesh.bounds+6,0.0);
    af_bounds3d(mesh.vertices.data(),mesh.vertices.rows(),mesh.bounds);
    check_cancel(cancel);
    if(mesh.triangles.rows()) mesh.tree.init(mesh.vertices,mesh.triangles);
    render_chunks(mesh,cancel);
    mesh.prepared=true;
}
void prepare_mesh(Mesh& mesh,const Faces& faces,uint64_t cancel,bool complete) {
    const bool empty=mesh.generated&&mesh.vertices.rows()==0&&faces.empty();
    if(!empty&&(mesh.vertices.rows()==0||!mesh.vertices.allFinite()||faces.empty()))
        throw std::runtime_error("Mesh needs finite vertices and polygon faces.");
    std::vector<Eigen::Vector3i> triangles; mesh.offsets={0};
    for(size_t i=0;i<faces.size();++i) {
        check_cancel(cancel); add_face(mesh,faces[i],triangles,int(i));
    }
    mesh.triangles.resize(triangles.size(),3);
    for(size_t i=0;i<triangles.size();++i) mesh.triangles.row(i)=triangles[i];
    if(complete) rebuild_mesh(mesh,cancel);
    else af_bounds3d(mesh.vertices.data(),mesh.vertices.rows(),mesh.bounds);
}
}
