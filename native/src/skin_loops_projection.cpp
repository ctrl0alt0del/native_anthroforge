// Maintained addon annuli projection/resampling policy, on owned native inputs.
#include "skin_loops.hpp"
#include <numeric>
namespace af::skin_loops {
Plane plane(const double* values) {
    if(!values) return {};
    const V3 origin(values),normal(values+3);
    if(!origin.allFinite()||!normal.allFinite()||normal.norm()<1e-12)
        throw std::runtime_error("Invalid skin topology symmetry plane.");
    return {true,origin,normal.normalized()};
}
Context::Context(const Mesh& source,const double* values,uint64_t token):
    mesh(source),surface(source,M4::Identity()),cancel(token),plane(skin_loops::plane(values)) {
    check_cancel(cancel);
    diagonal=(mesh.vertices.colwise().maxCoeff()-mesh.vertices.colwise().minCoeff()).norm();
    if(!std::isfinite(diagonal)||diagonal<1e-12) throw std::runtime_error("Skin guide surface has no extent.");
}
std::shared_ptr<skin::PointIndex> point_index(const Vertices& points,uint64_t cancel) {
    std::vector<int> indices(points.rows()); std::iota(indices.begin(),indices.end(),0);
    return std::make_shared<skin::PointIndex>(points,indices,cancel);
}
Vertices authored(const Path& path,const M4& frame,uint64_t cancel) {
    const auto count=path.samples.size()/11;
    if(!path.closed||count<3||count>1048576||!frame.allFinite()||std::abs(frame.block<3,3>(0,0).determinant())<1e-18)
        throw std::runtime_error("Topology guide requires an accepted closed path and nonsingular frame.");
    Vertices result(count,3);
    for(size_t i=0;i<count;++i) {
        if(i%4096==0) check_cancel(cancel);
        result.row(i)=point(frame,V3(path.samples.data()+11*i));
    }
    return result;
}
double perimeter(const Vertices& points) {
    double length=0;
    for(int i=0;i<points.rows();++i) length+=(points.row((i+1)%points.rows())-points.row(i)).norm();
    return length;
}
Loop projected(Context& context,const Vertices& points) {
    Loop result; result.points.resize(points.rows(),3); result.normals.resize(points.rows(),3);
    for(int i=0;i<points.rows();++i) {
        if(i%256==0) check_cancel(context.cancel);
        const auto hit=nearest(context.surface,points.row(i));
        const auto ids=context.mesh.triangles.row(hit.triangle);
        const V3 a=context.mesh.vertices.row(ids[0]),b=context.mesh.vertices.row(ids[1]),c=context.mesh.vertices.row(ids[2]);
        result.points.row(i)=hit.point; result.normals.row(i)=(b-a).cross(c-a).normalized();
    }
    result.center=result.points.colwise().mean(); result.perimeter=perimeter(result.points);
    return result;
}
static std::vector<double> cumulative(const Vertices& points) {
    std::vector<double> lengths(points.rows()+1,0);
    for(int i=0;i<points.rows();++i) lengths[i+1]=lengths[i]+(points.row((i+1)%points.rows())-points.row(i)).norm();
    return lengths;
}
static void interpolate(const Loop& source,const std::vector<double>& lengths,double at,Loop& out,int row) {
    const int i=std::min(int(source.points.rows())-1,int(std::upper_bound(lengths.begin(),lengths.end(),at)-lengths.begin())-1);
    const int next=(i+1)%source.points.rows(); const double span=lengths[i+1]-lengths[i];
    const double factor=span>0?(at-lengths[i])/span:0;
    out.points.row(row)=(1-factor)*source.points.row(i)+factor*source.points.row(next);
    const V3 normal=(1-factor)*source.normals.row(i)+factor*source.normals.row(next);
    out.normals.row(row)=normal/(normal.norm()<1e-12?1:normal.norm());
}
Loop resampled(const Loop& source,int count,uint64_t cancel) {
    const auto lengths=cumulative(source.points);
    if(lengths.back()<1e-12) throw std::runtime_error("Topology guide has zero projected perimeter.");
    Loop result; result.points.resize(count,3); result.normals.resize(count,3);
    for(int i=0;i<count;++i) { check_cancel(cancel); interpolate(source,lengths,lengths.back()*i/count,result,i); }
    result.center=result.points.colwise().mean(); result.perimeter=perimeter(result.points);
    return result;
}
}
