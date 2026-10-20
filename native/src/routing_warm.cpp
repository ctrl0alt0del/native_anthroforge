#include "routing_planner.hpp"

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
static std::vector<size_t> prior_pins(const Input& input,const Path& previous) {
    std::vector<size_t> result;
    for(int i=0;i<input.count;++i) {
        check_cancel(input.cancel);
        const auto found=std::lower_bound(previous.parameters.begin(),previous.parameters.end(),double(i)-1e-9);
        if(found==previous.parameters.end()||std::abs(*found-i)>1e-8) return {};
        result.push_back(size_t(found-previous.parameters.begin()));
    }
    if(input.options.closed) result.push_back(previous.parameters.size());
    else if(result.back()+1!=previous.parameters.size()) return {};
    return result;
}
static Route remapped(const Route& points,const std::vector<size_t>& pins,const Reference& reference,uint64_t cancel) {
    Route result;
    for(size_t i=1;i<pins.size();++i) {
        check_cancel(cancel);
        const Route part(points.begin()+pins[i-1],points.begin()+pins[i]+1);
        const auto rows=resample(part,int(reference.pins[i]-reference.pins[i-1])+1);
        result.insert(result.end(),rows.begin()+int(!result.empty()),rows.end());
    }
    for(int64_t pin:reference.pins) result[pin]=reference.points[pin];
    return result;
}
static std::vector<Route> routes(const Route& points,const Reference& reference) {
    std::vector<Route> result;
    for(size_t i=1;i<reference.pins.size();++i)
        result.emplace_back(points.begin()+reference.pins[i-1],points.begin()+reference.pins[i]+1);
    return result;
}
bool warm_start(const Input& input,const World& world,const Reference& reference,std::vector<Span>& spans,uint64_t handle) {
    if(!handle) return false;
    const auto previous=path(handle);
    if(previous->closed!=bool(input.options.closed)) return false;
    const auto pins=prior_pins(input,*previous);
    if(pins.size()!=reference.pins.size()) return false;
    auto points=remapped(world_points(input,*previous),pins,reference,input.cancel);
    // SQP can restore clearance, but a seed crossing solid interiors needs a new corridor.
    if(!valid_handoff(routes(points,reference),input,world,false)) return false;
    spans=af::routing::spans(input,world,reference);
    if(input.options.closed) spans.front().seed=std::move(points);
    else for(size_t i=0;i<spans.size();++i)
        spans[i].seed.assign(points.begin()+reference.pins[i],points.begin()+reference.pins[i+1]+1);
    return true;
}
}
