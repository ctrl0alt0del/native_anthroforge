#include "routing_planner.hpp"
#include "routing_trace.hpp"
#include "anthroforge/routing_trace.h"
#include <Eigen/LU>

namespace af::routing {
static Input input(const double* records,int count,const double* world,const int* owners,
                   int surfaces,const AfRoutingOptions* options,uint64_t cancel) {
    if(!records||!world||!owners||!options||count<2||count>100000)
        throw std::runtime_error("Invalid routing input.");
    if(options->samples<2||options->samples>1000000||options->accepted_steps<1||options->accepted_steps>4096||
       (options->closed&&count<3)||!std::isfinite(options->radius)||options->radius<0)
        throw std::runtime_error("Invalid routing settings.");
    for(int i=0;i<count;++i) if(owners[i]<0||owners[i]>surfaces) throw std::runtime_error("Invalid routing owner.");
    if(!std::all_of(records,records+13*count,[](double value){return std::isfinite(value);}))
        throw std::runtime_error("Routing points must be finite.");
    const M4 matrix=Eigen::Map<const M4>(world);
    if(!matrix.allFinite()||!matrix.fullPivLu().isInvertible()) throw std::runtime_error("Invalid routing transform.");
    return {records,count,matrix,matrix.inverse(),std::vector<int>(owners,owners+count),*options,cancel};
}
static void execution(Input& input,double weight,int checkpoint) {
    if(!std::isfinite(weight)||weight<0||checkpoint<1||checkpoint>1000)
        throw std::runtime_error("Invalid routing execution settings.");
    input.length_weight=weight; input.checkpoint_steps=checkpoint;
}
static void resolve_contacts(Input& input,const World& world) {
    for(int i=0;i<input.count;++i) {
        check_cancel(input.cancel);
        if(input.owners[i]) continue;
        const V3 position=point(input.world,V3(input.records+13*i));
        const auto nearest=kernel::af_nearest_world(*world.collision,{position.x(),position.y(),position.z()});
        // Geometric contact at an authored pin is not an anatomical binding. Do not
        // exempt arbitrary nearby/inside points or extend contact by clearance radius.
        if(nearest.instance>=0&&nearest.distance<=world.floor)
            input.owners[i]=world.collision->items[nearest.instance].owner;
    }
}
static bool replan(const Input& input,const World& scene,Reference& reference,
                   std::vector<Span>& prepared,int64_t* counters,double* measures) {
    prepared=prepare_routes(input,scene,reference);
    return solve(prepared,input,counters,measures);
}
static uint64_t output(const Input& input,const Reference& reference,const std::vector<Span>& spans) {
    if(input.trace) for(size_t i=0;i<spans.size();++i) trace_path(input.trace,4,int(i),spans[i].output);
    return retain_path(make_path(result(input,reference,spans),input.options.closed,input.cancel));
}
static uint64_t evaluate(Input input,const World& scene,int64_t* counters,double* measures,uint64_t warm) {
    if(input.backend!=AF_ROUTING_CUSTOM&&input.backend!=AF_ROUTING_PIQP)
        throw std::runtime_error("Unknown routing backend.");
    resolve_contacts(input,scene);
    auto reference=af::routing::reference(input);
    trace_path(input.trace,0,0,reference.points);
    std::vector<Span> spans;
    const bool continuation=warm_start(input,scene,reference,spans,warm);
    if(input.trace) input.trace->warm=continuation;
    if(!continuation) spans=prepare_routes(input,scene,reference);
    if(!solve(spans,input,counters,measures)&&
       (!continuation||!replan(input,scene,reference,spans,counters,measures)))
        throw std::runtime_error("Routing could not find a collision-free path.");
    return output(input,reference,spans);
}
static void diagnose(Input& input,const World& scene,Trace& trace,uint64_t warm) {
    input.trace=&trace;
    try {
        const auto path=evaluate(input,scene,trace.counters.data(),trace.measures.data(),warm);
        af_path_release(path); trace.success=true;
    } catch(const std::exception& error) { check_cancel(input.cancel); trace.error=error.what(); }
}
}
uint64_t af_route_inspect_configured(const double* records,int count,const double* world,const int* owners,
    uint64_t handle,const AfRoutingOptions* options,uint64_t warm,uint64_t cancel,int backend,double weight,int checkpoint) {
    try {
        if(!options) throw std::runtime_error("Routing options are required.");
        const auto scene=af::routing::routing_scene(handle);
        if(scene->radius!=options->radius) throw std::runtime_error("Routing scene clearance changed.");
        auto input=af::routing::input(records,count,world,owners,int(scene->collision->items.size()),options,cancel);
        input.backend=backend; af::routing::execution(input,weight,checkpoint); auto trace=std::make_shared<af::routing::Trace>();
        af::routing::diagnose(input,*scene,*trace,warm); af::check_cancel(cancel);
        return af::routing::retain_trace(std::move(trace));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_route_path_with_backend(const double* records,int count,const double* world,const int* owners,
    const uint64_t* meshes,const double* matrices,int surfaces,const AfRoutingOptions* options,
    int64_t* counters,double* measures,uint64_t warm,uint64_t cancel,int backend) {
    try {
        if(!counters||!measures) throw std::runtime_error("Routing report storage is required.");
        auto input=af::routing::input(records,count,world,owners,surfaces,options,cancel); input.backend=backend;
        auto scene=af::routing::capture_world(meshes,matrices,surfaces,options->radius,cancel);
        return af::routing::evaluate(input,scene,counters,measures,warm);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_route_path_in_scene_configured(const double* records,int count,const double* world,const int* owners,
    uint64_t handle,const AfRoutingOptions* options,int64_t* counters,double* measures,uint64_t warm,uint64_t cancel,int backend,double weight,int checkpoint) {
    try {
        if(!counters||!measures||!options) throw std::runtime_error("Routing report and options are required.");
        const auto scene=af::routing::routing_scene(handle);
        if(scene->radius!=options->radius) throw std::runtime_error("Routing scene clearance changed.");
        auto input=af::routing::input(records,count,world,owners,int(scene->collision->items.size()),options,cancel);
        input.backend=backend; af::routing::execution(input,weight,checkpoint);
        return af::routing::evaluate(input,*scene,counters,measures,warm);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_route_path(const double* records,int count,const double* world,const int* owners,
    const uint64_t* meshes,const double* matrices,int surfaces,const AfRoutingOptions* options,
    int64_t* counters,double* measures,uint64_t warm,uint64_t cancel) {
    return af_route_path_with_backend(records,count,world,owners,meshes,matrices,surfaces,
        options,counters,measures,warm,cancel,AF_ROUTING_CUSTOM);
}
uint64_t af_route_path_in_scene(const double* records,int count,const double* world,const int* owners,
    uint64_t handle,const AfRoutingOptions* options,int64_t* counters,double* measures,uint64_t warm,uint64_t cancel) {
    return af_route_path_in_scene_with_backend(records,count,world,owners,handle,options,
        counters,measures,warm,cancel,AF_ROUTING_CUSTOM);
}

uint64_t af_route_path_in_scene_with_backend(const double* records,int count,const double* world,const int* owners,
    uint64_t handle,const AfRoutingOptions* options,int64_t* counters,double* measures,uint64_t warm,uint64_t cancel,int backend) {
    return af_route_path_in_scene_configured(records,count,world,owners,handle,options,counters,measures,warm,cancel,backend,0.9,1);
}
uint64_t af_route_inspect(const double* records,int count,const double* world,const int* owners,
    uint64_t handle,const AfRoutingOptions* options,uint64_t warm,uint64_t cancel,int backend) {
    return af_route_inspect_configured(records,count,world,owners,handle,options,warm,cancel,backend,0.9,1);
}
