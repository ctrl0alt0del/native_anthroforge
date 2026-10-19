// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_relaxation.hpp"
#include "tissue_math.hpp"
#include <set>
#include <chrono>
namespace af::tissue::kernel {
inline Vec load3(const double* p) { return af_vec(p); }
#include "../migration/tissue/kernel_4.hpp"
}

namespace af::tissue {
static kernel::af_tissue::Settings parameters(const Mesh& rest,const AfTissueRelax& s) {
    const int front=rest.tissue.kind==3?int(rest.tissue.source_count):0;
    const auto edges=mesh_edges(mesh_faces(rest),0);
    const bool closed=std::all_of(edges.begin(),edges.end(),[](const auto& e){return e.second.count==2;});
    return {s.iterations,s.passes,front,.0015*s.sagginess/.58,s.shape,closed?s.volume:0,
        .35,.55,.15,s.slack,s.limit,s.tolerance,{s.gravity[0],s.gravity[1],s.gravity[2]}};
}
Vertices relax_static(const Mesh& rest,const Constraints& constraints,const AfTissueRelax& settings,double* report,uint64_t cancel) {
    const kernel::CancelScope scope(cancel); const auto config=parameters(rest,settings);
    const int count=int(rest.vertices.rows()),triangles=int(rest.triangles.rows());
    const int tethers=int(constraints.tethers.size()/6);
    auto state=kernel::af_tissue::create(rest.vertices.data(),count,rest.triangles.data(),triangles,
        constraints.mass.data(),constraints.goals.data(),config);
    Vertices output(count,3);
    const int status=kernel::af_tissue::solve(state,config,constraints.tethers.data(),tethers,output.data(),report);
    check_cancel(cancel);
    if(status||!output.allFinite()) throw std::runtime_error("NUMERICAL_FAILURE: tissue static relaxation.");
    return output;
}
}
