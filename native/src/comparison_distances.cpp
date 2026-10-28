#include "anthroforge/inspection.h"
#include "mesh_internal.hpp"
#include <algorithm>
#include <cmath>

namespace af::inspection {
struct DistanceStats {
    double minimum=INFINITY,maximum=0,sum=0,squares=0; int64_t count=0;
    void add(double value) {
        if(!std::isfinite(value)) throw std::runtime_error("Comparison contains nonfinite distances.");
        minimum=std::min(minimum,value); maximum=std::max(maximum,value);
        sum+=value; squares+=value*value; ++count;
    }
    void write(double* out) const {
        out[0]=count?minimum:0; out[1]=maximum; out[2]=count?sum/double(count):0;
        out[3]=count?std::sqrt(squares/double(count)):0;
    }
};
static void nearest_samples(const Mesh& from,const M4& frame,const Surface& to,DistanceStats& out,uint64_t cancel) {
    const int64_t count=std::min<int64_t>(512,from.vertices.rows());
    for(int64_t i=0;i<count;++i) {
        check_cancel(cancel); const auto index=i*from.vertices.rows()/count;
        const auto hit=nearest(to,point(frame,from.vertices.row(index)));
        if(hit.triangle<0) throw std::runtime_error("Comparison surface has no usable triangle.");
        out.add(std::sqrt(hit.distance));
    }
}
static DistanceStats material(const Mesh& a,const M4& af,const Mesh& b,const M4& bf,uint64_t cancel) {
    if(a.vertices.rows()!=b.vertices.rows()||a.corners!=b.corners||a.offsets!=b.offsets)
        throw std::runtime_error("Material displacement requires verified canonical connectivity.");
    DistanceStats stats;
    for(int64_t i=0;i<a.vertices.rows();++i) {
        check_cancel(cancel); stats.add((point(af,a.vertices.row(i))-point(bf,b.vertices.row(i))).norm());
    }
    return stats;
}
static void compare(const Mesh& a,const M4& af,const Mesh& b,const M4& bf,bool verified,double* values,int64_t* counts,uint64_t cancel) {
    if(!af.allFinite()||!bf.allFinite()) throw std::runtime_error("Comparison frames must be finite.");
    check_cancel(cancel); DistanceStats geometry;
    nearest_samples(a,af,Surface(b,bf),geometry,cancel);
    nearest_samples(b,bf,Surface(a,af),geometry,cancel);
    geometry.write(values); counts[0]=geometry.count; counts[1]=0;
    if(verified) { const auto displacement=material(a,af,b,bf,cancel);
        displacement.write(values+4); counts[1]=displacement.count; }
}
}
int af_comparison_distances(uint64_t first,const double* a,uint64_t second,const double* b,int verified,double* values,int64_t* counts,uint64_t cancel) {
    try {
        if(!values||!counts) throw std::runtime_error("Comparison requires owned output buffers.");
        std::fill(values,values+8,0);
        af::inspection::compare(*af::mesh(first),af::M4(a),*af::mesh(second),af::M4(b),verified!=0,values,counts,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
