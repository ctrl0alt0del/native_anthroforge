// SPDX-License-Identifier: GPL-3.0-or-later
#include "mesh_internal.hpp"

namespace af {
struct PickRay { V3 origin,direction,shear; int x,y,z; };
static PickRay pick_ray(const V3& origin,const V3& direction) {
    Eigen::Index axis; direction.cwiseAbs().maxCoeff(&axis);
    const int z=int(axis),x=(z+1)%3,y=(x+1)%3;
    return {origin,direction,{-direction[x]/direction[z],-direction[y]/direction[z],1/direction[z]},x,y,z};
}
static V3 projected(const V3& vertex,const PickRay& ray) {
    const V3 p=vertex-ray.origin;
    return {p[ray.x]+ray.shear.x()*p[ray.z],p[ray.y]+ray.shear.y()*p[ray.z],p[ray.z]*ray.shear.z()};
}
static bool ray_box(const Eigen::AlignedBox3d& box,const V3& origin,const V3& ray,double limit) {
    double near=0,far=limit;
    for(int axis=0;axis<3;++axis) {
        if(ray[axis]==0) {
            if(origin[axis]<box.min()[axis]||origin[axis]>box.max()[axis]) return false;
            continue; // A boundary-parallel ray must not evaluate 0 * infinity.
        }
        double a=(box.min()[axis]-origin[axis])/ray[axis];
        double b=(box.max()[axis]-origin[axis])/ray[axis];
        if(a>b) std::swap(a,b);
        near=std::max(near,a); far=std::min(far,b);
        if(near>far) return false;
    }
    return far>0;
}
static bool triangle_hit(const V3& a,const V3& b,const V3& c,int face,RayHit& best) {
    // Ray-space edge functions share identical endpoint arithmetic across adjacent faces.
    // Woop/Benthin/Wald (2013), https://jcgt.org/published/0002/01/05/.
    const V3 edge(b.x()*c.y()-b.y()*c.x(),c.x()*a.y()-c.y()*a.x(),a.x()*b.y()-a.y()*b.x());
    if(edge.minCoeff()<0&&edge.maxCoeff()>0) return false;
    const double det=edge.sum();
    if(det==0) return false;
    const double t=edge.dot(V3(a.z(),b.z(),c.z()))/det;
    if(t<=0||t>=best.t) return false;
    best={face,edge.y()/det,edge.z()/det,t};
    return true;
}
static bool leaf_hit(const Mesh& mesh,int face,const PickRay& ray,RayHit& best) {
    const auto triangle=mesh.triangles.row(face);
    const V3 a=projected(mesh.vertices.row(triangle[0]),ray);
    const V3 b=projected(mesh.vertices.row(triangle[1]),ray);
    const V3 c=projected(mesh.vertices.row(triangle[2]),ray);
    return triangle_hit(a,b,c,face,best);
}
static bool ray_tree(const Mesh& mesh,const igl::AABB<Vertices,3>& tree,
                     const PickRay& ray,RayHit& best) {
    if(!ray_box(tree.m_box,ray.origin,ray.direction,best.t)) return false;
    if(tree.is_leaf()) return leaf_hit(mesh,tree.m_primitive,ray,best);
    const bool left=ray_tree(mesh,*tree.m_left,ray,best);
    const bool right=ray_tree(mesh,*tree.m_right,ray,best);
    return left||right;
}
bool intersect_ray(const Mesh& mesh,const V3& origin,const V3& ray,RayHit& hit) {
    if(!origin.allFinite()||!ray.allFinite()||ray.squaredNorm()==0)
        throw std::runtime_error("Picking requires a finite nonzero ray.");
    hit.t=std::numeric_limits<double>::infinity();
    if(!mesh.triangles.rows()) return false;
    return ray_tree(mesh,mesh.tree,pick_ray(origin,ray),hit);
}
}
