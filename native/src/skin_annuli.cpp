// Addon annuli.py construction policy; owned inputs, no Blender dependency.
#include "skin_annuli.hpp"
namespace af::skin_annuli {
int segment_count(const Loop& outer,const Loop& inner,double diagonal) {
    const double target=std::max(diagonal/80,1e-6);
    const double raw=std::ceil(std::max(outer.perimeter,inner.perimeter)/target);
    return int(std::clamp(std::ceil(raw/4)*4,24.0,96.0));
}
static int aligned_index(int i,int count,int shift,bool reverse) {
    const int index=(i-shift+count)%count;
    return reverse?count-1-index:index;
}
static double alignment_score(const Loop& first,const Loop& second,int shift,bool reverse) {
    double score=0;
    for(int i=0;i<first.points.rows();++i)
        score+=(first.points.row(i)-second.points.row(aligned_index(i,int(first.points.rows()),shift,reverse))).squaredNorm();
    return score;
}
Loop aligned(const Loop& reference,const Loop& candidate) {
    Loop result=candidate; double best=std::numeric_limits<double>::infinity();
    for(int reversed=0;reversed<2;++reversed) for(int shift=0;shift<candidate.points.rows();++shift) {
        const double score=alignment_score(reference,candidate,shift,reversed!=0);
        if(score>=best) continue;
        best=score;
        for(int i=0;i<candidate.points.rows();++i) {
            const int j=aligned_index(i,int(candidate.points.rows()),shift,reversed!=0);
            result.points.row(i)=candidate.points.row(j); result.normals.row(i)=candidate.normals.row(j);
        }
    }
    return result;
}
static std::vector<Quad> faces(int count) {
    std::vector<Quad> result;
    for(int r=0;r<rows-1;++r) for(int c=0;c<count;++c) {
        const int next=(c+1)%count;
        result.push_back({r*count+c,r*count+next,(r+1)*count+next,(r+1)*count+c});
    }
    return result;
}
static double orientation(Context& context,const Patch& patch,const Quad& face) {
    const V3 a=patch.points.row(face[0]),b=patch.points.row(face[1]),d=patch.points.row(face[3]);
    Vertices center(1,3); center.row(0)=(a+b+V3(patch.points.row(face[2]))+d)/4;
    const auto projected=skin_loops::projected(context,center);
    return (b-a).cross(d-a).dot(projected.normals.row(0));
}
void finish(Context& context,Patch& patch) {
    patch.faces=faces(patch.segments); std::vector<double> signs; double sum=0;
    for(const auto& face:patch.faces) {
        check_cancel(context.cancel); signs.push_back(orientation(context,patch,face)); sum+=signs.back();
    }
    const bool reverse=sum<0; patch.inversions=0;
    for(size_t i=0;i<signs.size();++i) {
        if((reverse?-signs[i]:signs[i])<=0) ++patch.inversions;
        if(reverse) std::reverse(patch.faces[i].begin(),patch.faces[i].end());
    }
}
Patch direct(Context& context,const Loop& outer,const Loop& inner) {
    Patch result; result.segments=segment_count(outer,inner,context.diagonal);
    const auto a=skin_loops::resampled(outer,result.segments,context.cancel);
    const auto b=aligned(a,skin_loops::resampled(inner,result.segments,context.cancel));
    result.points.resize(rows*result.segments,3); result.normals.resize(rows*result.segments,3);
    for(int r=0;r<rows;++r) {
        const double factor=double(r)/(rows-1);
        const auto ring=skin_loops::projected(context,(1-factor)*a.points+factor*b.points);
        result.points.middleRows(r*result.segments,result.segments)=ring.points;
        result.normals.middleRows(r*result.segments,result.segments)=ring.normals;
    }
    finish(context,result); return result;
}
Patch choose(Context& context,const Loop& outer,const Loop& inner) {
    auto best=direct(context,outer,inner); if(!best.inversions) return best;
    auto candidate=planar(context,outer,inner); if(!candidate.inversions) return candidate;
    if(candidate.inversions<best.inversions) best=std::move(candidate);
    candidate=radial(context,outer);
    if(candidate.inversions<best.inversions) best=std::move(candidate);
    return best;
}
}
