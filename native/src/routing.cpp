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
    return {records,count,matrix,matrix.inverse(),owners,*options,cancel};
}
}
uint64_t af_route_path(const double* records,int count,const double* world,const int* owners,
    const uint64_t* meshes,const double* matrices,int surfaces,const AfRoutingOptions* options,
    int64_t* counters,double* measures,uint64_t warm,uint64_t cancel) {
    try {
        if(!counters||!measures) throw std::runtime_error("Routing report storage is required.");
        const auto input=af::routing::input(records,count,world,owners,surfaces,options,cancel);
        auto scene=af::routing::capture_world(meshes,matrices,surfaces,options->radius,cancel);
        const auto reference=af::routing::reference(input);
        auto spans=af::routing::spans(input,scene,reference);
        if(!af::routing::warm_start(input,reference,spans,warm))
            af::routing::prepare_routes(input,scene,reference,spans);
        af::routing::solve(spans,input,counters,measures);
        return af::retain_path(af::make_path(af::routing::result(input,reference,spans),options->closed,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
