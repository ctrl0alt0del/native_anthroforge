#include "skin_annuli.hpp"
#include <Eigen/SVD>
#include <complex>
#include <numeric>
namespace af::skin_annuli {
constexpr double pi=3.14159265358979323846;
Frame frame(const Vertices& points,const Plane& plane) {
    Frame out; out.center=points.colwise().mean();
    const Eigen::MatrixXd centered=points.rowwise()-out.center.transpose();
    const auto svd=Eigen::JacobiSVD<Eigen::MatrixXd>(centered,Eigen::ComputeThinV);
    out.first=svd.matrixV().col(0); out.second=svd.matrixV().col(1); out.normal=out.first.cross(out.second);
    if(!plane.enabled) return out;
    out.center-=plane.normal.dot(out.center-plane.origin)*plane.normal;
    const V3 last=svd.matrixV().col(2);
    out.normal=last-last.dot(plane.normal)*plane.normal;
    out.normal/=std::max(out.normal.norm(),1e-12); out.first=plane.normal;
    out.second=out.normal.cross(plane.normal); return out;
}
Eigen::MatrixXd smooth(const Eigen::MatrixXd& values,int harmonics) {
    const int n=int(values.rows()); Eigen::MatrixXd result=Eigen::MatrixXd::Zero(n,values.cols());
    for(int column=0;column<values.cols();++column) for(int k=0;k<=std::min(harmonics,n/2);++k) {
        std::complex<double> coefficient=0;
        for(int j=0;j<n;++j) coefficient+=values(j,column)*std::polar(1.0,-2*pi*k*j/n);
        coefficient/=n; const double factor=(k==0||2*k==n)?1:2;
        for(int j=0;j<n;++j) result(j,column)+=factor*(coefficient*std::polar(1.0,2*pi*k*j/n)).real();
    }
    return result;
}
static double radius_at(const std::vector<std::pair<double,double>>& values,double angle) {
    const auto next=std::upper_bound(values.begin(),values.end(),std::make_pair(angle,std::numeric_limits<double>::infinity()));
    if(next==values.begin()) return next->second;
    if(next==values.end()) return values.back().second;
    const auto& a=*(next-1); const auto& b=*next;
    return a.second+(b.second-a.second)*(angle-a.first)/(b.first-a.first);
}
static Eigen::VectorXd radii(const Vertices& points,const Frame& axes) {
    std::vector<std::pair<double,double>> values;
    for(int i=0;i<points.rows();++i) {
        const V3 delta=V3(points.row(i))-axes.center; const double x=delta.dot(axes.first),y=delta.dot(axes.second);
        values.emplace_back(std::atan2(y,x),std::hypot(x,y));
    }
    std::stable_sort(values.begin(),values.end(),[](const auto& a,const auto& b){return a.first<b.first;});
    const auto front=values.front(),back=values.back();
    values.insert(values.begin(),{back.first-2*pi,back.second}); values.emplace_back(front.first+2*pi,front.second);
    Eigen::VectorXd result(points.rows());
    for(int i=0;i<result.size();++i) result[i]=radius_at(values,-pi+2*pi*i/result.size());
    return smooth(result,8);
}
Loop ray_project(Context& context,const Vertices& points,const V3& normal) {
    auto out=skin_loops::projected(context,points);
    if(normal.squaredNorm()<1e-24) return out;
    for(int i=0;i<points.rows();++i) {
        check_cancel(context.cancel); const V3 origin=V3(points.row(i))+normal*context.diagonal; RayHit hit;
        if(!intersect_ray(context.mesh,origin,-normal,hit)||hit.t>2*context.diagonal) continue;
        out.points.row(i)=origin-normal*hit.t;
        out.normals.row(i)=surface_normal(context.mesh,M4::Identity(),hit.id);
    }
    return out;
}
static void planar_rings(Context& context,Patch& out,const Loop& a,const Loop& b,const Plane& plane) {
    Vertices both(a.points.rows()+b.points.rows(),3); both<<a.points,b.points; auto axes=frame(both,plane);
    const double dot=axes.normal.dot(V3((a.normals.colwise().mean()+b.normals.colwise().mean())/2));
    axes.normal*=dot>0?1:(dot<0?-1:0);
    const auto ra=radii(a.points,axes),rb=radii(b.points,axes);
    for(int row=0;row<rows;++row) {
        const double factor=double(row)/(rows-1); Vertices seeds(out.segments,3);
        for(int i=0;i<out.segments;++i) {
            const double radius=(1-factor)*std::max(ra[i],rb[i])+factor*std::min(ra[i],rb[i]),angle=-pi+2*pi*i/out.segments;
            seeds.row(i)=axes.center+radius*(std::cos(angle)*axes.first+std::sin(angle)*axes.second);
        }
        const auto ring=ray_project(context,seeds,axes.normal);
        out.points.middleRows(row*out.segments,out.segments)=ring.points; out.normals.middleRows(row*out.segments,out.segments)=ring.normals;
    }
}
Patch planar(Context& context,const Loop& outer,const Loop& inner) {
    Patch result; result.mode=1; result.segments=segment_count(outer,inner,context.diagonal);
    const auto a=skin_loops::resampled(outer,result.segments,context.cancel);
    const auto b=aligned(a,skin_loops::resampled(inner,result.segments,context.cancel));
    result.points.resize(rows*result.segments,3); result.normals.resize(rows*result.segments,3);
    const bool symmetric=symmetry_candidate(outer,inner,context.plane);
    planar_rings(context,result,a,b,symmetric?context.plane:Plane{});
    if(symmetric) symmetrize(context,result);
    finish(context,result); return result;
}
}
