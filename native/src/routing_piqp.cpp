#include "routing_qp.hpp"
#include <piqp/piqp.hpp>

namespace af::routing::qp {
struct Context {
    std::unique_ptr<piqp::SparseSolver<double>> solver;
    Problem previous;
    uint64_t cancel=0;
};
static bool pattern(const Sparse& a,const Sparse& b) {
    if(a.rows()!=b.rows()||a.cols()!=b.cols()||a.nonZeros()!=b.nonZeros()) return false;
    return std::equal(a.outerIndexPtr(),a.outerIndexPtr()+a.cols()+1,b.outerIndexPtr())&&
        std::equal(a.innerIndexPtr(),a.innerIndexPtr()+a.nonZeros(),b.innerIndexPtr());
}
static void settings(piqp::SparseSolver<double>& solver) {
    auto& s=solver.settings(); s.verbose=false; s.max_iter=250;
    s.eps_abs=s.eps_rel=s.eps_duality_gap_abs=s.eps_duality_gap_rel=1e-9;
    s.check_duality_gap=true;
}
static void prepare(Context& context,Problem p) {
    const auto& old=context.previous;
    const bool reuse=context.solver&&pattern(p.P,old.P)&&pattern(p.A,old.A)&&pattern(p.G,old.G);
    if(!reuse) { context.solver=std::make_unique<piqp::SparseSolver<double>>(); settings(*context.solver); }
    if(reuse) context.solver->update(p.P,p.q,p.A,p.b,p.G,p.lower,p.upper);
    else context.solver->setup(p.P,p.q,p.A,p.b,p.G,p.lower,p.upper);
    context.previous=std::move(p);
}
static void install(kernel::AfV3SqpState& state,const Vector& x,const Vector& dual,
                    std::vector<int>& active,std::vector<double>& multipliers) {
    for(int i=0;i<state.job->count;++i) state.candidate[i]={x[3*i],x[3*i+1],x[3*i+2]};
    active.resize(dual.size()); std::iota(active.begin(),active.end(),0);
    multipliers.assign(dual.data(),dual.data()+dual.size());
}
static bool candidate(kernel::AfV3SqpState& state,std::vector<int>& active,std::vector<double>& multipliers) {
    auto context=std::static_pointer_cast<Context>(state.job->candidate_context);
    check_cancel(context->cancel); prepare(*context,problem(state));
    const auto status=context->solver->solve(); check_cancel(context->cancel);
    const auto& result=context->solver->result();
    if(status!=piqp::PIQP_SOLVED||!result.x.allFinite()||!result.z_l.allFinite())
        throw std::runtime_error("PIQP routing subproblem failed (status "+std::to_string(int(status))+").");
    install(state,result.x,result.z_l,active,multipliers); return true;
}
}
namespace af::routing {
void configure_piqp(kernel::AfV3SqpJob& job,uint64_t cancel) {
    auto context=std::make_shared<qp::Context>(); context->cancel=cancel;
    job.candidate_context=std::move(context); job.candidate_solver=qp::candidate;
}
}
