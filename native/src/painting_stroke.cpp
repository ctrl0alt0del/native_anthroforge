#include "painting_internal.hpp"
namespace af::painting {
using V2=Eigen::Vector2d;
static double distance(const V2& point,const double* samples,int count) {
    double result=(point-V2(samples)).squaredNorm();
    for(int i=1;i<count;++i) {
        const V2 a(samples+2*(i-1)),edge=V2(samples+2*i)-a;
        const double t=edge.squaredNorm()>0?std::clamp((point-a).dot(edge)/edge.squaredNorm(),0.0,1.0):0;
        result=std::min(result,(point-a-t*edge).squaredNorm());
    }
    return std::sqrt(result);
}
static std::vector<double> coverage(const Prepared& data,const double* samples,int count,const double* settings,uint64_t cancel) {
    std::vector<double> covered(size_t(data.count),0);
    for(int64_t i=0;i<data.projected.rows();++i) {
        check_cancel(cancel);
        if(data.projected(i,2)<=1e-9||(!settings[4]&&!data.visible[size_t(i)])) continue;
        const double t=std::max(0.0,1-distance(data.projected.row(i).head<2>(),samples,count)/settings[0]);
        const double influence=std::pow(t*t*(3-2*t),settings[3]);
        for(const auto& [index,weight]:data.mapping[size_t(i)])
            covered[size_t(index)]=std::max(covered[size_t(index)],influence*weight);
    }
    return covered;
}
static void validate(const Prepared& data,const double* baseline,const double* samples,int count,const double* settings) {
    if(count<1||count>4096||!baseline||!samples||!settings) throw std::runtime_error("A stroke requires 1–4096 pointer samples.");
    for(int i=0;i<2*count;++i) if(!std::isfinite(samples[i])) throw std::runtime_error("Paint samples must be finite.");
    for(int i=0;i<5;++i) if(!std::isfinite(settings[i])) throw std::runtime_error("Paint settings must be finite.");
    if(settings[0]<=0||settings[0]>4096||settings[1]<0||settings[1]>1||settings[2]<0||settings[2]>1||settings[3]<.05||settings[3]>20)
        throw std::runtime_error("Invalid brush radius, weight, strength or falloff.");
    for(int i=0;i<data.count;++i) if(!std::isfinite(baseline[i])||baseline[i]<0||baseline[i]>1)
        throw std::runtime_error("Paint baseline weights must be between zero and one.");
}
static std::unique_ptr<inspection::Comparison> colors(const Prepared& data,const double* values,uint64_t cancel) {
    auto result=std::make_unique<inspection::Comparison>(); result->target=data.target; result->reference=data.reference?data.reference:data.target;
    result->stats={0,1,0,0}; Vertices weights=Vertices::Zero(data.target->vertices.rows(),3);
    for(int64_t i=0;i<weights.rows();++i) {
        check_cancel(cancel);
        for(const auto& [index,weight]:data.mapping[size_t(i)]) weights(i,0)+=weight*values[index];
    }
    inspection::buffers(*result,weights,cancel); return result;
}
std::unique_ptr<inspection::Comparison> stroke(const Prepared& data,const double* baseline,const double* samples,int count,const double* settings,double* values,uint64_t cancel) {
    validate(data,baseline,samples,count,settings); const auto covered=coverage(data,samples,count,settings,cancel);
    for(int i=0;i<data.count;++i) values[i]=baseline[i]+(settings[1]-baseline[i])*covered[size_t(i)]*settings[2];
    return colors(data,values,cancel);
}
}
