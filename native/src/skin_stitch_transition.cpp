#include "skin_stitch.hpp"
#include <tuple>
namespace af::skin_stitch {
static int rejection(int first,int second) {
    const int smaller=std::min(first,second),larger=std::max(first,second);
    if(smaller<4) return 1;
    if((larger-smaller)%2) throw std::runtime_error("Skin guide has incompatible boundary parity.");
    if(larger-smaller>12) return 2;
    return double(larger)/smaller>1.5?3:0;
}
static Transition candidate(const Vertices& first,const Vertices& second,int shift,uint64_t cancel) {
    const auto ring=skin_ring::rolled(second,(int(second.rows())-shift)%int(second.rows()));
    Transition out; out.shift=shift; out.boundary=int(first.rows()); out.annulus=int(second.rows());
    out.mesh=strip(first,ring,regular_faces(first,ring)); quality(out,cancel); return out;
}
static auto score(const Transition& transition) {
    return std::make_tuple(transition.intersections,transition.p95,transition.maximum,std::abs(transition.shift),transition.shift);
}
static Transition sparse(const Vertices& first,const Vertices& second,uint64_t cancel) {
    const int radius=std::min(3,std::max(1,int(std::min(first.rows(),second.rows()))/12));
    auto best=candidate(first,second,0,cancel);
    for(int i=1;i<=radius;++i) for(const int shift:{-i,i}) {
        check_cancel(cancel); auto current=candidate(first,second,shift,cancel);
        if(score(current)<score(best)) best=std::move(current);
    }
    best.candidates=1+2*radius; return best;
}
static Quads regular_strip(const Vertices& a,const Vertices& b,uint64_t cancel) {
    const auto first=skin_ring::canonical(a),second=skin_ring::aligned(first,b,cancel);
    return strip(first,second,regular_faces(first,second));
}
static double diagonal(const Vertices& points) {
    return (points.colwise().maxCoeff()-points.colwise().minCoeff()).norm();
}
static Transition staged(const Vertices& first,const Vertices& second,int reason,uint64_t cancel) {
    int count=int(std::nearbyint(.5*(first.rows()+second.rows())));
    if(count%2!=first.rows()%2) ++count;
    const Vertices middle=.5*(skin_ring::samples(first,count,cancel)+skin_ring::samples(second,count,cancel));
    const auto a=regular_strip(first,middle,cancel),b=regular_strip(middle,second,cancel);
    Transition out; out.mode=1; out.reason=reason; out.boundary=int(first.rows()); out.annulus=int(second.rows());
    out.mesh=weld({a,b},1e-7*diagonal(first),false,cancel); quality(out,cancel); return out;
}
static Transition side(const Vertices& first,const Vertices& second,uint64_t cancel) {
    const int reason=rejection(int(first.rows()),int(second.rows()));
    if(reason) return staged(first,second,reason,cancel);
    auto result=sparse(first,second,cancel);
    if(!result.intersections&&result.p95<=4&&result.maximum<=12) return result;
    return staged(first,second,4,cancel);
}
static Vertices coordinates(const Vertices& points,const Plane& plane) {
    const V3 reference=std::abs(plane.normal.z())>.9?V3::UnitY():V3::UnitZ();
    const V3 vertical=(reference-reference.dot(plane.normal)*plane.normal).normalized(),tangent=vertical.cross(plane.normal);
    const Vertices relative=points.rowwise()-plane.origin.transpose(); Vertices result(points.rows(),3);
    result.col(0)=relative*plane.normal; result.col(1)=relative*tangent; result.col(2)=relative*vertical; return result;
}
static Vertices enforce_symmetry(const Vertices& points,const Plane& plane,uint64_t cancel) {
    const auto tree=skin_loops::point_index(points,cancel); Vertices result=points;
    for(int i=0;i<points.rows();++i) {
        check_cancel(cancel); const V3 p=points.row(i),reflected=p-2*(p-plane.origin).dot(plane.normal)*plane.normal;
        const V3 q=points.row(tree->nearest(points,reflected).first);
        result.row(i)=.5*(p+q-2*(q-plane.origin).dot(plane.normal)*plane.normal);
    }
    return result;
}
static std::vector<Vertices> stages(const Vertices& first,const Vertices& second,const Plane& plane,uint64_t cancel) {
    const double ratio=double(std::max(first.rows(),second.rows()))/std::min(first.rows(),second.rows());
    const int count=std::max(1,int(std::ceil(std::log(ratio)/std::log(1.5)))); std::vector<Vertices> result{first};
    for(int i=1;i<count;++i) {
        const double alpha=double(i)/count,estimate=first.rows()*std::pow(double(second.rows())/first.rows(),alpha);
        const int size=std::max(4,2*int(std::nearbyint(estimate/2)));
        const Vertices points=(1-alpha)*skin_ring::samples(first,size,cancel)+alpha*skin_ring::samples(second,size,cancel);
        result.push_back(enforce_symmetry(points,plane,cancel));
    }
    result.push_back(second); return result;
}
static std::vector<Quad> equal_faces(int count) {
    std::vector<Quad> result;
    for(int i=0;i<count;++i) result.push_back({i,(i+1)%count,count+(i+1)%count,count+i});
    return result;
}
static Transition centered(const Vertices& first,const Vertices& second,const Plane& plane,uint64_t cancel) {
    const auto rings=stages(first,second,plane,cancel); std::vector<Quads> parts;
    for(size_t i=1;i<rings.size();++i) {
        const auto& a=rings[i-1]; const auto& b=rings[i];
        const auto faces=a.rows()==b.rows()?equal_faces(int(a.rows())):centered_faces(coordinates(a,plane),coordinates(b,plane));
        validate(faces,int(a.rows()),int(b.rows())); parts.push_back(strip(a,b,faces));
    }
    Vertices combined(first.rows()+second.rows(),3); combined<<first,second;
    Transition out; out.mode=2; out.boundary=int(first.rows()); out.annulus=int(second.rows());
    out.mesh=weld(parts,1e-7*std::max(diagonal(combined),1e-9),false,cancel); quality(out,cancel); return out;
}
Transition transition(const Vertices& first,const Vertices& second,const Plane& plane,double diagonal,uint64_t cancel) {
    check_cancel(cancel);
    const bool a=skin_ring::centered(first,plane,diagonal),b=skin_ring::centered(second,plane,diagonal);
    if(a!=b) throw std::runtime_error("Topology guide was matched to the wrong symmetry side.");
    const auto boundary=skin_ring::canonical(first),ring=skin_ring::aligned(boundary,second,cancel);
    return a?centered(boundary,ring,plane,cancel):side(boundary,ring,cancel);
}
}
