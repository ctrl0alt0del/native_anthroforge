#include "stacking_normal_support.hpp"

namespace af::stacking {
static Vertices base_normals(const Vertices& base,const Triangles& faces,std::atomic<bool>& cancel) {
    Vertices result=Vertices::Zero(base.rows(),3);
    for(int f=0;f<faces.rows();++f) {
        if(cancel) throw std::runtime_error("PAIR_CANCELLED");
        const auto ids=faces.row(f);
        const V3 ab=base.row(ids[1])-base.row(ids[0]),ac=base.row(ids[2])-base.row(ids[0]);
        const V3 area=ab.cross(ac);
        for(int j=0;j<3;++j) result.row(ids[j])+=area;
    }
    return result;
}
static NormalSupport support(const Mesh& mesh,const V3& origin,V3 normal,double tolerance) {
    NormalSupport result;
    if(normal.norm()<1e-15) return result;
    normal.normalize(); RayHit first,last;
    if(!intersect_ray_span(mesh,origin,normal,first,last)||last.t-first.t<=tolerance) return result;
    result.face=last.id; result.weights={1-last.u-last.v,last.u,last.v};
    result.normal=normal; result.distance=last.t; result.point=origin+last.t*normal;
    return result;
}
std::vector<NormalSupport> ambiguous_support(const Vertices& base,const Triangles& faces,
    const Vertices& provider,const Triangles& provider_faces,std::atomic<bool>& cancel) {
    Mesh target; target.vertices=provider; target.triangles=provider_faces;
    if(provider_faces.rows()) target.tree.init(target.vertices,target.triangles);
    const auto normals=base_normals(base,faces,cancel);
    const double tolerance=std::max(1e-12,(provider.colwise().maxCoeff()-provider.colwise().minCoeff()).norm()*1e-9);
    std::vector<NormalSupport> result(size_t(base.rows()));
    for(int i=0;i<base.rows();++i) {
        if(cancel) throw std::runtime_error("PAIR_CANCELLED");
        result[size_t(i)]=support(target,base.row(i),normals.row(i),tolerance);
    }
    return result;
}
}
