#pragma once
// Standalone policy extension: farthest distinct support along geometric base normals.
namespace af_stack_vector {
static af::Vertices support_vertices(const std::vector<Vec>& points) {
    af::Vertices result(points.size(),3);
    for(size_t i=0;i<points.size();++i) result.row(i)=eigen(points[i]);
    return result;
}
static af::Triangles support_faces(const Side& side) {
    af::Triangles result(side.faces.size()/3,3);
    for(int i=0;i<result.rows();++i) for(int j=0;j<3;++j) result(i,j)=int(side.faces[size_t(i)*3+j]);
    return result;
}
static void normal_ambiguities(const Side& under,const Side& cover,std::vector<Match>& matches,std::atomic<bool>& cancel) {
    const auto hits=af::stacking::ambiguous_support(support_vertices(cover.base),support_faces(cover),
        support_vertices(under.own),support_faces(under),cancel);
    for(size_t i=0;i<hits.size();++i) if(hits[i].face>=0) {
        const auto& hit=hits[i]; auto& match=matches[i];
        match.face=hit.face; match.weights=hit.weights; match.normal=hit.normal; match.provider=hit.point;
        match.bonus=hit.point-eigen(cover.base[i]); match.distance=-hit.distance;
        match.hits=std::max(match.hits,2); match.residual=0;
    }
}
}
