#include "routing_internal.hpp"

namespace af::routing {
static std::vector<Vec> world_points(const Input& input,const Path& path) {
    std::vector<Vec> points;
    for(size_t i=0;i<path.parameters.size();++i) {
        check_cancel(input.cancel);
        const V3 point=(input.world*V3(path.samples.data()+11*i).homogeneous()).head<3>();
        points.push_back({point.x(),point.y(),point.z()});
    }
    if(input.options.closed) points.push_back(points.front());
    return points;
}
bool warm_start(const Input& input,const Reference& reference,std::vector<Span>& spans,uint64_t handle) {
    if(!handle) return false;
    const auto previous=path(handle);
    if(previous->parameters.size()!=size_t(input.options.samples)||previous->closed!=bool(input.options.closed)) return false;
    auto points=world_points(input,*previous);
    for(int64_t pin:reference.pins) points[pin]=reference.points[pin];
    if(input.options.closed) spans.front().seed=std::move(points);
    else for(size_t i=0;i<spans.size();++i)
        spans[i].seed.assign(points.begin()+reference.pins[i],points.begin()+reference.pins[i+1]+1);
    return true;
}
}
