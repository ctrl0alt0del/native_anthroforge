// SPDX-License-Identifier: GPL-3.0-or-later
// Signed mean-value coordinates (Floater 2003), with linear boundary limits.
// This implementation does not use libigl's explicitly marked "Broken" mvc routine.
#include "material_chart.hpp"

namespace af::material {
struct Differential { double value=0; V2 gradient=V2::Zero(); };
static double cross(const V2& a,const V2& b) { return a.x()*b.y()-a.y()*b.x(); }
static Differential quotient(double a,const V2& da,double b,const V2& db) {
    return {a/b,(da*b-a*db)/(b*b)};
}
static Differential half_angle(const V2& a,const V2& b) {
    const double ra=a.norm(),rb=b.norm(),c=cross(a,b),dot=a.dot(b);
    const V2 dc(a.y()-b.y(),b.x()-a.x()),product=-a*rb/ra-b*ra/rb;
    if(dot>=0) return quotient(c,dc,ra*rb+dot,product-a-b);
    return quotient(ra*rb-dot,product+a+b,c,dc);
}
static bool boundary_value(const Cage& cage,const V2& query,V2& result,uint64_t cancel) {
    for(size_t i=0;i<cage.source.size();++i) {
        check_cancel(cancel); const size_t j=(i+1)%cage.source.size();
        const V2 edge=cage.source[j]-cage.source[i],offset=query-cage.source[i];
        if(edge.squaredNorm()<1e-24) throw std::runtime_error("Patch correspondence has a degenerate edge.");
        const double t=offset.dot(edge)/edge.squaredNorm();
        if(t>=-1e-13&&t<=1+1e-13&&(offset-t*edge).norm()<1e-13) {
            result=(1-t)*cage.target[i]+t*cage.target[j]; return true;
        }
    }
    return false;
}
static Mapping interior(const Cage& cage,const V2& query,uint64_t cancel) {
    std::vector<Differential> angles; Mapping result; Differential total;
    for(size_t i=0;i<cage.source.size();++i) {
        check_cancel(cancel); angles.push_back(half_angle(cage.source[i]-query,cage.source[(i+1)%cage.source.size()]-query));
    }
    for(size_t i=0;i<cage.source.size();++i) {
        check_cancel(cancel); const auto& a=angles[(i+angles.size()-1)%angles.size()]; const auto& b=angles[i];
        const V2 delta=cage.source[i]-query; const double r=delta.norm();
        const auto w=quotient(a.value+b.value,a.gradient+b.gradient,r,-delta/r);
        total.value+=w.value; total.gradient+=w.gradient;
        result.point+=w.value*cage.target[i]; result.derivative+=cage.target[i]*w.gradient.transpose();
    }
    result.point/=total.value; result.derivative=(result.derivative-result.point*total.gradient.transpose())/total.value;
    return result;
}
static V2 position(const Cage& cage,const V2& query,uint64_t cancel) {
    V2 result;
    return boundary_value(cage,query,result,cancel)?result:interior(cage,query,cancel).point;
}
Mapping mean_value(const Cage& cage,const V2& query,uint64_t cancel) {
    Mapping result;
    if(!boundary_value(cage,query,result.point,cancel)) result=interior(cage,query,cancel);
    else {
        // Boundary derivatives use symmetric limits; positions remain exact edge interpolation.
        constexpr double step=1e-5;
        for(int i=0;i<2;++i) {
            const V2 d=step*V2::Unit(i);
            result.derivative.col(i)=(position(cage,query+d,cancel)-position(cage,query-d,cancel))/(2*step);
        }
    }
    if(!result.point.allFinite()||!result.derivative.allFinite()) throw std::runtime_error("Patch material mapping is singular; explicitly rebind.");
    return result;
}
}
