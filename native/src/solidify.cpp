// SPDX-FileCopyrightText: 2023 Blender Authors
// Adapted for AnthroForge; see native/migration/BLENDER_PRIMITIVES.md.
// SPDX-License-Identifier: GPL-3.0-or-later
// Simple Solidify geometry formulas adapted from Blender 5.0.1 MOD_solidify_extrude.cc.
#include "construction_internal.hpp"
#include <map>
#include <limits>

namespace af {
struct ShellEdge { int a,b; std::vector<int> faces; };
struct ShellData {
    Faces faces; Points normals,vertex_normals;
    std::map<std::pair<int,int>,ShellEdge> edges;
    std::vector<double> shortest,angles,correction;
};
static double angle(const V3& a,const V3& b) {
    return std::acos(std::clamp(a.normalized().dot(b.normalized()),-1.0,1.0));
}
static V3 face_normal(const Mesh& mesh,const std::vector<int64_t>& face) {
    V3 result=V3::Zero();
    for(size_t j=0;j<face.size();++j) {
        const V3 a=mesh.vertices.row(face[j]),b=mesh.vertices.row(face[(j+1)%face.size()]);
        result+=a.cross(b);
    }
    return result.normalized();
}
static double corner_angle(const Mesh& mesh,const std::vector<int64_t>& face,size_t j) {
    const V3 p=mesh.vertices.row(face[j]);
    const V3 a=mesh.vertices.row(face[(j+face.size()-1)%face.size()]);
    const V3 b=mesh.vertices.row(face[(j+1)%face.size()]);
    return angle(a-p,b-p);
}
static void shell_face(ShellData& data,const Mesh& mesh,int index) {
    const auto& face=data.faces[index];
    const V3 normal=face_normal(mesh,face); data.normals.push_back(normal);
    for(size_t j=0;j<face.size();++j) {
        const int a=int(face[j]),b=int(face[(j+1)%face.size()]);
        data.vertex_normals[a]+=normal*corner_angle(mesh,face,j);
        auto key=std::minmax(a,b);
        auto found=data.edges.try_emplace(key,ShellEdge{a,b,{}}).first;
        found->second.faces.push_back(index);
        const double length=(mesh.vertices.row(a)-mesh.vertices.row(b)).norm();
        data.shortest[a]=std::min(data.shortest[a],length);
        data.shortest[b]=std::min(data.shortest[b],length);
    }
}
static ShellData shell_data(const Mesh& mesh) {
    ShellData data; const auto n=mesh.vertices.rows();
    data.faces=mesh_faces(mesh); data.vertex_normals.resize(n,V3::Zero());
    data.shortest.resize(n,std::numeric_limits<double>::max());
    data.angles.resize(n,M_PI/2); data.correction.resize(n,1);
    for(size_t i=0;i<data.faces.size();++i) shell_face(data,mesh,int(i));
    for(auto& normal:data.vertex_normals) if(normal.norm()>1e-20) normal.normalize();
    return data;
}
static void high_quality_normals(ShellData& data) {
    Points normals(data.vertex_normals.size(),V3::Zero());
    for(const auto& pair:data.edges) {
        const auto& edge=pair.second;
        if(edge.faces.size()>2) continue;
        V3 normal=data.normals[edge.faces[0]];
        if(edge.faces.size()==2) {
            const V3 other=data.normals[edge.faces[1]],sum=normal+other;
            normal=sum.norm()>1e-20?V3(sum.normalized()*std::max(angle(normal,other),1e-4)):V3::Zero();
        }
        normals[edge.a]+=normal; normals[edge.b]+=normal;
    }
    for(size_t i=0;i<normals.size();++i)
        if(normals[i].norm()>1e-20) data.vertex_normals[i]=normals[i].normalized();
}
static void even_correction(ShellData& data,const Mesh& mesh) {
    std::vector<double> sum(data.vertex_normals.size(),0),weight(sum.size(),0);
    for(size_t i=0;i<data.faces.size();++i) {
        const auto& face=data.faces[i];
        for(size_t j=0;j<face.size();++j) {
            const auto vertex=face[j]; const double a=std::max(corner_angle(mesh,face,j),1e-7);
            const double dot=std::abs(data.vertex_normals[vertex].dot(data.normals[i]));
            sum[vertex]+=a/(dot>1e-7?dot:1); weight[vertex]+=a;
        }
    }
    for(size_t i=0;i<sum.size();++i) if(weight[i]>0) data.correction[i]=sum[i]/weight[i];
}
static double signed_edge_angle(const V3& first,const V3& second,const V3& axis) {
    const V3 a=first-axis*first.dot(axis),b=second-axis*second.dot(axis);
    double value=std::atan2(axis.dot(b.cross(a)),a.dot(b));
    if(value<0) value+=2*M_PI;
    return value;
}
static void clamp_angles(ShellData& data,const Mesh& mesh,bool even) {
    for(const auto& pair:data.edges) {
        const auto& e=pair.second;
        if(e.faces.size()!=2) continue;
        const V3 a=data.normals[e.faces[0]],b=data.normals[e.faces[1]];
        const V3 axis=(mesh.vertices.row(e.a)-mesh.vertices.row(e.b)).normalized();
        const double value=even?M_PI-angle(a,b):signed_edge_angle(a,b,axis);
        data.angles[e.a]=std::max(data.angles[e.a],value);
        data.angles[e.b]=std::max(data.angles[e.b],value);
    }
}
static double clamped_offset(const ShellData& data,int i,double offset,const double* s,bool positive) {
    double extent=std::abs(s[0])*s[7];
    if(s[4]&&s[8]) extent*=1+std::abs(s[1]);
    if(extent<1e-7) return offset;
    double limit=data.shortest[i];
    if(s[8]) {
        const double a=(!s[4]&&positive?2*M_PI-data.angles[i]:data.angles[i])*0.5;
        const double cosine=std::cos(a);
        if(cosine<=0) return offset;
        limit/=cosine;
    }
    return offset*std::min(1.0,limit/extent);
}
static V3 shell_vertex(const Mesh& mesh,const ShellData& data,int i,const double* s,const double* weights,bool upper) {
    double influence=weights?weights[i]:1;
    if(weights&&s[9]) influence=1-influence;
    influence=s[10]+(1-s[10])*influence;
    const double offset=s[0]*(s[1]+(upper?1:-1))*0.5*influence*data.correction[i];
    const V3 p=mesh.vertices.row(i);
    return p+data.vertex_normals[i]*clamped_offset(data,i,offset,s,upper);
}
static std::vector<int> shell_mapping(const ShellData& data,int count,bool shell) {
    std::vector<int> mapping(count,-1);
    if(shell) { for(int i=0;i<count;++i) mapping[i]=count+i; return mapping; }
    for(const auto& pair:data.edges) if(pair.second.faces.size()==1) {
        mapping[pair.second.a]=0; mapping[pair.second.b]=0;
    }
    for(auto& index:mapping) if(index==0) index=count++;
    return mapping;
}
static Points shell_points(const Mesh& mesh,const ShellData& data,const double* s,const double* weights,const std::vector<int>& mapping) {
    Points result;
    const bool first_upper=(s[0]>=0)!=(s[6]!=0);
    for(int i=0;i<mesh.vertices.rows();++i) result.push_back(shell_vertex(mesh,data,i,s,weights,first_upper));
    for(int i=0;i<mesh.vertices.rows();++i)
        if(mapping[i]>=0) result.push_back(shell_vertex(mesh,data,i,s,weights,!first_upper));
    return result;
}
static Faces shell_faces(const ShellData& data,const double* s,const std::vector<int>& mapping) {
    Faces faces=data.faces;
    if(!(s[2]&&s[3])) for(auto face:data.faces) {
        std::reverse(face.begin()+1,face.end());
        for(auto& i:face) i=mapping[i];
        faces.push_back(std::move(face));
    }
    if(s[2]) for(const auto& pair:data.edges) if(pair.second.faces.size()==1) {
        const auto& e=pair.second; faces.push_back({e.b,e.a,mapping[e.a],mapping[e.b]});
    }
    return faces;
}
static std::shared_ptr<Mesh> solidify(const Mesh& mesh,const double* s,const double* weights,uint64_t cancel) {
    auto data=shell_data(mesh);
    check_cancel(cancel);
    if(s[5]) high_quality_normals(data);
    if(s[4]) even_correction(data,mesh);
    if(s[8]) clamp_angles(data,mesh,s[4]!=0);
    const auto mapping=shell_mapping(data,int(mesh.vertices.rows()),!(s[2]&&s[3]));
    return make_mesh(shell_points(mesh,data,s,weights,mapping),shell_faces(data,s,mapping),cancel,mesh.prepared);
}
}
uint64_t af_solidify(uint64_t source,const double* settings,const double* weights,uint64_t cancel) {
    try { return af::retain(af::solidify(*af::mesh(source),settings,weights,cancel)); }
    catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
