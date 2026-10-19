#include "mesh_internal.hpp"
#include <mutex>
#include <unordered_map>

namespace af {
static std::mutex registry_mutex;
static std::unordered_map<uint64_t,std::shared_ptr<Mesh>> registry;
static uint64_t next_id=1;
static thread_local std::string last_error;
static void memory_row(uint64_t handle,const Mesh& value,uint64_t* row) {
    row[0]=handle; row[1]=reinterpret_cast<uint64_t>(&value);
    row[2]=sizeof(Mesh)+value.vertices.size()*sizeof(double)+value.triangles.size()*sizeof(int)
        +(value.corners.capacity()+value.offsets.capacity()+value.polygons.capacity()+value.material.capacity())*sizeof(int64_t);
    // libigl AABB has one leaf per triangle and two children per internal node; root is in Mesh.
    row[3]=value.prepared?uint64_t(std::max<int64_t>(0,2*value.triangles.rows()-2))*sizeof(value.tree):0;
    row[4]=value.chunks.capacity()*sizeof(std::vector<float>);
    for(const auto& chunk:value.chunks) row[4]+=chunk.capacity()*sizeof(float);
    row[5]=value.vertices.rows(); row[6]=value.triangles.rows();
}
void set_error(const std::string& message) { last_error=message; }
std::shared_ptr<Mesh> mesh(uint64_t handle) {
    std::lock_guard<std::mutex> lock(registry_mutex);
    auto found=registry.find(handle);
    if(found==registry.end()) throw std::runtime_error("Unknown mesh handle.");
    return found->second;
}
uint64_t retain(std::shared_ptr<Mesh> value) {
    std::lock_guard<std::mutex> lock(registry_mutex);
    const auto id=next_id++; registry[id]=std::move(value); return id;
}
void check_cancel(uint64_t token) {
    if(token&&reinterpret_cast<Cancellation*>(token)->cancelled.load())
        throw std::runtime_error("Calculation cancelled.");
}
}
const char* af_last_error() { return af::last_error.c_str(); }
int af_mesh_memory_snapshot(uint64_t* rows,int capacity,uint64_t* total_handles) {
    if(capacity<0||!total_handles||(capacity>0&&!rows)) return -1;
    std::lock_guard<std::mutex> lock(af::registry_mutex);
    *total_handles=af::registry.size(); int count=0;
    for(const auto& entry:af::registry) {
        if(count>=capacity) break;
        af::memory_row(entry.first,*entry.second,rows+7*count); ++count;
    }
    return count;
}
uint64_t af_cancel_create() { return reinterpret_cast<uint64_t>(new af::Cancellation()); }
void af_cancel_request(uint64_t token) {
    if(token) reinterpret_cast<af::Cancellation*>(token)->cancelled.store(true);
}
void af_cancel_release(uint64_t token) { delete reinterpret_cast<af::Cancellation*>(token); }
uint64_t af_mesh_import(const char* path,double units,int y_up,uint64_t cancel) {
    try { return af::retain(af::read_mesh(path,units,y_up!=0,cancel)); }
    catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_mesh_create(const double* vertices,int64_t count,const int64_t* corners,
                       const int64_t* offsets,int64_t faces) {
    try {
        if(!vertices||!corners||!offsets||count<=0||faces<=0) throw std::runtime_error("Invalid mesh arrays.");
        auto mesh=std::make_shared<af::Mesh>();
        mesh->vertices=Eigen::Map<const af::Vertices>(vertices,count,3); af::Faces polygons;
        for(int64_t i=0;i<faces;++i) {
            if(offsets[i]<0||offsets[i+1]<offsets[i]) throw std::runtime_error("Invalid polygon offsets.");
            polygons.emplace_back(corners+offsets[i],corners+offsets[i+1]);
        }
        af::prepare_mesh(*mesh,polygons); return af::retain(mesh);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_mesh_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::registry_mutex); af::registry.erase(handle);
}
int af_mesh_sizes(uint64_t handle,int64_t* sizes) {
    try {
        const auto mesh=af::mesh(handle);
        sizes[0]=mesh->vertices.rows(); sizes[1]=int64_t(mesh->offsets.size())-1;
        sizes[2]=int64_t(mesh->corners.size()); sizes[3]=mesh->triangles.rows();
        sizes[4]=int64_t(mesh->chunks.size()); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
const void* af_mesh_buffer(uint64_t handle,int kind) {
    try {
        const auto mesh=af::mesh(handle);
        switch(kind) {
            case 0:return mesh->vertices.data(); case 1:return mesh->corners.data();
            case 2:return mesh->offsets.data(); case 3:return mesh->triangles.data();
            case 4:return mesh->polygons.data(); default: return nullptr;
        }
    } catch(const std::exception& error) { af::set_error(error.what()); return nullptr; }
}
int af_mesh_bounds(uint64_t handle,double* bounds) {
    try { const auto mesh=af::mesh(handle); std::copy(mesh->bounds,mesh->bounds+6,bounds); return 0; }
    catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_mesh_chunk(uint64_t handle,int chunk,const float** data,int* count) {
    try {
        const auto mesh=af::mesh(handle);
        const auto& values=mesh->chunks.at(chunk);
        *data=values.data(); *count=int(values.size()); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
