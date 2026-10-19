// Port of core/vcp/fiber_node_attachment_weights.py; native/migration/README.md.
#include "mesh_internal.hpp"
#include "anthroforge/attachments.h"
#include <set>

namespace af {
struct OwnerControl { double position; int owner; };
struct OwnerRun { int owner,first,last; };
struct AttachmentArc {
    std::vector<int> indices;
    std::vector<double> distances;
    std::vector<OwnerRun> runs;
};
static void owner_control(std::vector<OwnerControl>& controls,double position,int owner) {
    if(position>controls.back().position) controls.push_back({position,owner});
}
static AttachmentArc attachment_arc(const double* points,const int* owners,int count,int start,int end,uint64_t cancel) {
    AttachmentArc arc;
    for(int step=start;step<=end;++step) {
        check_cancel(cancel); const int index=step%count,local=step-start;
        const V3 current(points+index*3),previous(points+(step==start?index:(step-1)%count)*3);
        arc.indices.push_back(index);
        arc.distances.push_back(local?arc.distances.back()+(current-previous).norm():0.0);
        if(arc.runs.empty()||arc.runs.back().owner!=owners[index]) arc.runs.push_back({owners[index],local,local});
        else arc.runs.back().last=local;
    }
    return arc;
}
static void transition_controls(const AttachmentArc& arc,const OwnerRun& left,const OwnerRun& right,
                                std::vector<OwnerControl>& controls) {
    const auto& d=arc.distances;
    const double gap=d[right.first]-d[left.last],center=(d[left.last]+d[right.first])*0.5;
    const double extent=0.5*std::min(std::max(d[left.last]-d[left.first],gap),std::max(d[right.last]-d[right.first],gap));
    owner_control(controls,std::max(d[left.first],center-extent),left.owner);
    owner_control(controls,std::min(d[right.last],center+extent),right.owner);
}
static std::vector<OwnerControl> arc_controls(const AttachmentArc& arc) {
    std::vector<OwnerControl> controls{{0.0,arc.runs.front().owner}};
    for(size_t run=1;run<arc.runs.size();++run) transition_controls(arc,arc.runs[run-1],arc.runs[run],controls);
    owner_control(controls,arc.distances.back(),arc.runs.back().owner);
    if(controls.size()==1) controls.push_back(controls.front());
    return controls;
}
static void single_owner(int owner,int* targets,double* weights) {
    targets[0]=owner; targets[1]=-1; weights[0]=1; weights[1]=0;
}
static void blend_owner(double position,const OwnerControl& first,const OwnerControl& last,int* targets,double* weights) {
    if(first.owner==last.owner) { single_owner(first.owner,targets,weights); return; }
    const double t=std::clamp((position-first.position)/std::max(last.position-first.position,1e-30),0.0,1.0);
    const double weight=t*t*t*(10.0+t*(-15.0+6.0*t));
    if(weight<=1e-12) { single_owner(first.owner,targets,weights); return; }
    if(weight>=1.0-1e-12) { single_owner(last.owner,targets,weights); return; }
    targets[0]=first.owner; targets[1]=last.owner; weights[0]=1-weight; weights[1]=weight;
}
static void apply_arc(const AttachmentArc& arc,int* targets,double* weights,uint64_t cancel) {
    const auto controls=arc_controls(arc); size_t cursor=0;
    for(size_t i=1;i+1<arc.indices.size();++i) {
        check_cancel(cancel);
        while(cursor+2<controls.size()&&arc.distances[i]>=controls[cursor+1].position) ++cursor;
        blend_owner(arc.distances[i],controls[cursor],controls[cursor+1],targets+2*arc.indices[i],weights+2*arc.indices[i]);
    }
}
static std::vector<int> attachment_pins(const int* pins,int pin_count,int count,bool closed) {
    if(count<2||count>1000000||pin_count<1||pin_count>count||!pins) throw std::runtime_error("Invalid attachment reference.");
    const std::set<int> unique(pins,pins+pin_count);
    std::vector<int> result(unique.begin(),unique.end());
    if(result.front()<0||result.back()>=count) throw std::runtime_error("Invalid hard pin index.");
    if(!closed&&(result.front()!=0||result.back()!=count-1)) throw std::runtime_error("Open endpoints must be pinned.");
    return result;
}
static void initialize_owners(const double* points,const int* owners,int count,int* targets,double* weights) {
    if(!points||!owners||!targets||!weights) throw std::runtime_error("Attachment blending needs owned buffers.");
    for(int i=0;i<count;++i) {
        if(owners[i]<0||!V3(points+3*i).allFinite()) throw std::runtime_error("Invalid attachment owner or coordinates.");
        single_owner(owners[i],targets+2*i,weights+2*i);
    }
}
}
int af_attachment_weights(const double* points,const int* owners,int count,const int* pins,int pin_count,
                          int closed,int* targets,double* weights,uint64_t cancel) {
    try {
        const auto fixed=af::attachment_pins(pins,pin_count,count,closed!=0);
        af::initialize_owners(points,owners,count,targets,weights);
        for(size_t i=0;i<fixed.size()-(closed?0:1);++i) {
            const int end=i+1<fixed.size()?fixed[i+1]:fixed.front()+count;
            af::apply_arc(af::attachment_arc(points,owners,count,fixed[i],end,cancel),targets,weights,cancel);
        }
        af::check_cancel(cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_attachment_compact(int count,const int* owners,int surfaces,int* output,int* used) {
    try {
        if(count<1||surfaces<1||!owners||!output||!used) throw std::runtime_error("Invalid attachment owner buffers.");
        std::vector<int> mapping(surfaces,-1); int size=0;
        for(int i=0;i<count;++i) {
            if(owners[i]<-1||owners[i]>=surfaces) throw std::runtime_error("Attachment owner is outside the candidate set.");
            if(owners[i]>=0) mapping[owners[i]]=0;
        }
        for(int i=0;i<surfaces;++i) if(mapping[i]==0) { mapping[i]=size; used[size++]=i; }
        for(int i=0;i<count;++i) output[i]=owners[i]<0?-1:mapping[owners[i]];
        return size;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
