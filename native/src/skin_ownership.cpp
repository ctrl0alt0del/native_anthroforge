#include "skin_ownership.hpp"
#include <numeric>
namespace af::skin_ownership {
using Indices=std::map<int,std::unique_ptr<PointIndex>>;
static Indices bone_indices(const Samples& samples,const AFSkinOwnershipInput& in,uint64_t cancel) {
    Indices result;
    for(int i=0;i<in.source_count;++i) if(in.bone_ids[i]>=0&&!samples.indices[i].empty())
        result.emplace(i,std::make_unique<PointIndex>(samples.points,samples.indices[i],cancel));
    return result;
}
static std::vector<int> bone_points(const Samples& samples,const AFSkinOwnershipInput& in) {
    std::vector<int> result;
    for(int i=0;i<in.source_count;++i) if(in.bone_ids[i]>=0)
        result.insert(result.end(),samples.indices[i].begin(),samples.indices[i].end());
    return result;
}
static int resolve(const V3& p,int source,const Samples& samples,const AFSkinOwnershipInput& in,const Indices& bones) {
    int owner=-1; double best=std::numeric_limits<double>::infinity();
    if(source<0) return owner;
    for(int j=in.candidate_offsets[source];j<in.candidate_offsets[source+1];++j) {
        const int candidate=in.candidates[j]; const auto found=bones.find(candidate);
        if(found==bones.end()) continue;
        const auto hit=found->second->nearest(samples.points,p); const int id=in.bone_ids[candidate];
        if(hit.second<best||(hit.second==best&&(owner<0||id<owner))) { best=hit.second; owner=id; }
    }
    return owner;
}
static void assign_points(const Mesh& mesh,const Samples& data,const AFSkinOwnershipInput& in,
                         const PointIndex& all,const PointIndex& fallback,int* owners,int* sources,int* count,uint64_t cancel) {
    const auto bones=bone_indices(data,in,cancel); *count=0;
    for(int i=0;i<mesh.vertices.rows();++i) {
        if(i%1024==0) check_cancel(cancel);
        const V3 p=mesh.vertices.row(i); const auto nearest=all.nearest(data.points,p);
        sources[i]=nearest.first<0?-1:data.sources[nearest.first];
        owners[i]=resolve(p,sources[i],data,in,bones);
        if(owners[i]>=0) continue;
        ++*count; const auto hit=fallback.nearest(data.points,p);
        if(hit.first>=0) owners[i]=in.bone_ids[data.sources[hit.first]];
    }
}
void assign(const Mesh& mesh,const AFSkinOwnershipInput& in,int* owners,int* sources,int* fallback,uint64_t cancel) {
    const auto data=samples(in,cancel); std::vector<int> indices(data.points.rows());
    std::iota(indices.begin(),indices.end(),0);
    const PointIndex all(data.points,indices,cancel),bones(data.points,bone_points(data,in),cancel);
    assign_points(mesh,data,in,all,bones,owners,sources,fallback,cancel);
}
}
