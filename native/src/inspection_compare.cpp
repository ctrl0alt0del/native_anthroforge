#include "anthroforge/inspection.h"
#include "inspection_internal.hpp"

namespace af::inspection {
Comparison& comparison(uint64_t handle) {
    if(!handle) throw std::runtime_error("Missing inspection result.");
    return *reinterpret_cast<Comparison*>(handle);
}
static std::unique_ptr<Comparison> compare(uint64_t reference,uint64_t target,bool source,const M4& frame,uint64_t cancel) {
    auto out=std::make_unique<Comparison>(); out->reference=mesh(reference); out->target=mesh(target);
    const auto& a=*out->reference; const auto& b=*out->target;
    const Vertices delta=(b.vertices-mapped(a,b,a.vertices,source,cancel))*frame.block<3,3>(0,0).transpose();
    if(!delta.rows()||!delta.allFinite()) throw std::runtime_error("Comparison needs finite material geometry.");
    const Eigen::VectorXd lengths=delta.rowwise().norm();
    out->stats={lengths.minCoeff(),lengths.maxCoeff(),lengths.mean(),std::sqrt(lengths.squaredNorm()/double(lengths.size()))};
    buffers(*out,delta,cancel); return out;
}
}
uint64_t af_inspection_compare(uint64_t reference,uint64_t target,int source,const double* frame,uint64_t cancel) {
    try { return reinterpret_cast<uint64_t>(af::inspection::compare(reference,target,source!=0,af::M4(frame),cancel).release()); }
    catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_inspection_release(uint64_t handle) { delete reinterpret_cast<af::inspection::Comparison*>(handle); }
int af_inspection_summary(uint64_t handle,double* values,int64_t* counts) {
    try {
        const auto& c=af::inspection::comparison(handle);
        std::copy(c.stats.begin(),c.stats.end(),values); std::copy(c.target->bounds,c.target->bounds+6,values+4);
        counts[0]=int64_t(c.chunks.size()); counts[1]=c.target->vertices.rows(); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_inspection_chunk(uint64_t handle,int chunk,const float** data,int* count) {
    try {
        const auto& row=af::inspection::comparison(handle).chunks.at(size_t(chunk));
        *data=row.data(); *count=int(row.size()); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
uint64_t af_inspection_bytes(uint64_t handle) {
    try {
        uint64_t size=sizeof(af::inspection::Comparison);
        for(const auto& chunk:af::inspection::comparison(handle).chunks) size+=chunk.capacity()*sizeof(float);
        return size;
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
