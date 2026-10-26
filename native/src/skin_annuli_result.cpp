#include "skin_annuli.hpp"
#include "anthroforge/skin_annuli.h"
#include <mutex>
#include <unordered_map>
namespace af::skin_annuli {
static std::mutex mutex;
static std::unordered_map<uint64_t,std::shared_ptr<const Patches>> registry;
static uint64_t next=1;
uint64_t retain(Patches value) {
    auto owned=std::make_shared<const Patches>(std::move(value));
    std::lock_guard<std::mutex> lock(mutex); const auto id=next++;
    registry.emplace(id,std::move(owned)); return id;
}
std::shared_ptr<const Patches> get(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex); const auto found=registry.find(handle);
    if(found==registry.end()) throw std::runtime_error("Unknown skin annulus resource.");
    return found->second;
}
static std::array<int,3> sizes(const Patches& patches) {
    std::array<int,3> out{0,0,int(patches.size())};
    for(const auto& patch:patches) { out[0]+=int(patch.points.rows()); out[1]+=int(patch.faces.size()); }
    return out;
}
static void copy(const Patch& patch,double* samples,int64_t* quads,int point_offset) {
    for(int i=0;i<patch.points.rows();++i) for(int axis=0;axis<3;++axis) {
        samples[i*6+axis]=patch.points(i,axis); samples[i*6+3+axis]=patch.normals(i,axis);
    }
    for(size_t i=0;i<patch.faces.size();++i) for(int j=0;j<4;++j) quads[4*i+j]=patch.faces[i][j]+point_offset;
}
static void write(const Patches& patches,double* samples,int64_t* quads,int* metadata) {
    int point=0,face=0;
    for(size_t i=0;i<patches.size();++i) {
        const auto& patch=patches[i]; copy(patch,samples+point*6,quads+face*4,point);
        const std::array<int,9> row{point,patch.segments,face,int(patch.faces.size()),patch.first,patch.second,patch.mode,patch.mirror,patch.inversions};
        std::copy(row.begin(),row.end(),metadata+i*9);
        point+=int(patch.points.rows()); face+=int(patch.faces.size());
    }
}
}
int af_skin_annuli_sizes(uint64_t handle,int* sizes) {
    try {
        if(!sizes) throw std::runtime_error("Missing annulus size buffer.");
        const auto result=af::skin_annuli::sizes(*af::skin_annuli::get(handle));
        std::copy(result.begin(),result.end(),sizes); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_annuli_copy(uint64_t handle,double* samples,int64_t* quads,int* patches,const int* sizes) {
    try {
        const auto source=af::skin_annuli::get(handle); const auto required=af::skin_annuli::sizes(*source);
        if(!sizes||!std::equal(required.begin(),required.end(),sizes)||(!source->empty()&&(!samples||!quads||!patches)))
            throw std::runtime_error("Invalid annulus output buffers.");
        af::skin_annuli::write(*source,samples,quads,patches); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
void af_skin_annuli_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::skin_annuli::mutex); af::skin_annuli::registry.erase(handle);
}
