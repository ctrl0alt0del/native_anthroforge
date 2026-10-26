#include "skin_ownership.hpp"
namespace af::skin_ownership {
static void validate(const AFSkinOwnershipInput& in) {
    const int64_t total=int64_t(in.vertex_count)+in.triangle_count+in.segment_count;
    if(in.source_count<0||in.source_count>1000000||in.vertex_count<0||in.triangle_count<0||in.segment_count<0
       ||in.candidate_count<0||in.candidate_count>16777216||total>16777216)
        throw std::runtime_error("Invalid skin ownership sizes.");
    if(!in.vertex_offsets||!in.candidate_offsets||(in.source_count&&!in.bone_ids)||(in.vertex_count&&!in.vertices)
       ||(in.triangle_count&&(!in.triangles||!in.triangle_sources))||(in.segment_count&&(!in.segments||!in.segment_sources))
       ||(in.candidate_count&&!in.candidates)) throw std::runtime_error("Missing skin ownership buffers.");
    if(in.vertex_offsets[0]!=0||in.vertex_offsets[in.source_count]!=in.vertex_count||in.candidate_offsets[0]!=0
       ||in.candidate_offsets[in.source_count]!=in.candidate_count) throw std::runtime_error("Invalid skin ownership offsets.");
}
static void candidate_range(const AFSkinOwnershipInput& in,int source) {
    const int start=in.candidate_offsets[source],end=in.candidate_offsets[source+1];
    if(start<0||end<start||end>in.candidate_count||in.bone_ids[source]<-1)
        throw std::runtime_error("Invalid skin ownership candidates.");
    for(int i=start;i<end;++i) {
        const int id=in.candidates[i];
        if(id<0||id>=in.source_count||in.bone_ids[id]<0) throw std::runtime_error("Ownership candidate must be an SCP instance.");
    }
}
static void append(Samples& result,int source,int index,const V3& point) {
    if(!point.allFinite()) throw std::runtime_error("Nonfinite skin ownership sample.");
    result.points.row(index)=point; result.sources[index]=source; result.indices[source].push_back(index);
}
static void vertices(Samples& result,const AFSkinOwnershipInput& in,uint64_t cancel) {
    for(int source=0;source<in.source_count;++source) {
        check_cancel(cancel); candidate_range(in,source);
        const int start=in.vertex_offsets[source],end=in.vertex_offsets[source+1];
        if(start<0||end<start||end>in.vertex_count) throw std::runtime_error("Invalid source vertex range.");
        for(int i=start;i<end;++i) {
            if(i%4096==0) check_cancel(cancel);
            append(result,source,i,V3(in.vertices+3LL*i));
        }
    }
}
static V3 centroid(const AFSkinOwnershipInput& in,const int64_t* corners,int count,int source) {
    if(source<0||source>=in.source_count) throw std::runtime_error("Invalid ownership source index.");
    V3 result=V3::Zero();
    for(int j=0;j<count;++j) {
        const int64_t v=corners[j];
        if(v<in.vertex_offsets[source]||v>=in.vertex_offsets[source+1]) throw std::runtime_error("Ownership element crosses source boundaries.");
        result+=V3(in.vertices+3*v);
    }
    return result/double(count);
}
static void elements(Samples& result,const AFSkinOwnershipInput& in,uint64_t cancel) {
    for(int i=0;i<in.triangle_count;++i) {
        if(i%4096==0) check_cancel(cancel);
        append(result,in.triangle_sources[i],in.vertex_count+i,centroid(in,in.triangles+3LL*i,3,in.triangle_sources[i]));
    }
    for(int i=0;i<in.segment_count;++i) {
        if(i%4096==0) check_cancel(cancel);
        append(result,in.segment_sources[i],in.vertex_count+in.triangle_count+i,centroid(in,in.segments+2LL*i,2,in.segment_sources[i]));
    }
}
Samples samples(const AFSkinOwnershipInput& in,uint64_t cancel) {
    validate(in); check_cancel(cancel); Samples result;
    const int count=in.vertex_count+in.triangle_count+in.segment_count;
    result.points.resize(count,3); result.sources.resize(count); result.indices.resize(in.source_count);
    vertices(result,in,cancel); elements(result,in,cancel); return result;
}
}
