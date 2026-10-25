#include "fiber_deformation.hpp"
namespace af::fiber {
static void constrain(Preparation& v,int row) {
    const int p=nearest_pin(v,v.arc[size_t(row)]);
        const double w=kernel(distance(v,v.arc[size_t(row)],v.arc[size_t(v.pins[p])])/pin_width(v,int(p)));
        v.weights.row(row)*=1-w;
        const int owner=v.pin_owners[p];
        if(owner<0||owner>=int(v.parents.size())) throw std::runtime_error("Missing fiber pin surface.");
        v.weights(row,owner)+=w;
}
void prepare_weights(Preparation& v,const AfFiberReference& in,uint64_t cancel) {
    const int n=int(v.path->parameters.size());
    if(uint64_t(v.points.rows())*uint64_t(in.surfaces)>8388608) throw std::runtime_error("Fiber support weights exceed the preparation budget.");
    v.weights=Eigen::MatrixXd::Zero(v.points.rows(),in.surfaces); smooth_weights(v,in,cancel);
    for(int i=0;i<n;++i) constrain(v,i);
    for(int i=n;i<v.points.rows();++i) v.weights.row(i)=v.weights.row(v.knots[size_t((i-n)/3)]);
}
Map interpolated(const Preparation& v,const std::vector<Map>& maps,int row) {
    const double u=v.arc[size_t(row)]/v.length*(v.path->closed?8:7); const int low=int(u); const double f=u-low;
    const double w[4]{std::pow(1-f,3)/6,(3*f*f*f-6*f*f+4)/6,(-3*f*f*f+3*f*f+3*f+1)/6,f*f*f/6};
    Map result{M3::Zero(),V3::Zero()};
    for(int j=0;j<4;++j) {
        const int index=v.path->closed?(low+j+7)%8:std::clamp(low+j-1,0,7);
        result.linear+=w[j]*maps[size_t(index)].linear; result.translation+=w[j]*maps[size_t(index)].translation;
    }
    return result;
}
}
