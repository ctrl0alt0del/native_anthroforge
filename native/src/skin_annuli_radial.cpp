#include "skin_annuli.hpp"
namespace af::skin_annuli {
static std::pair<Vertices,Vertices> radial_seeds(Context& context,const Loop& loop,int segments) {
    const auto sampled=skin_loops::resampled(loop,segments,context.cancel); const auto axes=frame(sampled.points,{});
    Eigen::MatrixXd planar(segments,2);
    for(int i=0;i<segments;++i) {
        const V3 delta=V3(sampled.points.row(i))-axes.center;
        planar.row(i)<<delta.dot(axes.first),delta.dot(axes.second);
    }
    planar=smooth(planar,6); Vertices points(segments,3),directions(segments,3);
    for(int i=0;i<segments;++i) {
        const V3 offset=planar(i,0)*axes.first+planar(i,1)*axes.second;
        points.row(i)=axes.center+offset; directions.row(i)=offset/std::max(planar.row(i).norm(),1e-9);
    }
    return {skin_loops::projected(context,points).points,directions};
}
static Patch radial_candidate(Context& context,const std::pair<Vertices,Vertices>& seeds,double width) {
    Patch result; result.mode=2; result.segments=int(seeds.first.rows());
    result.points.resize(rows*result.segments,3); result.normals.resize(rows*result.segments,3);
    for(int row=0;row<rows;++row) {
        const double distance=-width+2*width*row/(rows-1);
        const auto ring=skin_loops::projected(context,seeds.first+distance*seeds.second);
        result.points.middleRows(row*result.segments,result.segments)=ring.points;
        result.normals.middleRows(row*result.segments,result.segments)=ring.normals;
    }
    finish(context,result); return result;
}
Patch radial(Context& context,const Loop& outer) {
    const auto seeds=radial_seeds(context,outer,segment_count(outer,outer,context.diagonal));
    Patch best; best.inversions=std::numeric_limits<int>::max();
    for(const double divisor:{90.0,120.0,160.0,220.0,320.0}) {
        check_cancel(context.cancel); auto candidate=radial_candidate(context,seeds,context.diagonal/divisor);
        if(!candidate.inversions) return candidate;
        if(candidate.inversions<best.inversions) best=std::move(candidate);
    }
    return best;
}
}
