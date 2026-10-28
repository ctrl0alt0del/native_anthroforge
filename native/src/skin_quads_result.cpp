#include "skin_quads.hpp"
#include <mutex>
#include <unordered_map>
namespace af::skin_quads {
static std::mutex mutex;
static std::unordered_map<uint64_t,std::shared_ptr<const Result>> registry;
static uint64_t next=1;
uint64_t retain(Result value) {
    auto owned=std::make_shared<const Result>(std::move(value));
    std::lock_guard<std::mutex> lock(mutex); const auto id=next++;
    registry.emplace(id,std::move(owned)); return id;
}
static std::shared_ptr<const Result> get(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex); const auto found=registry.find(handle);
    if(found==registry.end()) throw std::runtime_error("Unknown skin topology resource.");
    return found->second;
}
Quads capture(const Mesh& mesh,const int* regions,const int* guides,uint64_t cancel) {
    if(!regions||!guides) throw std::runtime_error("Missing skin polygon provenance.");
    Quads result; check_cancel(cancel); const auto faces=mesh_faces(mesh);
    for(int i=0;i<mesh.vertices.rows();++i) result.points.push_back(mesh.vertices.row(i));
    for(size_t i=0;i<faces.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        if(faces[i].size()!=4||regions[i]<0||regions[i]>2||guides[i]<-1) throw std::runtime_error("Skin refinement requires quads and valid region labels.");
        Quad quad; std::copy(faces[i].begin(),faces[i].end(),quad.begin()); result.faces.push_back(quad);
        result.regions.push_back(regions[i]); result.guides.push_back(guides[i]);
    }
    return result;
}
Result complete(Quads source,uint64_t cancel) {
    Faces faces; faces.reserve(source.faces.size());
    for(size_t i=0;i<source.faces.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        faces.emplace_back(source.faces[i].begin(),source.faces[i].end());
    }
    return {make_mesh(source.points,faces,cancel),std::move(source.regions),std::move(source.guides)};
}
}
uint64_t af_skin_topology_mesh(uint64_t handle) {
    try { return af::retain(af::skin_quads::get(handle)->mesh); }
    catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
int af_skin_topology_labels(uint64_t handle,int* regions,int* guides,int count) {
    try {
        const auto result=af::skin_quads::get(handle);
        if(count!=int(result->regions.size())||!regions||!guides) throw std::runtime_error("Invalid skin topology label buffers.");
        std::copy(result->regions.begin(),result->regions.end(),regions);
        std::copy(result->guides.begin(),result->guides.end(),guides); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
void af_skin_topology_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::skin_quads::mutex); af::skin_quads::registry.erase(handle);
}
uint64_t af_skin_quads_split(uint64_t handle,const uint8_t* selected,const int* regions,const int* guides,uint64_t cancel) {
    try {
        if(!selected) throw std::runtime_error("Missing quad selection.");
        const auto input=af::skin_quads::capture(*af::mesh(handle),regions,guides,cancel);
        const af::skin_quads::Mask mask(selected,selected+input.faces.size());
        auto result=af::skin_quads::split(input,mask,cancel);
        return af::skin_quads::retain(af::skin_quads::complete(std::move(result),cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
