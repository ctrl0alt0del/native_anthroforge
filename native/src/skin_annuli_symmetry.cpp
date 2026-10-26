#include "skin_annuli.hpp"
#include "scipy_lsap/rectangular_lsap.h"
#include <tuple>
namespace af::skin_annuli {
static V3 reflected(const V3& point,const Plane& plane) {
    return point-2*plane.normal.dot(point-plane.origin)*plane.normal;
}
static bool crosses(const Loop& loop,const Plane& plane) {
    const Eigen::VectorXd distances=(loop.points.rowwise()-plane.origin.transpose())*plane.normal;
    return distances.minCoeff()<0&&distances.maxCoeff()>0;
}
bool symmetry_candidate(const Loop& outer,const Loop& inner,const Plane& plane) {
    return plane.enabled&&outer.symmetric&&inner.symmetric&&crosses(outer,plane)&&crosses(inner,plane);
}
static void match_ring(Vertices& points,const std::vector<int>& positive,const std::vector<int>& negative,const Plane& plane) {
    const size_t count=positive.size(); std::vector<double> costs(count*count); std::vector<int64_t> a(count),b(count);
    for(size_t i=0;i<count;++i) for(size_t j=0;j<count;++j)
        costs[i*count+j]=(reflected(points.row(positive[i]),plane)-V3(points.row(negative[j]))).norm();
    if(solve_rectangular_linear_sum_assignment(count,count,costs.data(),false,a.data(),b.data()))
        throw std::runtime_error("Skin annulus symmetry assignment failed.");
    for(size_t i=0;i<count;++i) {
        const int first=positive[a[i]],second=negative[b[i]];
        const V3 average=(V3(points.row(first))+reflected(points.row(second),plane))/2;
        points.row(first)=average; points.row(second)=reflected(average,plane);
    }
}
static Vertices symmetric_ring(Vertices points,const Plane& plane,double tolerance) {
    std::vector<int> positive,negative,center;
    for(int i=0;i<points.rows();++i) {
        const double distance=plane.normal.dot(V3(points.row(i))-plane.origin);
        (std::abs(distance)<=tolerance?center:(distance>0?positive:negative)).push_back(i);
    }
    if(positive.size()!=negative.size()) return points;
    match_ring(points,positive,negative,plane);
    for(const int i:center) points.row(i)-=plane.normal.dot(V3(points.row(i))-plane.origin)*plane.normal.transpose();
    return points;
}
void symmetrize(Context& context,Patch& patch) {
    for(int row=0;row<rows;++row) {
        check_cancel(context.cancel);
        const auto ring=symmetric_ring(patch.points.middleRows(row*patch.segments,patch.segments),context.plane,context.diagonal/10000);
        patch.points.middleRows(row*patch.segments,patch.segments)=ring;
        patch.normals.middleRows(row*patch.segments,patch.segments)=skin_loops::projected(context,ring).normals;
    }
}
static double pair_error(const Patch& first,const Patch& second,const skin::PointIndex& index,const Plane& plane) {
    std::vector<double> distances; distances.reserve(first.points.rows());
    for(int i=0;i<first.points.rows();++i) distances.push_back(std::sqrt(index.nearest(second.points,reflected(first.points.row(i),plane)).second));
    std::sort(distances.begin(),distances.end()); const double at=.95*(distances.size()-1);
    const size_t low=size_t(at),high=std::min(low+1,distances.size()-1);
    return distances[low]+(at-low)*(distances[high]-distances[low]);
}
static void mirror(Patch& target,const Patch& source,const Plane& plane,int source_index) {
    target.points=source.points; target.normals=source.normals; target.faces=source.faces;
    target.segments=source.segments; target.inversions=source.inversions; target.mirror=source_index;
    for(int i=0;i<source.points.rows();++i) {
        target.points.row(i)=reflected(source.points.row(i),plane);
        const V3 normal=source.normals.row(i); target.normals.row(i)=normal-2*normal.dot(plane.normal)*plane.normal;
    }
    for(auto& face:target.faces) std::reverse(face.begin(),face.end());
}
static std::vector<std::tuple<double,int,int>> mirror_candidates(Context& context,const Patches& patches) {
    std::vector<std::shared_ptr<skin::PointIndex>> indices;
    for(const auto& patch:patches) indices.push_back(skin_loops::point_index(patch.points,context.cancel));
    std::vector<std::tuple<double,int,int>> candidates;
    for(int i=0;i<int(patches.size());++i) for(int j=i+1;j<int(patches.size());++j) {
        check_cancel(context.cancel); const double error=pair_error(patches[i],patches[j],*indices[j],context.plane);
        if(error<context.diagonal/40) candidates.emplace_back(error,i,j);
    }
    std::sort(candidates.begin(),candidates.end()); return candidates;
}
void mirror_pairs(Context& context,Patches& patches) {
    if(!context.plane.enabled) return;
    const auto candidates=mirror_candidates(context,patches); std::vector<bool> used(patches.size(),false);
    for(const auto& [error,first,second]:candidates) {
        check_cancel(context.cancel); if(used[first]||used[second]) continue;
        int source=first,target=second;
        const V3 delta=patches[source].points.colwise().mean()-patches[target].points.colwise().mean();
        if(delta.dot(context.plane.normal)<0) std::swap(source,target);
        mirror(patches[target],patches[source],context.plane,source); used[first]=used[second]=true;
    }
}
}
