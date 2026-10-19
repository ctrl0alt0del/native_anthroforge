#include "path_internal.hpp"
#include "component_index.hpp"
#include <mutex>
#include <unordered_map>

namespace af {
static std::mutex path_mutex;
static std::unordered_map<uint64_t,std::shared_ptr<Path>> paths;
static uint64_t next_path=1;
static uint64_t path_bytes(const Path& path) {
    return sizeof(Path)+(path.samples.capacity()+path.parameters.capacity())*sizeof(double)
        +path.render.capacity()*sizeof(float)+(path.index?component_bytes(*path.index):0);
}
std::shared_ptr<Path> path(uint64_t handle) {
    std::lock_guard<std::mutex> lock(path_mutex);
    const auto found=paths.find(handle);
    if(found==paths.end()) throw std::runtime_error("Unknown path handle.");
    return found->second;
}
uint64_t retain_path(std::shared_ptr<Path> value) {
    std::lock_guard<std::mutex> lock(path_mutex);
    const auto handle=next_path++;
    paths.emplace(handle,std::move(value));
    return handle;
}
static void append_sample(Path& path,const CurveSample& sample) {
    const auto& p=sample.position; const auto& t=sample.tangent; const auto& n=sample.normal;
    path.samples.insert(path.samples.end(),{p.x(),p.y(),p.z(),t.x(),t.y(),t.z(),n.x(),n.y(),n.z(),sample.radius,sample.tilt});
    for(int axis=0;axis<3;++axis) {
        path.bounds[axis]=std::min(path.bounds[axis],p[axis]);
        path.bounds[axis+3]=std::max(path.bounds[axis+3],p[axis]);
    }
}
static void validate_path(const Path& path) {
    const V3 extent=V3(path.bounds.data()+3)-V3(path.bounds.data());
    if(extent.norm()<1e-20) throw std::runtime_error("Path has zero length.");
    for(const double parameter:path.parameters)
        if(!std::isfinite(parameter)) throw std::runtime_error("Path parameter is not finite.");
}
std::shared_ptr<Path> make_path(const EvaluatedPath& evaluated,bool closed,uint64_t cancel) {
    if(evaluated.samples.size()<size_t(closed?3:2)) throw std::runtime_error("Path has too few samples.");
    auto result=std::make_shared<Path>(); result->closed=closed;
    result->parameters=evaluated.parameters; result->samples.reserve(evaluated.samples.size()*11);
    for(int axis=0;axis<3;++axis) result->bounds[axis]=result->bounds[axis+3]=evaluated.samples[0].position[axis];
    for(const auto& sample:evaluated.samples) {
        check_cancel(cancel);
        if(!sample.position.allFinite()||!sample.tangent.allFinite()||!sample.normal.allFinite()
            ||!std::isfinite(sample.radius)||!std::isfinite(sample.tilt))
            throw std::runtime_error("Path has non-finite or degenerate geometry.");
        append_sample(*result,sample);
    }
    validate_path(*result); prepare_path(*result,cancel); return result;
}
}
uint64_t af_path_evaluate(const double* records,int count,int engine,int closed,int resolution,uint64_t cancel) {
    try {
        af::check_cancel(cancel);
        return af::retain_path(af::make_path(af::authored_path(records,count,engine,closed!=0,resolution,cancel),closed!=0,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_path_restore(const double* samples,const double* parameters,int count,int closed) {
    try {
        if(!samples||!parameters||count<(closed?3:2)) throw std::runtime_error("Invalid path buffers.");
        af::EvaluatedPath evaluated{af::read_samples(samples,count),std::vector<double>(parameters,parameters+count)};
        return af::retain_path(af::make_path(evaluated,closed!=0,0));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_path_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::path_mutex); af::paths.erase(handle);
}
int af_path_info(uint64_t handle,int64_t* counts,double* bounds) {
    try {
        if(!counts||!bounds) throw std::runtime_error("Path info requires output buffers.");
        const auto value=af::path(handle);
        counts[0]=int64_t(value->parameters.size()); counts[1]=value->closed;
        counts[2]=int64_t(af::path_bytes(*value));
        std::copy(value->bounds.begin(),value->bounds.end(),bounds); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
const double* af_path_buffer(uint64_t handle,int kind) {
    try {
        if(kind<0||kind>1) throw std::runtime_error("Unknown path buffer.");
        const auto value=af::path(handle);
        return kind?value->parameters.data():value->samples.data();
    } catch(const std::exception& error) { af::set_error(error.what()); return nullptr; }
}
int af_path_memory_snapshot(uint64_t* rows,int capacity,uint64_t* total) {
    if(!total||capacity<0||(!rows&&capacity)) return -1;
    std::lock_guard<std::mutex> lock(af::path_mutex);
    *total=af::paths.size(); int count=0;
    for(const auto& item:af::paths) {
        if(count==capacity) break;
        auto* row=rows+count*3;
        row[0]=item.first; row[1]=reinterpret_cast<uint64_t>(item.second.get());
        row[2]=af::path_bytes(*item.second); ++count;
    }
    return count;
}
