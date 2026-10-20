// Numerical experiment only; not linked into the application.
// Compare exact station unions with fixed consumer density on identical native routes.
#include <algorithm>
#include <array>
#include <cmath>
#include <vector>

using Point = std::array<double,3>;
using Points = std::vector<Point>;
using Axis = std::vector<double>;
static Point mix(const Point& a,const Point& b,double t) {
    Point result{};
    for(int i=0;i<3;++i) result[i]=a[i]*(1-t)+b[i]*t;
    return result;
}
static double squared(const Point& a,const Point& b) {
    double result=0;
    for(int i=0;i<3;++i) result+=(a[i]-b[i])*(a[i]-b[i]);
    return result;
}
static Points points(const double* data,int count) {
    Points result;
    for(int i=0;i<count;++i) result.push_back({data[3*i],data[3*i+1],data[3*i+2]});
    return result;
}
static Axis stations(const Points& row) {
    Axis result{0};
    for(size_t i=1;i<row.size();++i) result.push_back(result.back()+std::sqrt(squared(row[i],row[i-1])));
    const double length=result.back();
    for(auto& value:result) value/=length;
    return result;
}
static Point sample(const Points& row,const Axis& axis,double t) {
    const auto found=std::lower_bound(axis.begin()+1,axis.end(),t);
    const size_t b=std::min(size_t(found-axis.begin()),axis.size()-1),a=b-1;
    return mix(row[a],row[b],(t-axis[a])/(axis[b]-axis[a]));
}
static Axis layout(const Axis& a,const Axis& b,int count) {
    Axis result;
    if(count) for(int i=0;i<count;++i) result.push_back(double(i)/(count-1));
    else {
        result=a; result.insert(result.end(),b.begin(),b.end());
        std::sort(result.begin(),result.end());
        result.erase(std::unique(result.begin(),result.end(),[](double x,double y){return std::abs(x-y)<1e-12;}),result.end());
    }
    return result;
}
static Points resample(const Points& row,const Axis& source,const Axis& target) {
    Points result;
    for(double t:target) result.push_back(sample(row,source,t));
    return result;
}
static void store(const Points& a,const Points& b,int strips,double* output) {
    for(int i=0;i<=strips;++i) for(size_t j=0;j<a.size();++j) {
        const auto p=mix(a[j],b[j],double(i)/strips);
        std::copy(p.begin(),p.end(),output+3*(i*a.size()+j));
    }
}
extern "C" __declspec(dllexport) int compare(
    const double* first,int n,const double* second,int m,int count,int strips,
    double along,double across,double* vertices,double* axis,double* marker) {
    const auto a=points(first,n),b=points(second,m);
    const auto u=stations(a),v=stations(b),target=layout(u,v,count);
    const auto x=resample(a,u,target),y=resample(b,v,target);
    store(x,y,strips,vertices); std::copy(target.begin(),target.end(),axis);
    const auto p=mix(sample(x,target,along),sample(y,target,along),across);
    std::copy(p.begin(),p.end(),marker);
    return int(target.size());
}
static double distance(const Point& p,const Point& a,const Point& b) {
    double product=0;
    for(int i=0;i<3;++i) product+=(p[i]-a[i])*(b[i]-a[i]);
    const double t=std::clamp(product/std::max(squared(a,b),1e-30),0.,1.);
    return std::sqrt(squared(p,mix(a,b,t)));
}
extern "C" __declspec(dllexport) double corner_error(const double* data,int n,const double* sampled,int m) {
    const auto source=points(data,n),row=points(sampled,m); double worst=0;
    for(const auto& p:source) {
        double best=1e300;
        for(size_t j=1;j<row.size();++j) best=std::min(best,distance(p,row[j-1],row[j]));
        worst=std::max(worst,best);
    }
    return worst;
}
