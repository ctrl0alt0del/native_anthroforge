// Included inside the copied routing-kernel namespace after its original candidate solve.
static void af_bench_objective(const AfV3SqpState& state,afbench::Problem& p) {
    std::vector<double> diagonal,lower; std::vector<Vec> rhs;
    af_v3_sqp_bands(const_cast<AfV3SqpState&>(state),diagonal,lower,rhs);
    const int n=state.job->count; std::vector<afbench::Triplet> entries;
    p.q.resize(3*n);
    for(int i=0;i<n;++i) for(int axis=0;axis<3;++axis) {
        const int at=3*i+axis; p.q[at]=-(&rhs[i].x)[axis];
        entries.emplace_back(at,at,diagonal[i]);
        if(i) { entries.emplace_back(at,at-3,lower[i]); entries.emplace_back(at-3,at,lower[i]); }
    }
    p.P.resize(3*n,3*n); p.P.setFromTriplets(entries.begin(),entries.end());
}
static void af_bench_pins(const AfV3SqpState& state,afbench::Problem& p) {
    const auto& job=*state.job; std::vector<afbench::Triplet> entries;
    p.b.resize(3*job.pin_count);
    for(int i=0;i<job.pin_count;++i) for(int axis=0;axis<3;++axis) {
        entries.emplace_back(3*i+axis,3*int(job.pins[i])+axis,1);
        p.b[3*i+axis]=job.targets[3*i+axis];
    }
    p.A.resize(p.b.size(),3*job.count); p.A.setFromTriplets(entries.begin(),entries.end());
}
static void af_bench_contacts(const AfV3SqpState& state,afbench::Problem& p) {
    const int count=int(state.contacts.size()); std::vector<afbench::Triplet> entries;
    p.lower.resize(count); p.upper=afbench::Vector::Constant(count,INFINITY);
    for(int i=0;i<count;++i) {
        const auto& row=state.contacts[i];
        p.lower[i]=af_v3_sqp_apply(row,state.points)-af_v3_sqp_linear_gap(row);
        for(int node=row.edge;node<=row.edge+1;++node) {
            const Vec j=af_v3_sqp_jacobian(row,node);
            for(int axis=0;axis<3;++axis) entries.emplace_back(i,3*node+axis,(&j.x)[axis]);
        }
    }
    p.G.resize(count,3*state.job->count); p.G.setFromTriplets(entries.begin(),entries.end());
}
static afbench::Problem af_bench_problem(const AfV3SqpState& state) {
    afbench::Problem problem;
    af_bench_objective(state,problem); af_bench_pins(state,problem); af_bench_contacts(state,problem);
    return problem;
}
static afbench::Vector af_bench_vector(const std::vector<Vec>& points) {
    afbench::Vector result(3*points.size());
    for(size_t i=0;i<points.size();++i) for(int axis=0;axis<3;++axis) result[3*i+axis]=(&points[i].x)[axis];
    return result;
}
static void af_bench_install(AfV3SqpState& state,const afbench::Vector& x,const afbench::Vector& dual,
                             std::vector<int>& active,std::vector<double>& multipliers) {
    for(int i=0;i<state.job->count;++i) state.candidate[i]={x[3*i],x[3*i+1],x[3*i+2]};
    active.resize(dual.size()); std::iota(active.begin(),active.end(),0);
    multipliers.assign(dual.data(),dual.data()+dual.size());
}
