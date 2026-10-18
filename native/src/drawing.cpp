/* Projection/sampling policy follows Blender 5.0.1 editcurve_paint.cc; see vendor/PROVENANCE.md. */
#include "mesh_internal.hpp"
#include "anthroforge/drawing.h"
#include <array>
#include <mutex>
#include <unordered_map>

namespace af {
using Pointer=Eigen::Matrix<double,9,1>;
using Sample=std::array<double,4>;
struct DrawingSurface { std::shared_ptr<Mesh> mesh; M4 frame; };
struct Projection {
    V3 origin,normal,previous;
    bool surface=false,locked=false;
    int first=0;
    double offset=0;
    bool relative=false;
};
struct Stroke {
    std::vector<DrawingSurface> surfaces;
    Projection projection;
    std::vector<Sample> samples;
    std::vector<Projection> states;
    Pointer pointer=Pointer::Zero();
    bool rebased=false;
};
static std::mutex stroke_mutex;
static std::unordered_map<uint64_t,std::shared_ptr<Stroke>> strokes;
static uint64_t next_stroke=1;
static std::shared_ptr<Stroke> stroke(uint64_t handle) {
    std::lock_guard<std::mutex> lock(stroke_mutex); const auto found=strokes.find(handle);
    if(found==strokes.end()) throw std::runtime_error("Unknown drawing stroke.");
    return found->second;
}
static Pointer pointer_input(const double* data) {
    if(!data) throw std::runtime_error("Drawing requires a pointer ray.");
    const Pointer value=Eigen::Map<const Pointer>(data);
    if(!value.allFinite()||value.segment<3>(3).norm()<1e-15||value[8]<0)
        throw std::runtime_error("Pointer ray must be finite and radius nonnegative.");
    return value;
}
static V3 surface_normal(const DrawingSurface& surface,int triangle) {
    const auto& mesh=*surface.mesh; const auto face=mesh.triangles.row(triangle);
    const V3 a=mesh.vertices.row(face[1])-mesh.vertices.row(face[0]);
    const V3 b=mesh.vertices.row(face[2])-mesh.vertices.row(face[0]);
    const V3 normal=surface.frame.block<3,3>(0,0).inverse().transpose()*a.cross(b);
    if(normal.norm()<1e-15) throw std::runtime_error("Degenerate drawing surface normal.");
    return normal.normalized();
}
static bool surface_hit(const Stroke& stroke,const Pointer& ray,V3& point,V3& normal) {
    double closest=std::numeric_limits<double>::infinity(); bool found=false;
    for(const auto& surface:stroke.surfaces) {
        double output[10];
        if(!pick_surface(*surface.mesh,surface.frame,ray.head<3>(),ray.segment<3>(3),output)||output[0]>=closest) continue;
        closest=output[0]; point=Eigen::Map<const V3>(output+4);
        normal=surface_normal(surface,int(output[2])); found=true;
    }
    return found;
}
static V3 plane_hit(const Pointer& ray,const V3& point,const V3& normal) {
    const V3 direction=ray.segment<3>(3); const double denominator=normal.dot(direction);
    if(std::abs(denominator)<1e-12*direction.norm()) throw std::runtime_error("Drawing ray is parallel to the depth plane.");
    const double distance=normal.dot(point-ray.head<3>())/denominator;
    if(distance<0) throw std::runtime_error("Drawing depth plane is behind the camera.");
    return ray.head<3>()+direction*distance;
}
static Sample project(const Stroke& stroke,Projection& state,const Pointer& ray) {
    V3 point,normal;
    if(state.surface&&!state.locked&&surface_hit(stroke,ray,point,normal)) {
        point+=normal*state.offset*(state.relative?ray[8]:1);
        if(state.first) {
            state.origin=point; state.locked=true;
            if(state.first==2) state.normal=normal;
        }
    } else point=plane_hit(ray,state.surface&&!state.locked?state.previous:state.origin,state.normal);
    state.previous=point; return {point.x(),point.y(),point.z(),ray[8]};
}
static std::shared_ptr<Stroke> make_stroke(int count,const uint64_t* meshes,const double* matrices,const double* plane,const double* settings) {
    if(count<0||!plane||!settings||(count&&(!meshes||!matrices))) throw std::runtime_error("Invalid stroke inputs.");
    auto value=std::make_shared<Stroke>(); auto& state=value->projection;
    state.origin=state.previous=Eigen::Map<const V3>(plane); state.normal=Eigen::Map<const V3>(plane+3);
    if(!state.origin.allFinite()||!state.normal.allFinite()||state.normal.norm()<1e-15||!std::isfinite(settings[2]))
        throw std::runtime_error("Invalid drawing depth or offset.");
    state.normal.normalize(); state.surface=settings[0]!=0; state.first=int(settings[1]);
    state.offset=settings[2]; state.relative=settings[3]!=0;
    if(state.first<0||state.first>2) throw std::runtime_error("Unknown first-hit plane setting.");
    for(int i=0;i<count;++i) value->surfaces.push_back({mesh(meshes[i]),Eigen::Map<const M4>(matrices+i*16)});
    return value;
}
static void append_sample(Stroke& stroke,const Pointer& ray) {
    if(stroke.samples.size()>=100000) throw std::runtime_error("Stroke sample limit reached.");
    auto state=stroke.projection; const auto sample=project(stroke,state,ray);
    stroke.states.push_back(stroke.projection); stroke.samples.push_back(sample);
    stroke.projection=state; stroke.pointer=ray;
}
static int append_pointer(Stroke& stroke,const Pointer& ray,bool interpolate) {
    const Pointer previous=stroke.pointer;
    const double distance=(ray.segment<2>(6)-previous.segment<2>(6)).norm();
    if(distance>300000||!std::isfinite(distance)) throw std::runtime_error("Pointer step exceeds stroke sample limit.");
    if(!stroke.samples.empty()&&interpolate&&!stroke.rebased&&distance<1) return int(stroke.samples.size());
    const int steps=interpolate&&!stroke.rebased&&!stroke.samples.empty()?int(std::ceil(distance/3)):1;
    if(steps>100000-int(stroke.samples.size())) throw std::runtime_error("Stroke sample limit reached.");
    for(int i=1;i<=std::max(1,steps);++i) append_sample(stroke,previous+(ray-previous)*(double(i)/std::max(1,steps)));
    stroke.rebased=false;
    return int(stroke.samples.size());
}
}
uint64_t af_stroke_create(int count,const uint64_t* meshes,const double* matrices,const double* plane,const double* settings) {
    try {
        auto value=af::make_stroke(count,meshes,matrices,plane,settings);
        std::lock_guard<std::mutex> lock(af::stroke_mutex); const auto key=af::next_stroke++;
        af::strokes.emplace(key,std::move(value)); return key;
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_stroke_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::stroke_mutex); af::strokes.erase(handle);
}
int af_stroke_append(uint64_t handle,const double* pointer,int interpolate) {
    try { return af::append_pointer(*af::stroke(handle),af::pointer_input(pointer),interpolate!=0); }
    catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
int af_stroke_probe(uint64_t handle,const double* pointer,double* output) {
    try {
        if(!output) throw std::runtime_error("Stroke preview needs an output buffer.");
        const auto value=af::stroke(handle); auto state=value->projection;
        const auto sample=af::project(*value,state,af::pointer_input(pointer));
        std::copy(sample.begin(),sample.end(),output); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_stroke_read(uint64_t handle,int start,int capacity,double* output) {
    try {
        const auto value=af::stroke(handle); const int count=int(value->samples.size());
        if(start<0||start>count||capacity<0||!output) throw std::runtime_error("Invalid stroke read range.");
        const int available=std::min(count-start,capacity);
        for(int i=0;i<available;++i) std::copy(value->samples[start+i].begin(),value->samples[start+i].end(),output+i*4);
        return available;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
int af_stroke_pop(uint64_t handle) {
    try {
        auto value=af::stroke(handle);
        if(!value->samples.empty()) {
            value->projection=value->states.back(); value->states.pop_back(); value->samples.pop_back();
        }
        return int(value->samples.size());
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
int af_drawing_plane(const double* frame,double* output) {
    try {
        if(!frame||!output) throw std::runtime_error("Plane requires a frame and output buffer.");
        const af::M4 matrix=Eigen::Map<const af::M4>(frame);
        const af::V3 normal=matrix.block<3,1>(0,0).cross(matrix.block<3,1>(0,1));
        if(!matrix.allFinite()||normal.norm()<1e-15) throw std::runtime_error("Invalid image plane.");
        Eigen::Map<af::V3> origin(output),direction(output+3);
        origin=matrix.block<3,1>(0,3); direction=normal.normalized(); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_stroke_view(uint64_t handle,const double* normal) {
    try {
        if(!normal) throw std::runtime_error("View normal is required.");
        const af::V3 direction=Eigen::Map<const af::V3>(normal);
        if(!direction.allFinite()||direction.norm()<1e-15) throw std::runtime_error("View normal must be finite and nonzero.");
        auto value=af::stroke(handle); auto& state=value->projection;
        if(!(state.locked&&state.first==2)) state.normal=direction.normalized();
        if(!state.surface&&!value->samples.empty()) state.origin=state.previous;
        value->rebased=true; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
