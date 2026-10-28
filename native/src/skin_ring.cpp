#include "skin_ring.hpp"
#include <Eigen/Eigenvalues>
namespace af::skin_ring {
Projection project(const Vertices& ring,double scale) {
    Projection out; out.center=ring.colwise().mean();
    const Vertices relative=ring.rowwise()-out.center.transpose();
    const Eigen::SelfAdjointEigenSolver<M3> solver(relative.transpose()*relative);
    if(solver.info()!=Eigen::Success) throw std::runtime_error("Topology ring plane decomposition failed.");
    out.first=solver.eigenvectors().col(2); out.second=solver.eigenvectors().col(1); out.normal=solver.eigenvectors().col(0);
    out.local.resize(ring.rows(),3); out.local.col(0)=relative*out.first*scale;
    out.local.col(1)=relative*out.second*scale; out.local.col(2)=relative*out.normal;
    out.radius=relative.rowwise().norm().maxCoeff(); return out;
}
bool inside(const Projection& projection,const V3& point) {
    const V3 delta=point-projection.center; const double x=delta.dot(projection.first),y=delta.dot(projection.second);
    bool result=false;
    for(int i=0;i<projection.local.rows();++i) {
        const auto a=projection.local.row(i),b=projection.local.row((i+1)%projection.local.rows());
        const double dy=b[1]-a[1],denom=std::abs(dy)<1e-12?1e-12:dy;
        if((a[1]>y)!=(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/denom+a[0]) result=!result;
    }
    return result;
}
bool centered(const Vertices& points,const skin_loops::Plane& plane,double diagonal) {
    return plane.enabled&&std::abs(plane.normal.dot(V3(points.colwise().mean())-plane.origin))<=1e-5*diagonal;
}
Vertices samples(const Vertices& points,int count,uint64_t cancel) {
    skin_loops::Loop loop; loop.points=points; loop.normals=Vertices::Zero(points.rows(),3);
    return skin_loops::resampled(loop,count,cancel).points;
}
Vertices rolled(const Vertices& points,int start,bool reverse) {
    Vertices out(points.rows(),3); const int count=int(points.rows());
    for(int i=0;i<count;++i) out.row(i)=points.row(((reverse?-i:i)+start+count)%count);
    return out;
}
Vertices canonical(const Vertices& points) {
    Eigen::Index index; points.col(2).maxCoeff(&index); return rolled(points,int(index));
}
Vertices aligned(const Vertices& reference,const Vertices& points,uint64_t cancel) {
    const int count=2*int(std::max(reference.rows(),points.rows())); const auto target=samples(reference,count,cancel);
    Vertices best; double error=std::numeric_limits<double>::infinity();
    for(int reverse=0;reverse<2;++reverse) for(int start=0;start<points.rows();++start) {
        check_cancel(cancel); auto candidate=rolled(points,reverse?-start+int(points.rows()):start,reverse!=0);
        const double cost=(target-samples(candidate,count,cancel)).rowwise().norm().sum();
        if(cost<error) { error=cost; best=std::move(candidate); }
    }
    return best;
}
}
