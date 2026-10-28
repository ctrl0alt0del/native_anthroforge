#include "skin_loops.hpp"
#include "skin_ring.hpp"
namespace af::skin_loops {
double directed_distance(const Loop& first,const Loop& second,uint64_t cancel) {
    double largest=0;
    for(int i=0;i<first.points.rows();++i) {
        if(i%256==0) check_cancel(cancel);
        largest=std::max(largest,second.index->nearest(second.points,first.points.row(i)).second);
    }
    return std::sqrt(largest);
}
bool symmetric(const Vertices& points,const Plane& plane,double diagonal,uint64_t cancel) {
    if(!plane.enabled) return false;
    const auto index=point_index(points,cancel); std::vector<double> errors;
    for(int i=0;i<points.rows();++i) {
        if(i%256==0) check_cancel(cancel);
        const V3 p=points.row(i),reflected=p-2*(p-plane.origin).dot(plane.normal)*plane.normal;
        errors.push_back(std::sqrt(index->nearest(points,reflected).second));
    }
    std::sort(errors.begin(),errors.end()); const double k=.95*(errors.size()-1);
    const double value=errors[size_t(k)]*(1-k+std::floor(k))+errors[size_t(std::ceil(k))]*(k-std::floor(k));
    return value<diagonal/40;
}
static bool nested(const Loop& first,const Loop& second) {
    const auto& outer=first.perimeter>=second.perimeter?first:second;
    const auto& inner=first.perimeter>=second.perimeter?second:first;
    const double ratio=inner.perimeter/std::max(outer.perimeter,1e-9);
    if(ratio<.2||ratio>.95) return false;
    const auto projection=skin_ring::project(outer.points);
    const double depth=std::abs(projection.normal.dot(inner.center-outer.center));
    return depth<=.25*projection.radius&&skin_ring::inside(projection,inner.center);
}
static int partner(const std::vector<Loop>& loops,int first,const std::vector<bool>& used) {
    int best=-1; double score=std::numeric_limits<double>::infinity();
    for(size_t i=first+1;i<loops.size();++i) {
        if(used[i]||!nested(loops[first],loops[i])) continue;
        const double candidate=(loops[first].center-loops[i].center).norm()/std::max(std::min(loops[first].perimeter,loops[i].perimeter),1e-6);
        if(candidate<score) { best=int(i); score=candidate; }
    }
    return best;
}
void pair(Prepared& result,uint64_t cancel) {
    std::vector<bool> used(result.loops.size());
    for(size_t i=0;i<result.loops.size();++i) {
        check_cancel(cancel); if(used[i]) continue;
        const int other=partner(result.loops,int(i),used); used[i]=true;
        if(other<0) { result.statuses[result.loops[i].source]=1; continue; }
        used[other]=true; const bool outer=result.loops[i].perimeter>=result.loops[other].perimeter;
        result.pairs.push_back(outer?std::make_pair(int(i),other):std::make_pair(other,int(i)));
    }
}
}
