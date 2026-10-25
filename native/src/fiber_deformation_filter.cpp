#include "fiber_deformation.hpp"
#include <array>
namespace af::fiber {
using Moment=std::array<long double,6>;
static constexpr int choose[6][6]={{1},{1,1},{1,2,1},{1,3,3,1},{1,4,6,4,1},{1,5,10,10,5,1}};
static constexpr int polynomial[6]={1,0,-10,20,-15,4};
static double owner_weight(const AfFiberReference& in,int row,int owner) {
    double result=0;
    for(int slot=0;slot<2;++slot) if(in.owners[2*row+slot]==owner) result+=in.weights[2*row+slot];
    return result;
}
static void direct(Preparation& v,const AfFiberReference& in,uint64_t cancel) {
    const int n=int(v.path->parameters.size());
    for(int i=0;i<n;++i) {
        check_cancel(cancel);
        for(int j=0;j<n;++j) {
            const double w=kernel(distance(v,v.arc[size_t(i)],v.arc[size_t(j)])/v.width)*v.mass[size_t(j)];
            for(int k=0;k<2;++k) if(in.weights[2*j+k]>0)
                v.weights(i,in.owners[2*j+k])+=w*in.weights[2*j+k];
        }
    }
}
static std::vector<Moment> moments(const Preparation& v,const AfFiberReference& in,int owner,uint64_t cancel) {
    const int n=int(v.path->parameters.size()); std::vector<Moment> sums(size_t(n+1),Moment{});
    for(int i=0;i<n;++i) {
        check_cancel(cancel); long double value=owner_weight(in,i,owner)*v.mass[size_t(i)];
        for(int k=0;k<6;++k) {
            sums[size_t(i+1)][k]=sums[size_t(i)][k]+value;
            value*=v.arc[size_t(i)]/v.width;
        }
    }
    return sums;
}
static long double integral(const std::vector<Moment>& sums,int begin,int end,long double center,int sign) {
    if(begin==end) return 0;
    long double result=0; Moment powers{1,center,0,0,0,0};
    for(int k=2;k<6;++k) powers[k]=powers[k-1]*center;
    for(int k=0;k<6;++k) for(int j=0;j<=k;++j) {
        const int direction=((sign<0&&k%2)?-1:1)*(j%2?-1:1);
        result+=polynomial[k]*choose[k][j]*direction*powers[k-j]*(sums[size_t(end)][j]-sums[size_t(begin)][j]);
    }
    return result;
}
static double window(const Preparation& v,const std::vector<Moment>& sums,double center) {
    const auto first=v.arc.begin(),last=first+v.path->parameters.size();
    const int begin=int(std::lower_bound(first,last,center-v.width)-first);
    const int middle=int(std::upper_bound(first,last,center)-first);
    const int end=int(std::upper_bound(first,last,center+v.width)-first);
    return double(integral(sums,begin,middle,center/v.width,1)+integral(sums,middle,end,center/v.width,-1));
}
static void filtered(Preparation& v,const AfFiberReference& in,uint64_t cancel) {
    const int n=int(v.path->parameters.size());
    for(int b=0;b<in.surfaces;++b) {
        const auto sums=moments(v,in,b,cancel);
        for(int i=0;i<n;++i) {
            check_cancel(cancel); const double center=v.arc[size_t(i)];
            double value=window(v,sums,center);
            if(v.path->closed) value+=window(v,sums,center-v.length)+window(v,sums,center+v.length);
            v.weights(i,b)=std::max(0.0,value); // Roundoff in the nonnegative compact kernel.
        }
    }
}
void smooth_weights(Preparation& v,const AfFiberReference& in,uint64_t cancel) {
    // Same degree-five compact convolution; prefix moments avoid quadratic cold preparation.
    if(v.path->parameters.size()<=512) direct(v,in,cancel); else filtered(v,in,cancel);
    for(int i=0;i<int(v.path->parameters.size());++i) {
        const double sum=v.weights.row(i).sum();
        if(!std::isfinite(sum)||sum<=0) throw std::runtime_error("Fiber support weights have no finite mass.");
        v.weights.row(i)/=sum;
    }
}
}
