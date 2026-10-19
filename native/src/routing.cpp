#include "routing_planner.hpp"
#include <Eigen/LU>

namespace af::routing {
static Input input(const double* records,int count,const double* world,const int* owners,
                   int surfaces,const AfRoutingOptions* options,uint64_t cancel) {
    if(!records||!world||!owners||!options||count<2||count>100000)
        throw std::runtime_error("Invalid routing input.");
    if(options->samples<count||options->samples>1000000||options->accepted_steps<1||options->accepted_steps>4096||
       (options->closed&&count<3)||!std::isfinite(options->radius)||options->radius<0)
        throw std::runtime_error("Invalid routing settings.");
    for(int i=0;i<count;++i) if(owners[i]<0||owners[i]>surfaces) throw std::runtime_error("Invalid routing owner.");
    if(!std::all_of(records,records+13*count,[](double value){return std::isfinite(value);}))
        throw std::runtime_error("Routing points must be finite.");
    const M4 matrix=Eigen::Map<const M4>(world);
    if(!matrix.allFinite()||!matrix.fullPivLu().isInvertible()) throw std::runtime_error("Invalid routing transform.");
    return {records,count,matrix,matrix.inverse(),std::vector<int>(owners,owners+count),*options,cancel};
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
static bool replan(const Input& input,const World& scene,const Reference& reference,
                   std::vector<Span>& prepared,int64_t* counters,double* measures) {
    prepared=spans(input,scene,reference);
    prepare_routes(input,scene,reference,prepared);
    return solve(prepared,input,counters,measures);
}
static uint64_t evaluate(Input input,const World& scene,int64_t* counters,double* measures,uint64_t warm) {
    resolve_contacts(input,scene);
    const auto reference=af::routing::reference(input);
    auto spans=af::routing::spans(input,scene,reference);
    const bool continuation=warm_start(input,scene,reference,spans,warm);
    if(!continuation) prepare_routes(input,scene,reference,spans);
    if(!solve(spans,input,counters,measures)&&
       (!continuation||!replan(input,scene,reference,spans,counters,measures)))
        throw std::runtime_error("Routing could not find a collision-free path.");
    return retain_path(make_path(result(input,reference,spans),input.options.closed,input.cancel));
}
}
uint64_t af_route_path(const double* records,int count,const double* world,const int* owners,
    const uint64_t* meshes,const double* matrices,int surfaces,const AfRoutingOptions* options,
    int64_t* counters,double* measures,uint64_t warm,uint64_t cancel) {
    try {
        if(!counters||!measures) throw std::runtime_error("Routing report storage is required.");
        const auto input=af::routing::input(records,count,world,owners,surfaces,options,cancel);
        auto scene=af::routing::capture_world(meshes,matrices,surfaces,options->radius,cancel);
        return af::routing::evaluate(input,scene,counters,measures,warm);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_route_path_in_scene(const double* records,int count,const double* world,const int* owners,
    uint64_t handle,const AfRoutingOptions* options,int64_t* counters,double* measures,uint64_t warm,uint64_t cancel) {
    try {
        if(!counters||!measures||!options) throw std::runtime_error("Routing report and options are required.");
        const auto scene=af::routing::routing_scene(handle);
        if(scene->radius!=options->radius) throw std::runtime_error("Routing scene clearance changed.");
        const auto input=af::routing::input(records,count,world,owners,int(scene->collision->items.size()),options,cancel);
        return af::routing::evaluate(input,*scene,counters,measures,warm);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
