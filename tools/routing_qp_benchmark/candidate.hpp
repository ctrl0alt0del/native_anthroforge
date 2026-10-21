#include "problem.hpp"
static bool af_bench_piqp(AfV3SqpState& state,int backend,std::vector<int>& active,
                          std::vector<double>& multipliers,afbench::Record& row) {
    const double begin=afbench::config.audit?afbench::now():0;
    const auto problem=af_bench_problem(state);
    if(afbench::config.audit) row.assembly=afbench::now()-begin;
    if(!state.qp_lab) state.qp_lab=std::make_shared<afbench::Context>();
    afbench::Vector dual; row.backend=backend;
    const auto x=afbench::piqp(*state.qp_lab,problem,row,dual);
    if(row.status!=piqp::PIQP_SOLVED||!x.allFinite()||!dual.allFinite()) return false;
    af_bench_install(state,x,dual,active,multipliers); return true;
}
static void af_bench_quality(const AfV3SqpState& state,const std::vector<int>& active,
                             const std::vector<double>& multipliers,afbench::Record& row) {
    const auto problem=af_bench_problem(state);
    afbench::Vector dual=afbench::Vector::Zero(state.contacts.size());
    row.dual_valid=active.size()==multipliers.size();
    if(row.dual_valid) for(size_t i=0;i<active.size();++i) dual[active[i]]=multipliers[i];
    afbench::quality(problem,af_bench_vector(state.candidate),dual,row);
    if(!row.dual_valid) row.stationarity=NAN;
}
static bool af_bench_run(AfV3SqpState& state,int backend,std::vector<int>& active,
                         std::vector<double>& multipliers) {
    afbench::Record row; row.backend=backend; row.step=afbench::config.step;
    row.points=state.job->count; row.contacts=int(state.contacts.size());
    const double begin=afbench::config.audit?afbench::now():0;
    const bool ok=backend?af_bench_piqp(state,backend,active,multipliers,row):
        af_v3_sqp_candidate_current(state,active,multipliers);
    if(!backend) row.status=ok?1:-1;
    if(afbench::config.audit) {
        row.total=afbench::now()-begin;
        if(ok) af_bench_quality(state,active,multipliers,row);
        afbench::records.push_back(row);
    }
    return ok;
}
static void af_bench_paired(AfV3SqpState& state) {
    const int orders[3][6]={{0,1,2,2,1,0},{1,2,0,0,2,1},{2,0,1,1,0,2}};
    for(int backend:orders[afbench::config.step%3]) {
        std::vector<int> active; std::vector<double> multipliers;
        af_bench_run(state,backend,active,multipliers);
    }
}
static bool af_v3_sqp_candidate(AfV3SqpState& state,std::vector<int>& active,std::vector<double>& multipliers) {
    ++afbench::config.step;
    if(afbench::config.paired) af_bench_paired(state);
    const bool ok=af_bench_run(state,afbench::config.backend,active,multipliers);
    if(ok) state.trust_boundary=af_v3_sqp_trust(state,state.candidate);
    return ok;
}
