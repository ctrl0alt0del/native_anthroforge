#include "mesh_internal.hpp"
#include "path_internal.hpp"
#include "anthroforge/skin_capture.h"
#include <limits>

namespace af::skin {
struct Capture {
    double* xyz; int64_t* faces; int* owners; uint8_t* skeletal;
    int64_t* segments=nullptr; int* segment_owners=nullptr; int segment_count=0;
    int vertices=0,triangles=0; V3 low=V3::Constant(INFINITY),high=V3::Constant(-INFINITY);
};
static void positions(Capture& out,const Mesh& mesh,const M4& frame,uint64_t cancel) {
    for(int i=0;i<mesh.vertices.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        const V3 value=point(frame,mesh.vertices.row(i));
        if(!value.allFinite()) throw std::runtime_error("Skin source has nonfinite positions.");
        Eigen::Map<V3>(out.xyz+3LL*(out.vertices+i))=value;
        out.low=out.low.cwiseMin(value); out.high=out.high.cwiseMax(value);
    }
}
static void connectivity(Capture& out,const Mesh& mesh,bool reflected,int owner,bool scp,uint64_t cancel) {
    for(int i=0;i<mesh.triangles.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        for(int j=0;j<3;++j) out.faces[3LL*(out.triangles+i)+j]=
            int64_t(out.vertices)+mesh.triangles(i,reflected?2-j:j);
        out.owners[out.triangles+i]=owner; out.skeletal[out.triangles+i]=uint8_t(scp);
    }
    out.vertices+=int(mesh.vertices.rows()); out.triangles+=int(mesh.triangles.rows());
}
static void source(Capture& out,const Mesh& mesh,const double* matrix,int owner,bool scp,uint64_t cancel) {
    const M4 frame=Eigen::Map<const M4>(matrix);
    if(!frame.allFinite() || std::abs(frame.block<3,3>(0,0).determinant())<1.e-18)
        throw std::runtime_error("Skin source requires a nonsingular finite transform.");
    positions(out,mesh,frame,cancel);
    connectivity(out,mesh,frame.block<3,3>(0,0).determinant()<0,owner,scp,cancel);
}
static void path_connectivity(Capture& out,const Path& path,int count,int owner) {
    for(int i=0;i<count-(path.closed?0:1);++i) {
        const int edge=out.segment_count++; out.segment_owners[edge]=owner;
        out.segments[2LL*edge]=out.vertices+i; out.segments[2LL*edge+1]=out.vertices+(i+1)%count;
    }
    out.vertices+=count;
}
static void path_source(Capture& out,const Path& path,const double* matrix,int owner,uint64_t cancel) {
    const M4 frame=Eigen::Map<const M4>(matrix); const int count=int(path.samples.size()/11);
    if(!frame.allFinite()||std::abs(frame.block<3,3>(0,0).determinant())<1.e-18)
        throw std::runtime_error("Skin centerline requires a nonsingular finite transform.");
    for(int i=0;i<count;++i) {
        if(i%4096==0) check_cancel(cancel);
        const V3 value=point(frame,V3(path.samples.data()+11LL*i));
        if(!value.allFinite()) throw std::runtime_error("Nonfinite skin centerline position.");
        Eigen::Map<V3>(out.xyz+3LL*(out.vertices+i))=value;
        out.low=out.low.cwiseMin(value); out.high=out.high.cwiseMax(value);
    }
    path_connectivity(out,path,count,owner);
}

struct CaptureLimits { int vertices,faces,segments; };
static void mixed_source(Capture& out,uint64_t handle,int kind,const double* frame,int owner,
                         bool scp,const CaptureLimits& limits,uint64_t cancel) {
    if(kind==0) {
        const auto item=mesh(handle);
        if(item->vertices.rows()>limits.vertices-out.vertices||item->triangles.rows()>limits.faces-out.triangles)
            throw std::runtime_error("Skin capture output buffers are too small.");
        source(out,*item,frame,owner,scp,cancel);
    } else if(kind==1) {
        const auto item=path(handle); const int count=int(item->samples.size()/11);
        if(count>limits.vertices-out.vertices||count-(item->closed?0:1)>limits.segments-out.segment_count)
            throw std::runtime_error("Skin centerline output buffers are too small.");
        path_source(out,*item,frame,owner,cancel);
    } else throw std::runtime_error("Unknown skin source kind.");
}
static void policies(const double* input,int count,double length,double* output) {
    for(int i=0;i<count;++i) {
        const double gap=input[3*i],strength=input[3*i+1],scp=input[3*i+2];
        if(!std::isfinite(gap)||gap<0||gap>1||!std::isfinite(strength)||strength<0||strength>1||(scp!=0&&scp!=1))
            throw std::runtime_error("Invalid skin source policy.");
        output[3*i]=gap*length; output[3*i+1]=strength; output[3*i+2]=scp;
    }
}
static void assemble(Capture& out,const uint64_t* handles,const double* frames,int count,
                     int vertices,int faces,const double* rules,uint64_t cancel) {
    for(int i=0;i<count;++i) {
        check_cancel(cancel); const auto item=mesh(handles[i]);
        if(item->vertices.rows()>vertices-out.vertices || item->triangles.rows()>faces-out.triangles)
            throw std::runtime_error("Skin capture output buffers are too small.");
        source(out,*item,frames+16LL*i,i,rules[3*i+2]!=0,cancel);
    }
    if(out.vertices!=vertices||out.triangles!=faces||vertices==0||faces==0)
        throw std::runtime_error("Skin capture requires matching nonempty geometry buffers.");
}
}
int af_skin_capture(const uint64_t* meshes,const double* frames,int sources,int vertices,int faces,
    const double* policies,double* xyz,int64_t* triangles,int* owners,uint8_t* skeletal,double* absolute,uint64_t cancel) {
    try {
        if(!meshes||!frames||!policies||!xyz||!triangles||!owners||!skeletal||!absolute||sources<1||vertices<0||faces<0)
            throw std::runtime_error("Missing skin capture buffers.");
        af::skin::Capture out{xyz,triangles,owners,skeletal};
        af::skin::assemble(out,meshes,frames,sources,vertices,faces,policies,cancel);
        af::skin::policies(policies,sources,(out.high-out.low).maxCoeff(),absolute); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}

int af_skin_capture_sources(const uint64_t* handles,const int* kinds,const double* frames,int count,
    const int* limits,const double* rules,double* xyz,int64_t* faces,int* owners,uint8_t* scp,
    double* absolute,int64_t* edges,int* edge_owners,uint64_t cancel) {
    try {
        if(!handles||!kinds||!frames||!limits||!rules||!xyz||!faces||!owners||!scp||!absolute||!edges||!edge_owners||count<1)
            throw std::runtime_error("Missing skin source capture buffers.");
        af::skin::Capture out{xyz,faces,owners,scp,edges,edge_owners};
        const af::skin::CaptureLimits capacity{limits[0],limits[1],limits[2]};
        for(int i=0;i<count;++i) af::skin::mixed_source(out,handles[i],kinds[i],frames+16LL*i,i,rules[3*i+2]!=0,capacity,cancel);
        if(out.vertices!=limits[0]||out.triangles!=limits[1]||out.segment_count!=limits[2]||out.vertices<2)
            throw std::runtime_error("Skin capture counts do not match sources.");
        af::skin::policies(rules,count,(out.high-out.low).maxCoeff(),absolute); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
