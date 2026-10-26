#include "skin_stitch.hpp"
namespace af::skin_stitch {
static Vertices points(const Transition& transition) {
    Vertices result(transition.mesh.points.size(),3);
    for(size_t i=0;i<transition.mesh.points.size();++i) result.row(i)=transition.mesh.points[i]; return result;
}
static V3 reflected(const V3& point,const Plane& plane) {
    return point-2*(point-plane.origin).dot(plane.normal)*plane.normal;
}
static void mirror(Transition& target,const Transition& source,const Plane& plane,uint64_t cancel) {
    const auto geometry=points(target); const auto index=skin_loops::point_index(geometry,cancel); std::vector<int64_t> map;
    for(const auto& point:source.mesh.points) {
        check_cancel(cancel); const auto hit=index->nearest(geometry,reflected(point,plane));
        if(hit.second>1e-8) throw std::runtime_error("Transition pair is not symmetric across the requested plane.");
        map.push_back(hit.first);
    }
    auto saved=std::move(target.mesh.points); target=source; target.mesh.points=std::move(saved);
    for(auto& face:target.mesh.faces) { for(auto& vertex:face) vertex=map[vertex]; std::reverse(face.begin(),face.end()); }
}
static void partner(std::vector<Transition>& values,const Vertices& centers,int source,std::set<int>& pending,const Plane& plane,double diagonal,uint64_t cancel) {
    if(pending.empty()) return;
    const V3 point=reflected(centers.row(source),plane); int best=-1; double distance=INFINITY;
    for(const int i:pending) {
        const double current=(V3(centers.row(i))-point).norm();
        if(current<distance) { distance=current; best=i; }
    }
    if(distance<.02*diagonal) { mirror(values[best],values[source],plane,cancel); pending.erase(best); }
}
void mirror_transitions(std::vector<Transition>& values,const Plane& plane,double diagonal,uint64_t cancel) {
    if(!plane.enabled) return;
    std::set<int> pending; Vertices centers(values.size(),3);
    for(size_t i=0;i<values.size();++i) {
        centers.row(i)=points(values[i]).colwise().mean();
        if((V3(centers.row(i))-plane.origin).dot(plane.normal)>1e-5*diagonal) pending.insert(int(i));
    }
    for(size_t i=0;i<values.size();++i) if((V3(centers.row(i))-plane.origin).dot(plane.normal)<-1e-5*diagonal)
        partner(values,centers,int(i),pending,plane,diagonal,cancel);
}
}
