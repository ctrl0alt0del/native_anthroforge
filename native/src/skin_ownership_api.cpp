#include "skin_ownership.hpp"
#include <numeric>
int af_skin_ownership(uint64_t handle,const AFSkinOwnershipInput* input,double ratio,int* owners,int* sources,int* fallback,uint64_t cancel) {
    try {
        if(!input||!owners||!sources||!fallback||!std::isfinite(ratio)||ratio<0||ratio>1)
            throw std::runtime_error("Invalid skin ownership request.");
        af::check_cancel(cancel); const auto mesh=af::mesh(handle);
        af::skin_ownership::assign(*mesh,*input,owners,sources,fallback,cancel);
        af::skin_ownership::clean(*mesh,owners,ratio,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_owner_regions(const int* owners,int count,const int* mapping,int owner_count,int remainder,int* regions,uint64_t cancel) {
    try {
        if(count<0||owner_count<0||!owners||!mapping||!regions||remainder<0) throw std::runtime_error("Invalid ownership region buffers.");
        af::check_cancel(cancel);
        for(int i=0;i<count;++i) {
            if(i%4096==0) af::check_cancel(cancel);
            if(owners[i]<-1||owners[i]>=owner_count) throw std::runtime_error("Invalid skin bone index.");
            regions[i]=owners[i]<0?remainder:mapping[owners[i]];
            if(regions[i]<0) throw std::runtime_error("Invalid skin region index.");
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
namespace af::skin_ownership {
static void transfer(const Mesh& source,const Mesh& target,const int* owners,const double* lengths,int* sampled,double* sizes,uint64_t cancel) {
    std::vector<int> indices(source.vertices.rows()); std::iota(indices.begin(),indices.end(),0);
    const PointIndex index(source.vertices,indices,cancel);
    if(indices.empty()) throw std::runtime_error("Density sampling needs source vertices.");
    for(int i=0;i<source.vertices.rows();++i) if(owners[i]<-1||!std::isfinite(lengths[i])||lengths[i]<0)
        throw std::runtime_error("Invalid density sample value.");
    for(int i=0;i<target.vertices.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        const auto hit=index.nearest(source.vertices,target.vertices.row(i));
        sampled[i]=owners[hit.first]; sizes[i]=lengths[hit.first];
    }
}
}
int af_skin_sample_density(uint64_t source,uint64_t target,const int* owners,const double* lengths,int* sampled,double* sizes,uint64_t cancel) {
    try {
        if(!owners||!lengths||!sampled||!sizes) throw std::runtime_error("Missing density sample buffers.");
        af::check_cancel(cancel);
        af::skin_ownership::transfer(*af::mesh(source),*af::mesh(target),owners,lengths,sampled,sizes,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
