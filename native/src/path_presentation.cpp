#include "path_internal.hpp"
#include "component_index.hpp"

namespace af {
void prepare_path(Path& path,uint64_t cancel) {
    const int count=int(path.parameters.size()),vertices=count+(path.closed?1:0);
    path.render.reserve(size_t(vertices)*3);
    for(int i=0;i<vertices;++i) {
        check_cancel(cancel);
        const auto* p=path.samples.data()+11*(i%count);
        for(int axis=0;axis<3;++axis) {
            if(std::abs(p[axis])>std::numeric_limits<float>::max()) throw std::runtime_error("Path exceeds render range.");
            path.render.push_back(float(p[axis]));
        }
    }
    path.index=path_index(path.samples.data(),count,path.closed,cancel);
}
static int pick_path(uint64_t handle,const double* matrix,const ComponentRay& ray,double* output) {
    const auto value=path(handle);
    const auto hit=component_nearest(*value->index,Eigen::Map<const M4>(matrix),ray);
    if(hit.second<0) return 0;
    output[0]=hit.first; output[1]=hit.second;
    const V3 position=ray.origin+ray.direction.normalized()*hit.first;
    for(int axis=0;axis<3;++axis) output[2+axis]=position[axis];
    return 1;
}
}
int af_path_chunk(uint64_t handle,int chunk,const float** data,int* count) {
    try {
        const auto value=af::path(handle); const size_t start=size_t(chunk)*af::path_chunk_segments*3;
        if(chunk<0||!data||!count||start+3>=value->render.size()) throw std::runtime_error("Invalid path render chunk.");
        *data=value->render.data()+start;
        *count=int(std::min(value->render.size()-start,size_t(af::path_chunk_segments+1)*3)); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_path_chunk_count(uint64_t handle) {
    try {
        const auto value=af::path(handle);
        const size_t segments=value->render.size()/3-1;
        return int((segments+af::path_chunk_segments-1)/af::path_chunk_segments);
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
int af_paths_pick(int count,const uint64_t* paths,const double* matrices,
    const double* origin,const double* direction,double radius,double* output) {
    try {
        if(count<0||!origin||!direction||(count&&(!paths||!matrices||!output))) throw std::runtime_error("Invalid path batch.");
        const af::ComponentRay ray{af::V3(origin),af::V3(direction),radius}; int found=0;
        for(int i=0;i<count;++i) {
            if(af::pick_path(paths[i],matrices+16*i,ray,output+6*found+1)) { output[6*found]=i; ++found; }
        }
        return found;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
