#pragma once
#include <piqp/piqp.hpp>
#include <chrono>
#include <iomanip>
#include <memory>
#include <sstream>
#include <vector>

namespace afbench {
using Vector = Eigen::VectorXd;
using Sparse = Eigen::SparseMatrix<double>;
using Dense = Eigen::MatrixXd;
using Triplet = Eigen::Triplet<double>;
struct Problem { Sparse P,A,G; Vector q,b,lower,upper; };
struct Record {
    int step=0,backend=0,points=0,contacts=0,status=0,iterations=0,reused=0,dual_valid=1;
    double total=0,assembly=0,prepare=0,solve=0,primal=0,stationarity=0,objective=0;
};
struct Config { int backend=0,paired=0,audit=0,step=0; double tolerance=1e-9; };
inline thread_local Config config;
inline thread_local std::vector<Record> records;
inline double now() {
    return std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
inline bool pattern(const Sparse& a,const Sparse& b) {
    if(a.rows()!=b.rows()||a.cols()!=b.cols()||a.nonZeros()!=b.nonZeros()) return false;
    return std::equal(a.outerIndexPtr(),a.outerIndexPtr()+a.cols()+1,b.outerIndexPtr())&&
        std::equal(a.innerIndexPtr(),a.innerIndexPtr()+a.nonZeros(),b.innerIndexPtr());
}
template<class Solver> void settings(Solver& solver) {
    auto& s=solver.settings(); s.verbose=false; s.max_iter=250;
    s.eps_abs=s.eps_rel=s.eps_duality_gap_abs=s.eps_duality_gap_rel=config.tolerance;
    s.check_duality_gap=true;
}
struct Context {
    std::unique_ptr<piqp::SparseSolver<double>> sparse;
    std::unique_ptr<piqp::DenseSolver<double>> dense;
    Problem previous; int dense_n=-1,dense_a=-1,dense_g=-1;
};
inline void prepare_sparse(Context& context,const Problem& p,Record& row) {
    const auto& old=context.previous;
    row.reused=context.sparse&&pattern(p.P,old.P)&&pattern(p.A,old.A)&&pattern(p.G,old.G);
    if(!row.reused) context.sparse=std::make_unique<piqp::SparseSolver<double>>();
    settings(*context.sparse);
    if(row.reused) context.sparse->update(p.P,p.q,p.A,p.b,p.G,p.lower,p.upper);
    else context.sparse->setup(p.P,p.q,p.A,p.b,p.G,p.lower,p.upper);
    context.previous=p;
}
inline void prepare_dense(Context& context,const Problem& p,Record& row) {
    row.reused=context.dense&&context.dense_n==p.P.rows()&&context.dense_a==p.A.rows()&&context.dense_g==p.G.rows();
    if(!row.reused) context.dense=std::make_unique<piqp::DenseSolver<double>>();
    settings(*context.dense);
    const Dense P(p.P),A(p.A),G(p.G);
    if(row.reused) context.dense->update(P,p.q,A,p.b,G,p.lower,p.upper);
    else context.dense->setup(P,p.q,A,p.b,G,p.lower,p.upper);
    context.dense_n=int(p.P.rows()); context.dense_a=int(p.A.rows()); context.dense_g=int(p.G.rows());
}
template<class Solver> Vector solve(Solver& solver,Record& row,Vector& dual) {
    const double begin=config.audit?now():0;
    row.status=int(solver.solve());
    const auto& result=solver.result(); row.iterations=int(result.info.iter);
    dual=result.z_l;
    if(config.audit) row.solve=now()-begin;
    return result.x;
}
inline Vector piqp(Context& context,const Problem& problem,Record& row,Vector& dual) {
    const double begin=config.audit?now():0;
    if(row.backend==1) prepare_sparse(context,problem,row); else prepare_dense(context,problem,row);
    if(config.audit) row.prepare=now()-begin;
    return row.backend==1?solve(*context.sparse,row,dual):solve(*context.dense,row,dual);
}
inline double maximum(const Vector& value) { return value.size()?value.cwiseAbs().maxCoeff():0; }
inline void quality(const Problem& p,const Vector& x,const Vector& dual,Record& row) {
    const Vector gap=p.G*x-p.lower;
    row.primal=std::max(maximum(p.A*x-p.b),gap.size()?std::max(0.,-gap.minCoeff()):0.);
    Vector gradient=p.P*x+p.q-p.G.transpose()*dual;
    // Pin multipliers are unrestricted; stationarity is measured on free coordinates.
    for(int col=0;col<p.A.outerSize();++col)
        if(p.A.outerIndexPtr()[col+1]!=p.A.outerIndexPtr()[col]) gradient[col]=0;
    row.stationarity=maximum(gradient);
    row.objective=.5*x.dot(p.P*x)+p.q.dot(x);
}
inline const char* csv() {
    static thread_local std::string text; std::ostringstream out; out<<std::setprecision(17);
    out<<"step,backend,points,contacts,status,iterations,reused,dual_valid,total_ms,assembly_ms,prepare_ms,solve_ms,primal,stationarity,objective\n";
    for(const auto& r:records)
        out<<r.step<<','<<r.backend<<','<<r.points<<','<<r.contacts<<','<<r.status<<','<<r.iterations<<','<<r.reused<<','<<r.dual_valid<<','
           <<r.total<<','<<r.assembly<<','<<r.prepare<<','<<r.solve<<','<<r.primal<<','<<r.stationarity<<','<<r.objective<<'\n';
    text=out.str(); return text.c_str();
}
}
