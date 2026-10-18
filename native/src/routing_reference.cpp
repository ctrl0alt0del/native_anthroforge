#include "routing_internal.hpp"

namespace af::routing {
static std::vector<Vec> anchors(const Input& input) {
    std::vector<Vec> result;
    for(int i=0;i<input.count;++i) {
        const V3 value=point(input.world,V3(input.records+13*i));
        result.push_back({value.x(),value.y(),value.z()});
    }
    if(input.options.closed) result.push_back(result.front());
    return result;
}
static std::vector<double> span_lengths(const std::vector<Vec>& points) {
    std::vector<double> result;
    for(size_t i=1;i<points.size();++i) result.push_back(kernel::norm(kernel::sub(points[i],points[i-1])));
    return result;
}
std::vector<int> allocate_edges(const std::vector<double>& lengths,int edges) {
    const int count=int(lengths.size()),remaining=edges-count; std::vector<int> result(count,1),order(count);
    const double total=std::accumulate(lengths.begin(),lengths.end(),0.0); std::vector<double> fractions(count);
    int left=remaining;
    for(int i=0;i<count;++i) {
        const double raw=remaining*(total>1e-12?lengths[i]/total:1.0/count),whole=std::floor(raw);
        result[i]+=int(whole); left-=int(whole); fractions[i]=raw-whole;
    }
    std::iota(order.begin(),order.end(),0);
    std::stable_sort(order.begin(),order.end(),[&](int a,int b){return fractions[a]>fractions[b];});
    for(int i=0;i<left;++i) ++result[order[i]];
    return result;
}
Reference reference(const Input& input) {
    const auto points=anchors(input);
    const auto counts=allocate_edges(span_lengths(points),input.options.samples-int(!input.options.closed));
    Reference result{{points.front()},{0},{0}};
    for(int i=0;i<int(counts.size());++i) {
        const Vec delta=kernel::sub(points[i+1],points[i]);
        for(int step=1;step<=counts[i];++step) {
            check_cancel(input.cancel); const double t=double(step)/counts[i];
            result.points.push_back(kernel::add(points[i],kernel::mul(delta,t)));
            result.parameters.push_back(i+t);
        }
        result.pins.push_back(int64_t(result.points.size()-1));
    }
    return result;
}
static void append_samples(EvaluatedPath& output,const Input& input,const Reference& reference,const Span& span) {
    const size_t first=output.samples.empty()?0:1;
    for(size_t i=first;i<span.output.size();++i) {
        check_cancel(input.cancel); const double parameter=reference.parameters[output.samples.size()];
        const int knot=std::min(input.count-1,int(parameter)),next=(knot+1)%input.count;
        const double t=parameter-knot,*a=input.records+13*knot,*b=input.records+13*next;
        const Vec& vertex=span.output[i]; const V3 position=point(input.inverse,V3(vertex.x,vertex.y,vertex.z));
        output.samples.push_back({position,V3::UnitZ(),V3::UnitY(),a[9]*(1-t)+b[9]*t,a[10]*(1-t)+b[10]*t});
        output.parameters.push_back(parameter);
    }
}
EvaluatedPath result(const Input& input,const Reference& reference,const std::vector<Span>& spans) {
    EvaluatedPath output;
    for(const auto& span:spans) append_samples(output,input,reference,span);
    if(input.options.closed) { output.samples.pop_back(); output.parameters.pop_back(); }
    curve_frames(output.samples,input.options.closed,input.cancel,true);
    return output;
}
}
