// Native cursor queries and de Casteljau subdivision of authored Bezier segments.
#include "construction_internal.hpp"

namespace af {
using Cubic=std::array<V3,4>;
struct CurveRay { V3 origin,direction; };
static V3 cubic_point(const Cubic& c,double t) {
    const double s=1-t;
    return s*s*s*c[0]+3*s*s*t*c[1]+3*s*t*t*c[2]+t*t*t*c[3];
}
static double ray_distance(const Cubic& c,double t,const CurveRay& ray) {
    const V3 offset=cubic_point(c,t)-ray.origin;
    const double along=std::max(0.0,offset.dot(ray.direction));
    return (offset-along*ray.direction).squaredNorm();
}
static double refine(const Cubic& c,const CurveRay& ray,double left,double right) {
    constexpr double ratio=0.6180339887498948482;
    double a=right-ratio*(right-left),b=left+ratio*(right-left);
    double fa=ray_distance(c,a,ray),fb=ray_distance(c,b,ray);
    for(int i=0;i<36;++i) {
        if(fa<fb) { right=b; b=a; fb=fa; a=right-ratio*(right-left); fa=ray_distance(c,a,ray); }
        else { left=a; a=b; fa=fb; b=left+ratio*(right-left); fb=ray_distance(c,b,ray); }
    }
    return (left+right)*0.5;
}
static double closest_parameter(const Cubic& c,const CurveRay& ray) {
    std::array<double,33> distances{};
    for(int i=0;i<=32;++i) distances[i]=ray_distance(c,double(i)/32,ray);
    double best=distances[0]<distances[32]?0:1,score=std::min(distances[0],distances[32]);
    for(int i=0;i<=32;++i) if(distances[i]<=distances[std::max(0,i-1)]&&distances[i]<=distances[std::min(32,i+1)]) {
        const double t=refine(c,ray,double(std::max(0,i-1))/32,double(std::min(32,i+1))/32);
        const double value=ray_distance(c,t,ray);
        if(value<score) { best=t; score=value; }
    }
    return best;
}
static int closest_curve(const double* cubics,int count,const CurveRay& ray,double* output) {
    double best=std::numeric_limits<double>::infinity(); int index=-1;
    for(int i=0;i<count;++i) {
        const double* p=cubics+12*i; const Cubic c{V3(p),V3(p+3),V3(p+6),V3(p+9)};
        const double t=closest_parameter(c,ray),distance=ray_distance(c,t,ray);
        const V3 point=cubic_point(c,t);
        if(distance>=best||(point-ray.origin).dot(ray.direction)<0) continue;
        best=distance; index=i; output[0]=t;
        for(int axis=0;axis<3;++axis) output[axis+1]=point[axis];
        output[4]=std::sqrt(distance);
    }
    return index;
}
static void split_handles(double* a,double* b,double* middle,double t) {
    const V3 p(a),q(a+6),r(b+3),s(b);
    const V3 pq=(1-t)*p+t*q,qr=(1-t)*q+t*r,rs=(1-t)*r+t*s;
    const V3 left=(1-t)*pq+t*qr,right=(1-t)*qr+t*rs,center=(1-t)*left+t*right;
    for(int axis=0;axis<3;++axis) {
        a[axis+6]=pq[axis]; b[axis+3]=rs[axis]; middle[axis]=center[axis];
        middle[axis+3]=left[axis]; middle[axis+6]=right[axis];
    }
    middle[9]=(1-t)*a[9]+t*b[9]; middle[10]=(1-t)*a[10]+t*b[10];
    a[11]=a[12]=b[11]=b[12]=middle[11]=middle[12]=2;
}
static void subdivide(const double* data,int count,int closed,int segment,double t,double* output) {
    if(count<2||segment<0||segment>=count-(closed?0:1)||!std::isfinite(t)||t<=0||t>=1)
        throw std::runtime_error("Subdivision requires a valid segment and an interior parameter.");
    std::vector<double> resolved(data,data+count*13);
    if(af_curve_handles(resolved.data(),count,closed)) throw std::runtime_error(af_last_error());
    for(int i=0;i<count;++i) {
        resolved[i*13+11]=int(resolved[i*13+11])%4; resolved[i*13+12]=int(resolved[i*13+12])%4;
        std::copy_n(resolved.data()+i*13,13,output+(i+(i>segment))*13);
    }
    const int next=segment+1==count?0:segment+2;
    split_handles(output+segment*13,output+next*13,output+(segment+1)*13,t);
}
}
int af_curve_closest(const double* cubics,int count,const double* origin,const double* direction,double* output) {
    const af::V3 ray(direction);
    if(count<1||!cubics||!ray.allFinite()||ray.norm()<1e-20) return -1;
    return af::closest_curve(cubics,count,{af::V3(origin),ray.normalized()},output);
}
int af_curve_split(const double* points,int count,int closed,int segment,double t,double* output) {
    try {
        af::subdivide(points,count,closed,segment,t,output); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
