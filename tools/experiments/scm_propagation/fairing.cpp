// Isolated curve reconstruction experiment. Never linked into the application.
#include "regional.cpp"
#include <memory>
using Dense=Eigen::MatrixXd;
struct Fairing {
    Trial* trial;
    Dense laplacian,mass,bending,hessian,coupling;
    std::vector<int> free;
    Eigen::LDLT<Dense> factor;
};
static Dense positions(const Points& points,int count) {
    Dense result(count,3);
    for(int i=0;i<count;++i) result.row(i)=points[size_t(i)];
    return result;
}
static Dense laplacian(const Trial& t) {
    Dense result=Dense::Zero(t.samples,t.samples);
    const double length=t.arc[size_t(t.samples-1)];
    for(int i=1;i<t.samples-1;++i) {
        const double a=(t.arc[size_t(i)]-t.arc[size_t(i-1)])/length;
        const double b=(t.arc[size_t(i+1)]-t.arc[size_t(i)])/length;
        if(std::min(a,b)<1e-10) throw std::runtime_error("Coincident samples in experiment.");
        result(i,i-1)=2/(a*(a+b)); result(i,i)=-2/(a*b); result(i,i+1)=2/(b*(a+b));
    }
    return result;
}
static void factor(Fairing& f,double fraction) {
    const auto& t=*f.trial; f.laplacian=laplacian(t); f.mass=Dense::Zero(t.samples,t.samples);
    for(int i=0;i<t.samples;++i) f.mass(i,i)=cell(t,i)/t.arc[size_t(t.samples-1)];
    f.bending=std::pow(fraction,4)*f.laplacian.transpose()*f.mass;
    f.hessian=f.mass+f.bending*f.laplacian;
    for(int i=0;i<t.samples;++i) if(std::find(t.pins.begin(),t.pins.end(),i)==t.pins.end()) f.free.push_back(i);
    const Dense reduced=f.hessian(f.free,f.free); f.factor.compute(reduced);
    f.coupling=f.hessian(f.free,t.pins);
    if(f.factor.info()!=Eigen::Success) throw std::runtime_error("Experimental factorization failed.");
}
static M local_linear(const Trial& t,const std::vector<Map>& transforms,int row) {
    const double u=t.arc[size_t(row)]/t.arc[size_t(t.samples-1)]*(t.regions-1);
    const int low=std::clamp(int(u),0,t.regions-2); const double f=u-low;
    const double weights[4]{std::pow(1-f,3)/6,(3*f*f*f-6*f*f+4)/6,(-3*f*f*f+3*f*f+3*f+1)/6,f*f*f/6};
    M result=M::Zero();
    for(int j=0;j<4;++j) result+=weights[j]*transforms[size_t(std::clamp(low+j-1,0,t.regions-1))].linear;
    return result;
}
static Dense differential(const Fairing& f,const std::vector<std::vector<Map>>& transforms) {
    const auto& t=*f.trial; const Dense rest=f.laplacian*positions(t.points,t.samples);
    Dense result=Dense::Zero(t.samples,3);
    for(int i=0;i<t.samples;++i) for(int b=0;b<t.parents;++b)
        result.row(i)+=(t.weights[size_t(i*t.parents+b)]*local_linear(t,transforms[size_t(b)],i)*rest.row(i).transpose()).transpose();
    return result;
}
static Dense reconstructed(Fairing& f,const double* current,const double* goals) {
    const auto& t=*f.trial; const auto transforms=maps(t,nullptr,current);
    auto raw=blended(t,transforms); exact_pins(t,raw,goals);
    const Dense targets=f.mass*positions(raw,t.samples)+f.bending*differential(f,transforms);
    const Dense pins=positions(read(goals,int(t.pins.size())),int(t.pins.size()));
    const Dense rhs=targets(f.free,Eigen::all)-f.coupling*pins;
    const Dense solution=f.factor.solve(rhs);
    if(!solution.allFinite()) throw std::runtime_error("Invalid reconstructed curve.");
    Dense result(t.samples,3); result(f.free,Eigen::all)=solution; result(t.pins,Eigen::all)=pins;
    return result;
}
API void* fair_prepare(void* trial,double fraction) {
    try {
        if(!trial||fraction<=0) throw std::runtime_error("Invalid fairing configuration.");
        auto f=std::make_unique<Fairing>(); f->trial=static_cast<Trial*>(trial); factor(*f,fraction);
        return f.release();
    } catch(const std::exception& e) { last_error=e.what(); return nullptr; }
}
API int fair_evaluate(void* handle,const double* current,const double* goals,double* output) {
    try {
        auto& f=*static_cast<Fairing*>(handle); const auto result=reconstructed(f,current,goals);
        // This fixture has one sample and three coincident handles per authored polyline point.
        for(int i=0;i<f.trial->rows;++i) {
            const int node=i<f.trial->samples?i:(i-f.trial->samples)/3;
            Eigen::Map<V>(output+3*i)=result.row(node);
        }
        return 0;
    } catch(const std::exception& e) { last_error=e.what(); return 1; }
}
API void fair_release(void* handle) { delete static_cast<Fairing*>(handle); }
