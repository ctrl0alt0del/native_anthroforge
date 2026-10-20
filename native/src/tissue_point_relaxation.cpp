// SPDX-License-Identifier: GPL-3.0-or-later
// Port of af_soft_tissue_point.hpp, reusing owned native BVH queries.
#include "tissue_relaxation.hpp"

namespace af::tissue {
using Neighbors=std::vector<std::vector<int64_t>>;
struct PointContext {
    const Mesh& host;
    Surface surface;
    M4 frame,inverse;
    V3 center,gravity;
    Neighbors neighbors;
};
static Neighbors neighbors(const Mesh& rest) {
    Neighbors result(size_t(rest.vertices.rows()));
    for(const auto& row:mesh_edges(mesh_faces(rest),0)) {
        const auto [a,b]=row.first; result[size_t(a)].push_back(b); result[size_t(b)].push_back(a);
    }
    return result;
}
static PointContext context(const Mesh& rest,const Mesh& host,const AfTissueSource& source,const AfTissueRelax& s) {
    const M4 frame=Eigen::Map<const M4>(source.host_frame); const V3 gravity(s.gravity);
    const M4 base=Eigen::Map<const M4>(source.frame);
    return {host,Surface(host,M4::Identity()),frame,frame.inverse(),base.block<3,1>(0,3),
        gravity.norm()>1e-10?V3(gravity.normalized()):V3(0,0,-1),neighbors(rest)};
}
static void gravity(Vertices& points,const PointContext& context,const AfTissueRelax& s,uint64_t cancel) {
    for(int64_t i=0;i<points.rows();++i) {
        check_cancel(cancel); const V3 p=points.row(i),local=point(context.inverse,p);
        const double distance=(p-point(context.frame,nearest(context.surface,local).point)).norm();
        double step=(.002+.02*distance)*s.sagginess*10; if(s.limit>0) step=std::min(step,s.limit*.25);
        points.row(i)+=(context.gravity*step).transpose();
    }
}
static void viscosity(Vertices& points,const Neighbors& neighbors,double shape,uint64_t cancel) {
    Vertices next=points; const double alpha=(1-std::clamp(shape,0.,1.))*.18;
    for(size_t i=0;i<neighbors.size();++i) {
        check_cancel(cancel); const auto& row=neighbors[i]; if(row.empty()) continue;
        V3 sum=V3::Zero(); for(auto j:row) sum+=points.row(j).transpose();
        next.row(i)=(1-alpha)*points.row(i)+(alpha/row.size())*sum.transpose();
    }
    points=std::move(next);
}
static V3 clamp(const PointContext& context,const V3& p) {
    const V3 local=point(context.inverse,p),control=point(context.inverse,context.center),direction=control-local;
    if(direction.norm()<=1e-10) return p;
    RayHit hit;
    if(intersect_ray(context.host,local,direction,hit)&&hit.t<1) return point(context.frame,local+direction*hit.t);
    return p;
}
static void project(Vertices& points,const Mesh& rest,const PointContext& context,double limit,uint64_t cancel) {
    for(int64_t i=0;i<points.rows();++i) {
        check_cancel(cancel); V3 p=clamp(context,points.row(i));
        const V3 before=rest.vertices.row(i); const double drop=(p-before).dot(context.gravity);
        if(limit>0&&drop>limit) p-=context.gravity*(drop-limit);
        points.row(i)=p;
    }
}
Vertices relax_point(const Mesh& rest,const Constraints&,const AfTissueSource& source,const AfTissueRelax& s,double* report,uint64_t cancel) {
    if(!source.host) throw std::runtime_error("Point geometric relaxation requires its Anchor's accepted anatomical surface.");
    const auto host=mesh(source.host); const auto ctx=context(rest,*host,source,s); Vertices points=rest.vertices;
    for(int i=0;i<s.iterations;++i) {
        const Vertices previous=points; gravity(points,ctx,s,cancel); viscosity(points,ctx.neighbors,s.shape,cancel);
        project(points,rest,ctx,s.limit,cancel); const double change=(points-previous).rowwise().norm().maxCoeff();
        report[1]=i+1; report[2]=change; report[0]=change<1e-6?1:2;
        if(change<1e-6) break;
    }
    return points;
}
}
