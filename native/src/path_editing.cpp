#include "path_internal.hpp"

namespace af {
struct ParameterPath {
    std::shared_ptr<Path> path;
    Samples samples;
    double end;
};
static ParameterPath parameter_path(uint64_t handle) {
    auto value=path(handle);
    const double end=value->closed?std::floor(value->parameters.back())+1:value->parameters.back();
    return {value,read_samples(value->samples.data(),int(value->parameters.size())),end};
}
static V3 parameter_point(const ParameterPath& value,double parameter) {
    const auto& p=value.path->parameters; const auto& samples=value.samples;
    const auto next=std::upper_bound(p.begin(),p.end(),parameter);
    if(next==p.begin()) return samples.front().position;
    const size_t first=size_t(next-p.begin()-1),last=(first+1)%samples.size();
    if(first+1==p.size()&&!value.path->closed) return samples.back().position;
    const double end=last?p[last]:value.end;
    const double t=std::clamp((parameter-p[first])/std::max(end-p[first],1e-30),0.0,1.0);
    return samples[first].position*(1-t)+samples[last].position*t;
}
static double nearest_parameter(const ParameterPath& value,const V3& point,double low,double high,uint64_t cancel) {
    double best=std::numeric_limits<double>::infinity(),chosen=(low+high)*0.5;
    const auto& p=value.path->parameters;
    for(size_t i=0;i<p.size()-(value.path->closed?0:1);++i) {
        check_cancel(cancel); const double start=std::max(low,p[i]);
        const double end=std::min(high,i+1<p.size()?p[i+1]:value.end);
        if(end<start) continue;
        const V3 a=parameter_point(value,start),b=parameter_point(value,end),delta=b-a;
        const double t=std::clamp((point-a).dot(delta)/std::max(delta.squaredNorm(),1e-30),0.0,1.0);
        const double distance=(point-a-t*delta).squaredNorm();
        if(distance<best) { best=distance; chosen=start+t*(end-start); }
    }
    return chosen;
}
static std::vector<double> correspondence(const ParameterPath& opening,const double* records,
    const int* indices,int count,bool closed,uint64_t cancel) {
    if(count<(closed?3:2)||!records||!indices) throw std::runtime_error("Invalid edit correspondence.");
    std::vector<double> result(indices,indices+count); result.push_back(opening.end);
    const double last=opening.end-(opening.path->closed?1:0);
    if(result.front()!=0||(!closed&&result[count-1]!=last)) throw std::runtime_error("Preserve curve endpoint correspondence.");
    for(int i=1;i<count;++i) {
        if(result[i]>=0) continue;
        int next=i+1; while(result[next]<0) ++next;
        result[i]=nearest_parameter(opening,V3(records+13*i),result[i-1],result[next],cancel);
    }
    if(!std::is_sorted(result.begin(),result.end())||result.back()>opening.end)
        throw std::runtime_error("Authored point ordering must preserve correspondence.");
    return result;
}
static double remap_parameter(const std::vector<double>& mapping,double parameter) {
    const size_t index=std::min(size_t(std::max(0.0,std::floor(parameter))),mapping.size()-2);
    const double t=std::clamp(parameter-double(index),0.0,1.0);
    return mapping[index]*(1-t)+mapping[index+1]*t;
}
static void rebase_samples(EvaluatedPath& output,const ParameterPath& current,const ParameterPath& opening,
                           const std::vector<double>& mapping,uint64_t cancel) {
    for(size_t i=0;i<output.samples.size();++i) {
        check_cancel(cancel); const double parameter=remap_parameter(mapping,output.parameters[i]);
        output.samples[i].position+=parameter_point(current,parameter)-parameter_point(opening,parameter);
    }
}
static void rebase_controls(double* records,int count,const ParameterPath& current,const ParameterPath& opening,
                            const std::vector<double>& mapping) {
    for(int i=0;i<count;++i) {
        const V3 delta=parameter_point(current,mapping[i])-parameter_point(opening,mapping[i]);
        for(int slot=0;slot<3;++slot) {
            Eigen::Map<V3> point(records+13*i+3*slot); point+=delta;
        }
        records[13*i+11]=int(records[13*i+11])%4; records[13*i+12]=int(records[13*i+12])%4;
    }
}
static void edited_tangents(Samples& samples,bool closed,uint64_t cancel) {
    for(size_t i=0;i<samples.size();++i) {
        check_cancel(cancel);
        const size_t a=i?i-1:(closed?samples.size()-1:0),b=i+1<samples.size()?i+1:(closed?0:i);
        const V3 delta=samples[b].position-samples[a].position;
        if(delta.norm()>1e-20) samples[i].tangent=delta.normalized();
    }
    curve_frames(samples,closed,cancel,true);
}
static bool deform_samples(EvaluatedPath& output,const ParameterPath& opening,
                           const ParameterPath& draft,uint64_t cancel) {
    V3 first=V3::Zero(); bool varied=false;
    for(size_t i=0;i<output.samples.size();++i) {
        check_cancel(cancel); const double parameter=output.parameters[i];
        const V3 delta=parameter_point(draft,parameter)-parameter_point(opening,parameter);
        if(i==0) first=delta;
        varied=varied||(delta-first).squaredNorm()>1e-28;
        output.samples[i].position+=delta;
    }
    return varied;
}
}
uint64_t af_path_rebase(uint64_t current_handle,uint64_t opening_handle,uint64_t draft_handle,
    const double* records,const int* indices,int count,double* controls,uint64_t cancel) {
    try {
        const auto current=af::parameter_path(current_handle),opening=af::parameter_path(opening_handle);
        const auto draft=af::parameter_path(draft_handle);
        const auto mapping=af::correspondence(opening,records,indices,count,draft.path->closed,cancel);
        af::EvaluatedPath output{draft.samples,draft.path->parameters};
        af::rebase_samples(output,current,opening,mapping,cancel);
        std::copy_n(records,count*13,controls); af::rebase_controls(controls,count,current,opening,mapping);
        af::edited_tangents(output.samples,draft.path->closed,cancel);
        return af::retain_path(af::make_path(output,draft.path->closed,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_path_control_deform(uint64_t current_handle,uint64_t opening_handle,
                               uint64_t draft_handle,uint64_t cancel) {
    try {
        const auto current=af::parameter_path(current_handle),opening=af::parameter_path(opening_handle);
        const auto draft=af::parameter_path(draft_handle);
        if(opening.end!=draft.end||opening.path->closed!=draft.path->closed)
            throw std::runtime_error("Control deformation must preserve path topology.");
        af::EvaluatedPath output{current.samples,current.path->parameters};
        if(af::deform_samples(output,opening,draft,cancel))
            af::edited_tangents(output.samples,current.path->closed,cancel);
        return af::retain_path(af::make_path(output,current.path->closed,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
