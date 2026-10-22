#include "height_box_solver.hpp"
#include <piqp/piqp.hpp>
#include <sstream>

namespace af::tissue {
using afs::Sparse;
using afs::Vector;
struct HeightBox {
    Sparse P;
    Vector q,lower,upper,fixed;
    std::vector<int> free,pins,bounds;
};
static std::vector<int> selector(const Sparse& matrix,int columns) {
    std::vector<int> indices(columns,-1),counts(matrix.rows(),0);
    for(int j=0;j<matrix.outerSize();++j) for(Sparse::InnerIterator value(matrix,j);value;++value) {
        afs::require(value.value()==1&&indices[j]==-1,"Height constraints must select distinct variables");
        indices[j]=int(value.row()); ++counts[value.row()];
    }
    afs::require(std::all_of(counts.begin(),counts.end(),[](int count){return count==1;}),"Invalid height selector");
    return indices;
}
static void partition(HeightBox& box,const afs::Quadratic& p) {
    const int size=int(p.q.size()); box.pins=selector(p.A,size); box.bounds=selector(p.G,size);
    box.fixed=Vector::Zero(size); box.free.assign(size,-1); int count=0;
    for(int i=0;i<size;++i) {
        afs::require((box.pins[i]>=0)!=(box.bounds[i]>=0),"Height variables require one pin or bound");
        if(box.pins[i]>=0) box.fixed[i]=p.b[box.pins[i]];
        else box.free[i]=count++;
    }
    box.q.resize(count); box.lower.resize(count); box.upper.resize(count);
}
static void objective(HeightBox& box,const afs::Quadratic& p) {
    const Vector linear=p.q+p.P*box.fixed; std::vector<afs::Triplet> entries;
    for(int j=0;j<p.P.outerSize();++j) if(box.free[j]>=0)
        for(Sparse::InnerIterator value(p.P,j);value;++value) if(box.free[value.row()]>=0)
            entries.emplace_back(box.free[value.row()],box.free[j],value.value());
    box.P.resize(box.q.size(),box.q.size()); box.P.setFromTriplets(entries.begin(),entries.end());
    for(int i=0;i<int(box.free.size());++i) if(box.free[i]>=0) {
        const int j=box.free[i],row=box.bounds[i]; box.q[j]=linear[i];
        box.lower[j]=p.lower[row]; box.upper[j]=p.upper[row];
    }
}
static HeightBox reduced(const afs::Quadratic& p,afs::Diagnostics& report) {
    const double start=afs::now_ms(); HeightBox box; partition(box,p); objective(box,p);
    report.assembly_ms+=afs::now_ms()-start; return box;
}
static void configure(piqp::SparseSolver<double>& solver,const afs::Options& o) {
    auto& s=solver.settings(); s.verbose=false; s.max_iter=o.max_iterations;
    s.eps_abs=s.eps_rel=s.eps_duality_gap_abs=s.eps_duality_gap_rel=std::min(1e-8,o.tolerance*.01);
    s.check_duality_gap=true; s.preconditioner_scale_cost=o.robust_linear_solve;
    s.iterative_refinement_always_enabled=o.robust_linear_solve;
}
static void prepare(piqp::SparseSolver<double>& solver,const HeightBox& box,const afs::Options& o,afs::Diagnostics& report) {
    const double start=afs::now_ms(); configure(solver,o);
    solver.setup(box.P,box.q,piqp::nullopt,piqp::nullopt,piqp::nullopt,piqp::nullopt,piqp::nullopt,box.lower,box.upper);
    report.setup_ms+=afs::now_ms()-start; ++report.setups;
}
static afs::Solution expanded(const afs::Quadratic& p,const HeightBox& box,const piqp::Result<double>& result,piqp::Status status) {
    afs::Solution out{box.fixed,Vector::Zero(p.b.size()),Vector::Zero(p.lower.size()),Vector::Zero(p.upper.size())};
    out.iterations=int(result.info.iter);
    out.status=status==piqp::PIQP_SOLVED?afs::QpStatus::solved:
        status==piqp::PIQP_PRIMAL_INFEASIBLE?afs::QpStatus::infeasible:afs::QpStatus::failed;
    for(int i=0;i<int(box.free.size());++i) if(box.free[i]>=0) {
        const int j=box.free[i],row=box.bounds[i]; out.x[i]=result.x[j];
        out.z_lower[row]=result.z_bl[j]; out.z_upper[row]=result.z_bu[j];
    }
    const Vector gradient=p.P*out.x+p.q;
    for(int i=0;i<int(box.pins.size());++i) if(box.pins[i]>=0) out.y[box.pins[i]]=-gradient[i];
    return out;
}
class BoxHeights final : public afs::QpSolver {
public:
    afs::Solution solve(const afs::Quadratic& p,const afs::Options& o,afs::Diagnostics& report) override {
        const auto box=reduced(p,report); piqp::SparseSolver<double> solver; prepare(solver,box,o,report);
        const double start=afs::now_ms(); const auto status=solver.solve(); const auto& result=solver.result();
        report.solve_ms+=afs::now_ms()-start; report.iterations+=int(result.info.iter); report.solver_status=int(status);
        std::ostringstream detail; detail<<" primal="<<result.info.primal_res<<" dual="<<result.info.dual_res<<" gap="<<result.info.duality_gap;
        report.solver_detail=detail.str(); return expanded(p,box,result,status);
    }
};
std::unique_ptr<afs::QpSolver> make_box_heights() { return std::make_unique<BoxHeights>(); }
}
