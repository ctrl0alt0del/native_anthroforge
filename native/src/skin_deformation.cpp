#include "skin_deformation_kernel.hpp"
#include <mutex>
namespace af::skin::deformation {
using namespace af_ad;
struct Preparation {
    State state;
    Eigen::RowVector3d center;
    double scale=1;
    mutable std::mutex mutex;
};
static void validate(const AfSkinReference& a) {
    if(!a.proxy||!a.tets||!a.points||!a.samples||!a.weights||a.proxy_count<4||a.tet_count<1||a.point_count<1||a.sample_count<1)
        throw std::runtime_error("Skin reference requires a proxy, skin and anatomical samples.");
    if((a.method!=0&&a.method!=2)||a.handles<5||a.handles>1024||!std::isfinite(a.strength)||a.strength<=0)
        throw std::runtime_error("Invalid skin deformation settings.");
    if(a.method==2&&a.proxy_count<a.handles) throw std::runtime_error("FAST handles exceed proxy vertices.");
}
static M normalized(const double* values,int count,const Preparation& p) {
    M result=(Eigen::Map<const RM>(values,count,3).rowwise()-p.center)/p.scale;
    if(!result.allFinite()) throw std::runtime_error("Skin deformation requires finite positions.");
    return result;
}
static void initialize(Preparation& p,const AfSkinReference& a,uint64_t cancel) {
    auto& s=p.state; const M points=Eigen::Map<const RM>(a.points,a.point_count,3);
    p.center=(points.colwise().maxCoeff()+points.colwise().minCoeff())*.5;
    p.scale=(points.colwise().maxCoeff()-points.colwise().minCoeff()).maxCoeff();
    if(!points.allFinite()||p.scale<=0) throw std::runtime_error("Skin reference has zero or invalid extent.");
    s.rest=normalized(a.proxy,a.proxy_count,p); s.points=normalized(a.points,a.point_count,p);
    s.samples=normalized(a.samples,a.sample_count,p); s.tets=Eigen::Map<const RI>(a.tets,a.tet_count,4);
    s.sample_weights=Eigen::Map<const V>(a.weights,a.sample_count); s.method=a.method; s.lambda=a.strength;
    s.token=cancel; s.cancel=a.cache_path?a.cache_path:"";
    if(s.tets.minCoeff()<0||s.tets.maxCoeff()>=a.proxy_count||!s.sample_weights.allFinite()||s.sample_weights.minCoeff()<=0)
        throw std::runtime_error("Skin reference has invalid proxy indices or sample weights.");
}
std::shared_ptr<Preparation> prepare(const AfSkinReference& input,uint64_t cancel) {
    check_cancel(cancel); validate(input); auto p=std::make_shared<Preparation>(); initialize(*p,input,cancel);
    common(p->state); check_cancel(cancel);
    if(input.method==0) stiffness(p->state); else reduced_prepare(p->state,input.handles);
    check_cancel(cancel); p->state.token=0; return p;
}
static void copy_world(double* out,const M& points,const Preparation& p) {
    Eigen::Map<RM>(out,points.rows(),3)=(points*p.scale).rowwise()+p.center;
}
static void diagnostics(State& s,const M& x,double* out) {
    physical(s,x); out[0]=s.iterations; out[1]=s.residual; out[2]=s.minimum_j;
    out[3]=s.outside; out[4]=s.max_outside;
    out[5]=(s.skin*s.rest-s.points).rowwise().norm().maxCoeff();
}
void solve(Preparation& p,const double* targets,int count,double* points,double* predicted,double* report,uint64_t cancel) {
    std::lock_guard<std::mutex> lock(p.mutex); auto& s=p.state;
    if(!targets||!points||!predicted||!report||count!=s.samples.rows()) throw std::runtime_error("Invalid skin deformation output buffers.");
    check_cancel(cancel); s.token=cancel;
    const M delta=normalized(targets,count,p)-s.samples;
    const M x=s.method==0?linear(s,delta):reduced_solve(s,delta);
    const M output=s.points+s.skin*(x-s.rest),prediction=s.samples+s.constraints*(x-s.rest);
    if(!output.allFinite()||!prediction.allFinite()) throw std::runtime_error("Nonfinite skin deformation result.");
    diagnostics(s,x,report); check_cancel(cancel);
    copy_world(points,output,p); copy_world(predicted,prediction,p); s.token=0;
}
void embedding(Preparation& p,int* ids,double* weights) {
    std::lock_guard<std::mutex> lock(p.mutex);
    if(!ids||!weights) throw std::runtime_error("Missing skin embedding buffers.");
    Eigen::SparseMatrix<double,Eigen::RowMajor> rows=p.state.skin;
    std::fill(ids,ids+4*rows.rows(),0); std::fill(weights,weights+4*rows.rows(),0.);
    for(int i=0;i<rows.rows();++i) {
        int j=0;
        for(decltype(rows)::InnerIterator it(rows,i);it;++it) {
            if(j>=4) throw std::runtime_error("INVALID_EMBEDDING_ARITY");
            ids[4*i+j]=int(it.col()); weights[4*i+j++]=it.value();
        }
    }
}
template<class Derived> static uint64_t storage(const Eigen::MatrixBase<Derived>& matrix) {
    return uint64_t(matrix.size())*sizeof(typename Derived::Scalar);
}
static uint64_t storage(const S& matrix) {
    return uint64_t(matrix.data().allocatedSize())*(sizeof(double)+sizeof(int))+
        uint64_t(matrix.outerSize()+1)*sizeof(int)+(matrix.isCompressed()?0:uint64_t(matrix.outerSize())*sizeof(int));
}
static uint64_t fast_storage(const State& s) {
    const auto& f=s.fast;
    uint64_t bytes=storage(s.reduced_factor.matrixLDLT())+storage(s.reduced_factor.transpositionsP().indices());
    bytes+=storage(f.M_KG)+storage(f.Q)+storage(f.Mass_tilde)+storage(f.fixed_dim)+storage(f.interpolated);
    bytes+=storage(f.M_FullSolve)+storage(f.CSM)+storage(f.CSolveBlock1)+storage(f.L0)+storage(f.Lvel0);
    bytes+=storage(f.fext)+storage(f.fgrav)+storage(f.Pi_1)+f.free_mask.capacity()/8;
    for(const auto& matrix:f.CSM_M) bytes+=storage(matrix);
    return bytes;
}
static uint64_t state_storage(const State& s) {
    uint64_t bytes=storage(s.rest)+storage(s.points)+storage(s.samples)+storage(s.weights)+storage(s.basis)+storage(s.controls);
    bytes+=storage(s.tets)+storage(s.boundary)+storage(s.owners)+storage(s.handles)+storage(s.groups);
    bytes+=storage(s.skin)+storage(s.constraints)+storage(s.weighted)+storage(s.block)+storage(s.stiffness)+storage(s.lbs);
    bytes+=storage(s.reduced_constraints)+storage(s.reduced_hessian)+storage(s.sample_weights)+storage(s.identity);
    bytes+=s.elements.capacity()*sizeof(Element)+s.edges.capacity()*sizeof(decltype(s.edges)::value_type);
    for(const auto& edges:s.edges) bytes+=edges.capacity()*sizeof(decltype(s.edges)::value_type::value_type);
    if(s.method==0) bytes+=storage(s.factor.matrixL().nestedExpression())+storage(s.factor.vectorD())+
        storage(s.factor.permutationP().indices())+storage(s.factor.permutationPinv().indices());
    else bytes+=fast_storage(s);
    return bytes;
}
uint64_t bytes(const Preparation& p) {
    std::lock_guard<std::mutex> lock(p.mutex);
    // Retained buffers and factorization; allocator overhead is not an RSS measurement.
    return sizeof(Preparation)+state_storage(p.state);
}
}
