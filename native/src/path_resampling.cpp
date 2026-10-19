#include "path_internal.hpp"

namespace af {
struct AnchoredSampling {
    Samples source;
    std::vector<double> lengths,stations;
};
static std::vector<double> anchor_stations(const Path& path,const std::vector<double>& lengths,const int* knots,int count) {
    if(count<1||!knots||knots[0]!=0) throw std::runtime_error("Retain the curve's first point when sampling.");
    std::vector<double> stations;
    for(int i=0;i<count;++i) {
        const auto found=std::lower_bound(path.parameters.begin(),path.parameters.end(),double(knots[i]));
        if(found==path.parameters.end()||*found!=knots[i]||(i&&knots[i]<=knots[i-1]))
            throw std::runtime_error("Retained point must have accepted path correspondence, in authored order.");
        stations.push_back(lengths[size_t(found-path.parameters.begin())]);
    }
    if(path.closed) stations.push_back(lengths.back());
    else if(stations.back()!=lengths.back()) throw std::runtime_error("Retain both open endpoints when sampling.");
    return stations;
}
static AnchoredSampling prepare_anchors(const Path& path,const int* knots,int count) {
    auto source=read_samples(path.samples.data(),int(path.parameters.size()));
    if(path.closed) source.push_back(source.front());
    auto lengths=curve_lengths(source);
    auto stations=anchor_stations(path,lengths,knots,count);
    return {std::move(source),std::move(lengths),std::move(stations)};
}
static std::vector<int> span_allocation(const std::vector<double>& stations,int edges) {
    std::vector<double> lengths;
    for(size_t i=1;i<stations.size();++i) lengths.push_back(stations[i]-stations[i-1]);
    return allocate_edges(lengths,edges);
}
static Samples sample_anchors(const AnchoredSampling& source,int count,bool closed,int* indices,uint64_t cancel) {
    const auto allocation=span_allocation(source.stations,count-int(!closed)); Samples samples;
    for(size_t span=0;span<allocation.size();++span) {
        indices[span]=int(samples.size());
        const double start=source.stations[span],length=source.stations[span+1]-start;
        for(int step=0;step<allocation[span];++step) {
            check_cancel(cancel);
            samples.push_back(at_distance(source.source,source.lengths,start+length*step/allocation[span]));
        }
    }
    if(!closed) { indices[allocation.size()]=int(samples.size()); samples.push_back(source.source.back()); }
    curve_frames(samples,closed,cancel,false); return samples;
}
}
int af_path_sample_anchored(uint64_t handle,const int* knots,int anchors,int count,double* output,int* indices,uint64_t cancel) {
    try {
        af::check_cancel(cancel); const auto path=af::path(handle);
        if(!output||!indices||count<(path->closed?3:2)||count>1000000||anchors>count)
            throw std::runtime_error("Invalid anchored sampling budget or buffers.");
        const auto source=af::prepare_anchors(*path,knots,anchors);
        af::write_samples(af::sample_anchors(source,count,path->closed,indices,cancel),output); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
