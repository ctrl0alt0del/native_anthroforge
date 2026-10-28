#include "anthroforge/skin_fit.h"
#include "skin_fit_validation.hpp"

namespace af::skin::fit {
static double percentile(std::vector<double> values) {
    std::sort(values.begin(),values.end());
    double index=.95*double(values.size()-1); size_t low=size_t(index),high=std::min(low+1,values.size()-1);
    return values[low]+(values[high]-values[low])*(index-double(low));
}
static std::vector<char> moving(const Vertices& rest,const double* targets,const int* training,int frames) {
    Eigen::VectorXd displacement=Eigen::VectorXd::Zero(rest.rows());
    for(int i=0;i<frames;++i) if(training[i]) {
        Eigen::Map<const Vertices> target(targets+int64_t(i)*rest.rows()*3,rest.rows(),3);
        displacement=displacement.cwiseMax((target-rest).rowwise().norm());
    }
    double threshold=std::max(displacement.maxCoeff()*.01,1e-10);
    std::vector<char> active(size_t(rest.rows()));
    for(int i=0;i<rest.rows();++i) active[size_t(i)]=displacement(i)>threshold;
    return active;
}
static void report(const Eigen::VectorXd& errors,const std::vector<char>& active,double extent,double* output) {
    std::vector<double> all(errors.data(),errors.data()+errors.size()),selected;
    for(int i=0;i<errors.size();++i) if(active[size_t(i)]) selected.push_back(errors(i));
    output[0]=std::sqrt(errors.squaredNorm()/double(errors.size()));
    output[1]=100*percentile(all)/extent; output[2]=errors.maxCoeff();
    output[3]=100*percentile(selected.empty()?all:selected)/extent;
}
static void quality(const double* vertices,int count,const double* targets,const double* predicted,
    const int* training,int frames,double* output,uint64_t cancel) {
    Eigen::Map<const Vertices> rest(vertices,count,3);
    double extent=(rest.colwise().maxCoeff()-rest.colwise().minCoeff()).maxCoeff();
    if(!rest.allFinite()||extent<=0) throw std::runtime_error("Fitting requires a nonzero finite reference extent.");
    auto active=moving(rest,targets,training,frames);
    for(int i=0;i<frames;++i) {
        check_cancel(cancel); Eigen::Map<const Vertices> a(targets+int64_t(i)*count*3,count,3);
        Eigen::Map<const Vertices> b(predicted+int64_t(i)*count*3,count,3);
        if(!a.allFinite()||!b.allFinite()) throw std::runtime_error("Nonfinite fitted positions.");
        report((a-b).rowwise().norm(),active,extent,output+i*4);
    }
}
}
int af_skin_fit_quality(const double* vertices,int count,const double* targets,const double* predicted,
    const int* training,int frames,double* output,uint64_t cancel) {
    try {
        if(!vertices||!targets||!predicted||!training||!output||count<1||frames<2)
            throw std::runtime_error("Missing fitted quality inputs.");
        af::skin::fit::quality(vertices,count,targets,predicted,training,frames,output,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_fit_sampling(double minimum,double maximum,int count,double* values,int* training) {
    try {
        if(!values||!training||!std::isfinite(minimum)||!std::isfinite(maximum)||minimum>=maximum||count<5||count>33||!(count%2))
            throw std::runtime_error("Fitting requires an increasing range and an odd sample count (5-33).");
        for(int i=0;i<count;++i) { values[i]=minimum+(maximum-minimum)*i/(count-1); training[i]=int(i%2==0); }
        values[count-1]=maximum; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_fit_repeatability(const double* first,const double* replay,int count,double* error) {
    try {
        if(!first||!replay||!error||count<1) throw std::runtime_error("Missing repeatability samples.");
        Eigen::Map<const af::Vertices> a(first,count,3),b(replay,count,3);
        double extent=(a.colwise().maxCoeff()-a.colwise().minCoeff()).maxCoeff(); *error=(a-b).cwiseAbs().maxCoeff();
        if(!a.allFinite()||!b.allFinite()||extent<=0||*error>extent*1e-5)
            throw std::runtime_error("Shortcut replay is not repeatable; fitting stopped.");
        return 0;
    } catch(const std::exception& failure) { af::set_error(failure.what()); return 1; }
}
