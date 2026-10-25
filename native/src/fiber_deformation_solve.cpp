#include "fiber_deformation.hpp"
namespace af::fiber {
static Sparse laplacian(const Preparation& v) {
    const int n=int(v.path->parameters.size()); std::vector<Triplet> entries;
    for(int i=0;i<n;++i) {
        if(!v.path->closed&&(i==0||i==n-1)) continue;
        const int before=(i+n-1)%n,after=(i+1)%n;
        const double a=(i?v.arc[size_t(i)]-v.arc[size_t(before)]:v.length-v.arc[size_t(before)])/v.length;
        const double b=(after?v.arc[size_t(after)]-v.arc[size_t(i)]:v.length-v.arc[size_t(i)])/v.length;
        if(std::min(a,b)<1e-10) continue; // Zero-length spans carry no curvature constraint.
        entries.emplace_back(i,before,2/(a*(a+b))); entries.emplace_back(i,i,-2/(a*b)); entries.emplace_back(i,after,2/(b*(a+b)));
    }
    Sparse result(n,n); result.setFromTriplets(entries.begin(),entries.end()); return result;
}
static void factor(Preparation& v,const Sparse& h,uint64_t cancel) {
    std::vector<Triplet> reduced,coupling; std::vector<int> pinned(size_t(h.rows()),-1);
    for(size_t i=0;i<v.pins.size();++i) pinned[size_t(v.pins[i])]=int(i);
    for(int j=0;j<h.outerSize();++j) for(Sparse::InnerIterator it(h,j);it;++it) {
        const int row=v.free_index[size_t(it.row())],col=v.free_index[size_t(it.col())];
        if(row<0) continue;
        if(col>=0) reduced.emplace_back(row,col,it.value()); else coupling.emplace_back(row,pinned[size_t(it.col())],it.value());
    }
    Sparse matrix(v.free.size(),v.free.size()); matrix.setFromTriplets(reduced.begin(),reduced.end());
    v.coupling.resize(v.free.size(),v.pins.size()); v.coupling.setFromTriplets(coupling.begin(),coupling.end());
    check_cancel(cancel); if(v.free.empty()) return;
    v.factor.compute(matrix); check_cancel(cancel);
    if(v.factor.info()!=Eigen::Success) throw std::runtime_error("Fiber shape reconstruction factorization failed.");
}
void prepare_reconstruction(Preparation& v,uint64_t cancel) {
    const int n=int(v.path->parameters.size()); v.free_index.assign(size_t(n),-1);
    for(int i=0;i<n;++i) if(!std::binary_search(v.pins.begin(),v.pins.end(),i)) {
        v.free_index[size_t(i)]=int(v.free.size()); v.free.push_back(i);
    }
    v.laplacian=laplacian(v); Sparse mass(n,n);
    for(int i=0;i<n;++i) mass.insert(i,i)=v.mass[size_t(i)];
    v.bending=std::pow(.2,4)*v.laplacian.transpose()*mass;
    const Sparse h=mass+v.bending*v.laplacian; factor(v,h,cancel);
}
static Vertices raw_points(const Preparation& v,const std::vector<std::vector<Map>>& maps,std::vector<M3>& linear,uint64_t cancel) {
    Vertices points=Vertices::Zero(v.points.rows(),3); linear.assign(size_t(v.points.rows()),M3::Zero());
    for(int i=0;i<points.rows();++i) {
        check_cancel(cancel);
        for(size_t b=0;b<maps.size();++b) if(v.weights(i,int(b))>0) {
            const auto transform=interpolated(v,maps[b],i); const double w=v.weights(i,int(b));
            points.row(i)+=(w*(transform.linear*v.points.row(i).transpose()+transform.translation)).transpose();
            linear[size_t(i)]+=w*transform.linear;
        }
    }
    return points;
}
static void pins(const Preparation& v,Vertices& raw,const double* goals) {
    Vertices delta(v.pins.size(),3);
    for(size_t p=0;p<v.pins.size();++p) delta.row(int(p))=V3(goals+3*p).transpose()-raw.row(v.pins[p]);
    for(int i=0;i<raw.rows();++i) for(size_t p=0;p<v.pins.size();++p)
        raw.row(i)+=kernel(distance(v,v.arc[size_t(i)],v.arc[size_t(v.pins[p])])/pin_width(v,int(p)))*delta.row(int(p));
}
static Vertices reconstruct(const Preparation& v,const Vertices& raw,const std::vector<M3>& linear,const double* goals,uint64_t cancel) {
    const int n=int(v.path->parameters.size()); Vertices details=v.laplacian*v.points.topRows(n);
    for(int i=0;i<n;++i) details.row(i)=(linear[size_t(i)]*details.row(i).transpose()).transpose().eval();
    const Vertices target=v.bending*(details-v.laplacian*raw.topRows(n));
    const Vertices fixed=Eigen::Map<const Vertices>(goals,int(v.pins.size()),3)-raw(v.pins,Eigen::all);
    const Vertices rhs=target(v.free,Eigen::all)-v.coupling*fixed;
    Vertices result=raw.topRows(n); check_cancel(cancel);
    if(!v.free.empty()) {
        const Vertices solution=v.factor.solve(rhs);
        result(v.free,Eigen::all)+=solution;
    }
    result(v.pins,Eigen::all)=Eigen::Map<const Vertices>(goals,int(v.pins.size()),3);
    check_cancel(cancel); if(!result.allFinite()) throw std::runtime_error("Fiber shape reconstruction produced nonfinite points.");
    return result;
}
void evaluate(const Preparation& v,const uint64_t* meshes,const double* frames,const double* goals,double* output,uint64_t cancel) {
    const auto maps=fit(v,meshes,frames,cancel); std::vector<M3> linear;
    auto raw=raw_points(v,maps,linear,cancel); pins(v,raw,goals);
    const auto result=reconstruct(v,raw,linear,goals,cancel); const int n=int(result.rows());
    for(int i=0;i<raw.rows();++i) {
        check_cancel(cancel); const int sample=i<n?i:v.knots[size_t((i-n)/3)];
        Eigen::Map<V3>(output+3*i)=(result.row(sample)+(raw.row(i)-raw.row(sample))).transpose();
    }
}
}
