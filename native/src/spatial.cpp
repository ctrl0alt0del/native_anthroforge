#include "mesh_internal.hpp"
#include <igl/Hit.h>

namespace af {
Surface::Surface(const Mesh& mesh,const M4& matrix):triangles(&mesh.triangles) {
    if(!mesh.prepared) throw std::runtime_error("Surface queries require a finalized mesh.");
    vertices=(mesh.vertices*matrix.block<3,3>(0,0).transpose()).rowwise()+matrix.block<3,1>(0,3).transpose();
    if(triangles->rows()) tree.init(vertices,*triangles);
}
V3 barycentric(const V3& p,const V3& a,const V3& b,const V3& c) {
    const V3 v0=b-a,v1=c-a,v2=p-a;
    const double d00=v0.dot(v0),d01=v0.dot(v1),d11=v1.dot(v1),den=d00*d11-d01*d01;
    if(std::abs(den)<1e-30) throw std::runtime_error("Degenerate attachment triangle.");
    const double v=(d11*v2.dot(v0)-d01*v2.dot(v1))/den;
    const double w=(d00*v2.dot(v1)-d01*v2.dot(v0))/den;
    return {1-v-w,v,w};
}
Hit nearest(const Surface& surface,const V3& point) {
    if(!surface.triangles->rows()) throw std::runtime_error("No usable attachment surface: geometry is empty.");
    Hit hit; Eigen::RowVector3d nearest;
    hit.distance=surface.tree.squared_distance(surface.vertices,*surface.triangles,point.transpose(),hit.triangle,nearest);
    hit.point=nearest.transpose();
    if(hit.triangle<0) throw std::runtime_error("No usable attachment surface.");
    const auto tri=surface.triangles->row(hit.triangle);
    hit.weights=barycentric(hit.point,surface.vertices.row(tri[0]),surface.vertices.row(tri[1]),surface.vertices.row(tri[2]));
    return hit;
}
static int closest_corner(const Mesh& mesh,const M4& matrix,int polygon,const V3& world) {
    int closest=-1; double distance=std::numeric_limits<double>::infinity();
    for(auto i=mesh.offsets[polygon];i<mesh.offsets[polygon+1];++i) {
        const int vertex=int(mesh.corners[i]);
        const double candidate=(point(matrix,mesh.vertices.row(vertex))-world).squaredNorm();
        if(candidate<distance) { closest=vertex; distance=candidate; }
    }
    return closest;
}
static void write_hit(const Mesh& mesh,const M4& matrix,const V3& origin,const igl::Hit& hit,double* output) {
    const auto triangle=mesh.triangles.row(hit.id);
    const V3 weights(1-hit.u-hit.v,hit.u,hit.v);
    V3 local=V3::Zero();
    for(int i=0;i<3;++i) local+=weights[i]*mesh.vertices.row(triangle[i]).transpose();
    const V3 world=point(matrix,local);
    output[0]=(world-origin).norm(); output[1]=double(mesh.polygons[hit.id]);
    output[2]=hit.id; output[3]=closest_corner(mesh,matrix,int(mesh.polygons[hit.id]),world);
    for(int i=0;i<3;++i) { output[4+i]=world[i]; output[7+i]=weights[i]; }
}
static void extend_bounds(Eigen::AlignedBox3d& bounds,const Mesh& mesh,const M4& matrix) {
    for(int corner=0;corner<8;++corner) {
        V3 local;
        for(int axis=0;axis<3;++axis) local[axis]=mesh.bounds[axis+((corner&(1<<axis))?3:0)];
        bounds.extend(point(matrix,local));
    }
}
int pick_surface(const Mesh& mesh,const M4& world,const V3& start,const V3& ray,double* output) {
    if(!mesh.prepared) throw std::runtime_error("Picking requires a finalized mesh.");
    const M4 inverse=world.inverse();
    const Eigen::RowVector3d local_start=point(inverse,start).transpose();
    const Eigen::RowVector3d local_ray=(inverse.block<3,3>(0,0)*ray).transpose();
    igl::Hit hit;
    if(!intersect_ray(mesh,local_start.transpose(),local_ray.transpose(),hit)) return 0;
    write_hit(mesh,world,start,hit,output); return 1;
}
}
int af_scene_bounds(int count,const uint64_t* meshes,const double* matrices,double* output) {
    try {
        if(count<1) throw std::runtime_error("Scene bounds require at least one mesh.");
        Eigen::AlignedBox3d bounds;
        for(int i=0;i<count;++i) af::extend_bounds(bounds,*af::mesh(meshes[i]),Eigen::Map<const af::M4>(matrices+16*i));
        if(!bounds.min().allFinite()||!bounds.max().allFinite()) throw std::runtime_error("Scene bounds must be finite.");
        for(int axis=0;axis<3;++axis) { output[axis]=bounds.min()[axis]; output[axis+3]=bounds.max()[axis]; }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_pick(uint64_t handle,const double* matrix,const double* origin,const double* direction,double* output) {
    try {
        const auto mesh=af::mesh(handle); const af::M4 world=Eigen::Map<const af::M4>(matrix);
        return af::pick_surface(*mesh,world,Eigen::Map<const af::V3>(origin),Eigen::Map<const af::V3>(direction),output);
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
int af_scene_pick(int count,const uint64_t* meshes,const double* matrices,
                   const double* origin,const double* direction,double* hits) {
    int found=0;
    for(int i=0;i<count;++i) {
        const int result=af_pick(meshes[i],matrices+16*i,origin,direction,hits+11*found+1);
        if(result<0) return -1;
        if(result) { hits[11*found]=i; ++found; }
    }
    return found;
}
int af_surface_normal(uint64_t handle,const double* matrix,int triangle,double* output) {
    try {
        const auto mesh=af::mesh(handle); const af::M4 world=Eigen::Map<const af::M4>(matrix);
        if(triangle<0||triangle>=mesh->triangles.rows()) throw std::runtime_error("Invalid surface triangle.");
        const auto face=mesh->triangles.row(triangle);
        const af::V3 a=mesh->vertices.row(face[1])-mesh->vertices.row(face[0]);
        const af::V3 b=mesh->vertices.row(face[2])-mesh->vertices.row(face[0]);
        const af::V3 normal=world.block<3,3>(0,0).inverse().transpose()*a.cross(b);
        if(!normal.allFinite()||normal.norm()<1e-15) throw std::runtime_error("Degenerate surface normal.");
        Eigen::Map<af::V3> result(output); result=normal.normalized(); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
