// SPDX-License-Identifier: GPL-3.0-or-later
// Qualified addon numerical core, pinned unchanged with hashes in sources.json.
#include "../migration/smoothing/src/core.cpp"
#include "../migration/smoothing/src/height.cpp"
#include "tissue_height.hpp"
#include "height_box_solver.hpp"
#include <piqp/results.hpp>

// Reuse the pinned material/field/QP implementation. Geometry acceptance belongs
// to the complete canonical mesh, not a per-triangle normal-dot comparison.
namespace af::tissue {
class CertifiedHeights final : public afs::QpSolver {
    std::unique_ptr<afs::QpSolver> solver_=make_box_heights();
public:
    afs::Solution solve(const afs::Quadratic& p,const afs::Options& options,afs::Diagnostics& report) override {
        auto solution=solver_->solve(p,options,report);
        if(report.solver_status==piqp::PIQP_MAX_ITER_REACHED&&afs::certify(p,solution,options.tolerance,report))
            solution.status=afs::QpStatus::solved;
        return solution;
    }
};
static afs::Field height_field(afh::Domain& d,const Vertices& base,const Vertices& own,const double* s,AF_HeightReport& r) {
    afs::require(!d.triangles.empty(),"No usable material triangles");
    afh::compact(d,base); afh::boundaries(d);
    auto field=afh::field(d,base,own,s[0],s[1],s[2]);
    afs::validate_field(field,int(d.ids.size()));
    r.samples=int(d.ids.size()); r.pinned=int(std::count(d.fixed.begin(),d.fixed.end(),true)); r.skipped_triangles=d.skipped;
    return field;
}
static Vertices height_result(const afh::Domain& d,const Vertices& base,const Vertices& own,const afs::Field& field,AF_HeightReport& report) {
    afs::CotangentBiharmonic builder; afs::NoSupport source;
    afs::Session session(d.mesh,builder,std::make_unique<CertifiedHeights>(),afs::Options{});
    const auto result=session.run(field,source); afh::metrics(report,result);
    afs::require(result.status==afs::Status::success,result.message.c_str());
    report.status=result.metrics.solver_status==piqp::PIQP_MAX_ITER_REACHED?1:0;
    report.max_change=afs::max_abs(result.values-field.target);
    Vertices output=own;
    for(int i=0;i<int(d.ids.size());++i) if(!d.fixed[i]) {
        const int j=d.ids[i]; output.row(j)=base.row(j)+(own.row(j)-base.row(j))*(result.values[i]/field.target[i]);
    }
    return output;
}
Vertices smooth_heights(const Vertices& base,const Vertices& own,const std::vector<int64_t>& faces,
                       const std::vector<int64_t>& labels,int part,const double* settings,AF_HeightReport& report) {
    const double start=afs::now_ms();
    auto domain=afh::triangles(base,faces.data(),int(labels.size()),3,labels.data(),part);
    const auto field=height_field(domain,base,own,settings,report);
    if(report.samples==report.pinned) return own;
    auto result=height_result(domain,base,own,field,report);
    report.total_ms=afs::now_ms()-start;
    return result;
}
}
