#include "routing_internal.hpp"

namespace af::routing {
static double median(std::vector<double> values) {
    std::sort(values.begin(),values.end()); const size_t middle=values.size()/2;
    return values.size()%2?values[middle]:(values[middle-1]+values[middle])*0.5;
}
static double regularization_scale(const std::vector<Vec>& points,double epsilon,double floor) {
    std::vector<double> diagonal(points.size(),0.01);
    for(size_t i=1;i<points.size();++i) {
        const Vec delta=kernel::sub(points[i],points[i-1]);
        const double weight=0.45/std::sqrt(kernel::dot(delta,delta)+epsilon*epsilon);
        diagonal[i-1]+=weight; diagonal[i]+=weight;
    }
    return std::max(median(diagonal),floor);
}
static double initial_penalty(size_t count) {
    const double weight=0.9*(count-1); std::vector<double> diagonal(count,0.01+2*weight);
    diagonal.front()-=weight; diagonal.back()-=weight;
    return std::max(1.0,median(diagonal));
}
static kernel::AfV3SqpConfig configuration(const World& world,const Span& span,const Input& input) {
    kernel::AfV3SqpConfig value{}; const double radius=input.options.radius;
    value.length_weight=0.9; value.fidelity_weight=0.01; value.radius=radius;
    value.slack=world.slack; value.numeric_floor=world.floor; value.length_scale=world.length;
    value.epsilon=std::max(world.floor,1e-4*kernel::af_v3_sqp_mean_length(span.reference,0));
    value.fixed_tolerance=1e-4; value.stationarity_tolerance=1e-4; value.relative_energy_tolerance=1e-5;
    value.trust_radius=std::max(8*radius,0.01*world.length); value.min_trust=std::max(0.25*radius,world.floor);
    value.max_trust=std::max(value.trust_radius,0.25*world.length);
    value.regularization_scale=regularization_scale(span.reference,value.epsilon,world.floor);
    value.regularization=1e-6*value.regularization_scale; value.penalty=initial_penalty(span.reference.size());
    value.accepted_cap=input.options.accepted_steps; value.trial_cap=std::max(32,8*value.accepted_cap);
    value.ccd_mode=kernel::AF_V3_SQP_CCD_INDEXED; value.ccd_budget=262143;
    return value;
}
static void edge_owners(Span& span,const Input& input,int first) {
    span.first.assign(span.reference.size()-1,0); span.second=span.first;
    for(size_t i=0;i<span.pins.size();++i) {
        const int owner=input.owners[(first+int(i))%input.count],pin=int(span.pins[i]);
        if(pin) span.second[pin-1]=owner;
        if(pin<int(span.first.size())) span.first[pin]=owner;
        span.targets.push_back(span.reference[pin]);
    }
}
static Span prepare_span(const Input& input,const World& world,const Reference& reference,int first,int last) {
    Span span; const int begin=int(reference.pins[first]),end=int(reference.pins[last]);
    span.reference.assign(reference.points.begin()+begin,reference.points.begin()+end+1);
    for(int i=first;i<=last;++i) span.pins.push_back(reference.pins[i]-begin);
    span.seed=span.reference; span.output=span.reference; edge_owners(span,input,first);
    span.session.reset(static_cast<kernel::AfV3NativeSession*>(kernel::af_v3_session_create(
        world.collision.get(),span.first.data(),span.second.data(),int(span.first.size()))));
    if(!span.session) throw std::runtime_error("Routing session preparation failed.");
    span.session->snapshot=world.snapshot.get(); span.session->face_owners=world.owners;
    span.job.config=configuration(world,span,input);
    if(input.backend==AF_ROUTING_PIQP) configure_piqp(span.job,input.cancel);
    return span;
}
std::vector<Span> spans(const Input& input,const World& world,const Reference& reference) {
    std::vector<Span> result;
    if(input.options.closed) result.push_back(prepare_span(input,world,reference,0,input.count));
    else for(int i=0;i<input.count-1;++i) result.push_back(prepare_span(input,world,reference,i,i+1));
    return result;
}
static kernel::AfV3SqpJob job(Span& span) {
    auto job=span.job; job.session=span.session.get(); job.count=int(span.reference.size());
    job.points=reinterpret_cast<const double*>(span.seed.data());
    job.reference=reinterpret_cast<const double*>(span.reference.data());
    job.targets=reinterpret_cast<const double*>(span.targets.data());
    job.pins=span.pins.data(); job.pin_count=int(span.pins.size());
    job.output=reinterpret_cast<double*>(span.output.data());
    return job;
}
static void synchronize_owner_span(std::vector<kernel::AfV3SqpJob>& jobs) {
    double length=1e-9;
    for(const auto& job:jobs) {
        length=std::max({length,4*job.config.slack,2.5*job.config.radius});
        for(int i=0;i<job.pin_count;++i) {
            const int pin=int(job.pins[i]); const Vec point=kernel::load3(job.points+3*pin);
            if(pin) length=std::max(length,kernel::norm(kernel::sub(point,kernel::load3(job.points+3*(pin-1)))));
            if(pin+1<job.count) length=std::max(length,kernel::norm(kernel::sub(point,kernel::load3(job.points+3*(pin+1)))));
        }
    }
    for(auto& job:jobs) job.config.owner_span=length;
}
static void report(const std::vector<kernel::AfV3SqpJob>& jobs,int64_t* counters,double* measures) {
    std::fill_n(counters,8,0); std::fill_n(measures,8,0);
    for(const auto& job:jobs) {
        const auto& r=job.result;
        counters[0]+=r.accepted; counters[1]+=r.rejected; counters[2]+=r.trials;
        counters[3]+=r.ccd_pairs; counters[4]+=r.ccd_tests; counters[5]+=r.contacts;
        counters[6]=std::max(counters[6],int64_t(r.termination)); counters[7]+=r.validated;
        measures[0]+=r.energy; measures[1]=std::max(measures[1],r.maximum_violation);
        measures[2]=std::max(measures[2],r.fixed_residual); measures[3]=std::max(measures[3],r.stationarity);
        measures[4]=std::max(measures[4],r.elapsed_ms);
    }
}
bool solve(std::vector<Span>& spans,const Input& input,int64_t* counters,double* measures) {
    std::vector<kernel::AfV3SqpJob> jobs; for(auto& span:spans) jobs.push_back(job(span));
    synchronize_owner_span(jobs); const int cap=input.options.accepted_steps;
    ControllerHandle controller(static_cast<kernel::AfV3SqpCoordinator*>(kernel::af_v3_native_sqp_begin(
        jobs.data(),int(jobs.size()),cap,std::max(32,8*cap))),kernel::af_v3_native_sqp_destroy);
    if(!controller) throw std::runtime_error("Routing controller creation failed.");
    int done=0,accepted=0,infeasible=0;
    while(!done) {
        check_cancel(input.cancel);
        if(kernel::af_v3_native_sqp_step(controller.get(),1,&done,&accepted,&infeasible))
            throw std::runtime_error("Routing controller failed.");
    }
    report(jobs,counters,measures);
    return !infeasible;
}
}
