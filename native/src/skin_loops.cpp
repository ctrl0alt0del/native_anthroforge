#include "skin_loops.hpp"
#include "anthroforge/skin_loops.h"
namespace af::skin_loops {
static Loop evaluate(Context& context,const Path& path,const M4& frame) {
    const auto raw=authored(path,frame,context.cancel);
    auto loop=projected(context,raw); const auto closed=closure(context,loop.points);
    loop=projected(context,closed);
    if(loop.perimeter<1e-12) return loop;
    loop=projected(context,resampled(loop,sample_count,context.cancel).points);
    loop.symmetric=symmetric(raw,context.plane,context.diagonal,context.cancel);
    loop.index=point_index(loop.points,context.cancel); return loop;
}
static bool duplicate(const Prepared& result,const Loop& loop,Context& context) {
    for(const auto& previous:result.loops) {
        check_cancel(context.cancel);
        const double distance=std::max(directed_distance(loop,previous,context.cancel),directed_distance(previous,loop,context.cancel));
        if(distance<context.diagonal/160) return true;
    }
    return false;
}
Prepared prepare(Context& context,int count,const uint64_t* paths,const double* frames) {
    Prepared result; result.statuses.assign(count,0);
    for(int i=0;i<count;++i) {
        check_cancel(context.cancel); const auto source=path(paths[i]);
        auto loop=evaluate(context,*source,Eigen::Map<const M4>(frames+16LL*i));
        if(loop.perimeter<1e-12) { result.statuses[i]=3; continue; }
        if(duplicate(result,loop,context)) { result.statuses[i]=2; continue; }
        loop.source=i; result.loops.push_back(std::move(loop));
    }
    pair(result,context.cancel); return result;
}
static void validate(const AFSkinLoopInput& input,const AFSkinLoopOutput& output) {
    if(input.count<0||input.count>2048||!output.sizes)
        throw std::runtime_error("Skin loop count exceeds the capture limit (2048).");
    if(input.count&&(!input.paths||!input.frames||!output.samples||!output.sources||!output.pairs||!output.statuses||!output.symmetric))
        throw std::runtime_error("Missing skin loop input or output buffers.");
}
static void write(const Prepared& result,AFSkinLoopOutput& output,uint64_t cancel) {
    for(size_t i=0;i<result.loops.size();++i) {
        check_cancel(cancel); const auto& loop=result.loops[i]; output.sources[i]=loop.source; output.symmetric[i]=loop.symmetric;
        for(int j=0;j<sample_count;++j) for(int axis=0;axis<3;++axis) {
            output.samples[(i*sample_count+j)*6+axis]=loop.points(j,axis);
            output.samples[(i*sample_count+j)*6+3+axis]=loop.normals(j,axis);
        }
    }
    for(size_t i=0;i<result.pairs.size();++i) {
        output.pairs[2*i]=result.pairs[i].first; output.pairs[2*i+1]=result.pairs[i].second;
    }
    std::copy(result.statuses.begin(),result.statuses.end(),output.statuses);
    output.sizes[0]=int(result.loops.size()); output.sizes[1]=int(result.pairs.size());
}
}
int af_skin_loops(uint64_t handle,const AFSkinLoopInput* input,AFSkinLoopOutput* output,uint64_t cancel) {
    try {
        if(!input||!output) throw std::runtime_error("Missing skin loop buffers.");
        af::skin_loops::validate(*input,*output); af::check_cancel(cancel);
        output->sizes[0]=output->sizes[1]=0; if(!input->count) return 0;
        const auto mesh=af::mesh(handle); af::skin_loops::Context context(*mesh,input->plane,cancel);
        const auto result=af::skin_loops::prepare(context,input->count,input->paths,input->frames);
        af::skin_loops::write(result,*output,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
