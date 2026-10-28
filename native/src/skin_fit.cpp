#include "skin_fit_kernel.hpp"
#include "skin_fit_validation.hpp"

namespace af::skin::fit {
static void validate(const AfSkinFit& a) {
    if(!a.vertices||!a.quads||!a.targets||a.count<4||a.quad_count<1||a.frames<2)
        throw std::runtime_error("Fitting requires a quad reference and at least two poses.");
    if(a.bones<1||a.bones>64||a.bones>a.count||(a.strategy!=0&&a.strategy!=1)||!std::isfinite(a.smoothing)||a.smoothing<0)
        throw std::runtime_error("Invalid bone fitting settings.");
    if(a.strategy==1&&a.bones!=2) throw std::runtime_error("Single Active requires a background and a moving bone.");
    if(!Eigen::Map<const Vertices>(a.vertices,a.count,3).allFinite()||
       !Eigen::Map<const Vertices>(a.targets,int64_t(a.count)*a.frames,3).allFinite())
        throw std::runtime_error("Bone fitting requires finite positions.");
    for(int64_t i=0;i<4LL*a.quad_count;++i) if(a.quads[i]<0||a.quads[i]>=a.count)
        throw std::runtime_error("Bone fitting face has an invalid vertex identity.");
}
static int run(const AfSkinFit& a,double* weights,double* matrices,double* report,uint64_t cancel) {
    check_cancel(cancel); validate(a); donor::cancellation=cancel;
    std::fill(report,report+5,0); int count;
    if(a.strategy==0) count=donor::sb_fit(a.vertices,a.count,a.quads,a.quad_count,a.targets,a.frames,a.bones,2,weights,matrices);
    else count=donor::one_fit(a.vertices,a.count,a.quads,a.quad_count,a.targets,a.frames,0,0,a.smoothing,weights,matrices,report)?2:0;
    if(!count) throw std::runtime_error(donor::error);
    check_cancel(cancel); return count;
}
static void interval(const double* keys,int count,double value,int& left,int& right,double& t) {
    if(count<2||!std::isfinite(value)) throw std::runtime_error("Invalid fitting playback interval.");
    for(int i=0;i<count;++i) if(!std::isfinite(keys[i])||(i&&keys[i]<=keys[i-1]))
        throw std::runtime_error("Fitting sample keys must be finite and increasing.");
    value=std::clamp(value,keys[0],keys[count-1]);
    right=std::min(int(std::upper_bound(keys,keys+count,value)-keys),count-1); left=std::max(0,right-1);
    t=(value-keys[left])/(keys[right]-keys[left]);
}
}
int af_skin_fit(const AfSkinFit* input,double* weights,double* matrices,double* report,uint64_t cancel) {
    try {
        if(!input||!weights||!matrices||!report) throw std::runtime_error("Missing fitting buffers.");
        return af::skin::fit::run(*input,weights,matrices,report,cancel);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
int af_skin_fit_predict(const double* vertices,int count,const double* weights,int bones,const double* keys,
    const double* matrices,int frames,const double* values,int samples,double* transforms,double* positions,uint64_t cancel) {
    try {
        if(!vertices||!weights||!keys||!matrices||!values||!transforms||!positions||count<1||bones<1||samples<1)
            throw std::runtime_error("Missing fitting prediction buffers.");
        af::skin::fit::validate_prediction(vertices,count,weights,bones,matrices,frames);
        for(int i=0;i<samples;++i) {
            af::check_cancel(cancel); int left,right; double t; af::skin::fit::interval(keys,frames,values[i],left,right,t);
            double* output=transforms+int64_t(i)*bones*16;
            af::skin::fit::donor::sb_interpolate(matrices+int64_t(left)*bones*16,matrices+int64_t(right)*bones*16,bones,t,output);
            af::skin::fit::donor::db_skin(vertices,count,weights,bones,output,positions+int64_t(i)*count*3);
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
