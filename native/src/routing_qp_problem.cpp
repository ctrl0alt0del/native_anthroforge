#include "routing_qp.hpp"

namespace af::routing::qp {
static void objective(kernel::AfV3SqpState& state,Problem& p) {
    std::vector<double> diagonal,lower; std::vector<Vec> rhs;
    kernel::af_v3_sqp_bands(state,diagonal,lower,rhs);
    const int n=state.job->count; std::vector<Triplet> entries;
    p.q.resize(3*n);
    for(int i=0;i<n;++i) for(int axis=0;axis<3;++axis) {
        const int at=3*i+axis; p.q[at]=-(&rhs[i].x)[axis];
        entries.emplace_back(at,at,diagonal[i]);
        if(i) { entries.emplace_back(at,at-3,lower[i]); entries.emplace_back(at-3,at,lower[i]); }
    }
    p.P.resize(3*n,3*n); p.P.setFromTriplets(entries.begin(),entries.end());
}
static void pins(const kernel::AfV3SqpState& state,Problem& p) {
    const auto& job=*state.job; std::vector<Triplet> entries;
    p.b.resize(3*job.pin_count);
    for(int i=0;i<job.pin_count;++i) for(int axis=0;axis<3;++axis) {
        entries.emplace_back(3*i+axis,3*int(job.pins[i])+axis,1);
        p.b[3*i+axis]=job.targets[3*i+axis];
    }
    p.A.resize(p.b.size(),3*job.count); p.A.setFromTriplets(entries.begin(),entries.end());
}
static void contacts(const kernel::AfV3SqpState& state,Problem& p) {
    const int count=int(state.contacts.size()); std::vector<Triplet> entries;
    p.lower.resize(count); p.upper=Vector::Constant(count,INFINITY);
    for(int i=0;i<count;++i) {
        const auto& row=state.contacts[i];
        p.lower[i]=kernel::af_v3_sqp_apply(row,state.points)-kernel::af_v3_sqp_linear_gap(row);
        for(int node=row.edge;node<=row.edge+1;++node) {
            const Vec j=kernel::af_v3_sqp_jacobian(row,node);
            for(int axis=0;axis<3;++axis) entries.emplace_back(i,3*node+axis,(&j.x)[axis]);
        }
    }
    p.G.resize(count,3*state.job->count); p.G.setFromTriplets(entries.begin(),entries.end());
}
Problem problem(kernel::AfV3SqpState& state) {
    Problem p; objective(state,p); pins(state,p); contacts(state,p); return p;
}
}
