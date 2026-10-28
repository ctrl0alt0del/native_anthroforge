#include "anthroforge/skin_validation.h"
#include "skin_loops.hpp"
#include <map>
#include <set>
namespace af::skin_validation {
using Graph=std::vector<std::set<int64_t>>;
using Edge=std::pair<int64_t,int64_t>;
struct Use { int count=0,sign=0; };
struct MeshEdges { std::map<Edge,Use> edges; Graph graph; int degenerates=0; bool quads=true; };
static double diagonal(const Mesh& mesh) {
    return std::max((mesh.vertices.colwise().maxCoeff()-mesh.vertices.colwise().minCoeff()).norm(),1e-9);
}
static double area(const Mesh& mesh,const std::vector<int64_t>& face) {
    const V3 origin=mesh.vertices.row(face[0]); double total=0;
    for(size_t i=1;i+1<face.size();++i) {
        const V3 a=mesh.vertices.row(face[i]),b=mesh.vertices.row(face[i+1]);
        total+=(a-origin).cross(b-origin).norm();
    }
    return total;
}
static MeshEdges edges(const Mesh& mesh,uint64_t cancel) {
    MeshEdges result; result.graph.resize(mesh.vertices.rows()); const auto faces=mesh_faces(mesh);
    const double extent=std::max((mesh.vertices.colwise().maxCoeff()-mesh.vertices.colwise().minCoeff()).maxCoeff(),1.);
    for(size_t i=0;i<faces.size();++i) {
        if(i%4096==0) check_cancel(cancel); const auto& face=faces[i]; result.quads&=face.size()==4;
        result.degenerates+=area(mesh,face)<extent*extent*1e-12;
        for(size_t j=0;j<face.size();++j) {
            const auto a=face[j],b=face[(j+1)%face.size()]; auto& use=result.edges[std::minmax(a,b)];
            ++use.count; use.sign+=a<b?1:-1; result.graph[a].insert(b); result.graph[b].insert(a);
        }
    }
    return result;
}
static int components(const Graph& graph,uint64_t cancel) {
    std::vector<bool> seen(graph.size(),false); std::vector<int64_t> stack; int count=0;
    for(size_t i=0;i<graph.size();++i) {
        if(i%4096==0) check_cancel(cancel); if(seen[i]||graph[i].empty()) continue;
        ++count; stack.push_back(int64_t(i)); seen[i]=true;
        while(!stack.empty()) {
            const auto id=stack.back(); stack.pop_back();
            for(const auto next:graph[id]) if(!seen[next]) { seen[next]=true; stack.push_back(next); }
        }
    }
    return count;
}
static void edge_quality(const MeshEdges& mesh,int patches,double* output,uint64_t cancel) {
    Graph boundary(mesh.graph.size()); bool orientable=true,manifold=true,regular=true; size_t valence=0;
    for(const auto& [edge,use]:mesh.edges) {
        manifold&=use.count<=2; orientable&=use.count==1||(use.count==2&&use.sign==0);
        if(use.count==1) { boundary[edge.first].insert(edge.second); boundary[edge.second].insert(edge.first); }
    }
    for(size_t i=0;i<mesh.graph.size();++i) {
        valence=std::max(valence,mesh.graph[i].size()); regular&=boundary[i].empty()||boundary[i].size()==2;
    }
    output[2]=components(mesh.graph,cancel); output[3]=orientable; output[4]=manifold;
    output[6]=components(boundary,cancel); output[7]=regular&&(output[6]==patches||output[6]==patches+1);
    output[13]=double(valence); output[14]=valence<=8;
}
static double symmetry(const Mesh& mesh,const double* value,uint64_t cancel) {
    if(!value) return 0; const auto plane=skin_loops::plane(value);
    const auto index=skin_loops::point_index(mesh.vertices,cancel); double maximum=0;
    for(int i=0;i<mesh.vertices.rows();++i) {
        if(i%4096==0) check_cancel(cancel); const V3 p=mesh.vertices.row(i);
        const V3 reflected=p-2*(p-plane.origin).dot(plane.normal)*plane.normal;
        maximum=std::max(maximum,index->nearest(mesh.vertices,reflected).second);
    }
    return std::sqrt(maximum);
}
static double fidelity(const Mesh& mesh,const Mesh& envelope,uint64_t cancel) {
    Surface surface(envelope,M4::Identity()); std::vector<double> distances; distances.reserve(mesh.vertices.rows());
    for(int i=0;i<mesh.vertices.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        distances.push_back(std::sqrt(nearest(surface,mesh.vertices.row(i)).distance));
    }
    std::sort(distances.begin(),distances.end()); const double at=.95*(distances.size()-1);
    const size_t low=size_t(std::floor(at)),high=size_t(std::ceil(at));
    return distances[low]+(at-low)*(distances[high]-distances[low]);
}
static void inspect(const Mesh& mesh,const Mesh& envelope,const int* regions,int guide_faces,
                    int patches,const double* plane,double* output,uint64_t cancel) {
    const auto topology=edges(mesh,cancel); output[0]=mesh.vertices.allFinite(); output[1]=topology.quads;
    output[5]=topology.degenerates==0; output[15]=topology.degenerates; edge_quality(topology,patches,output,cancel);
    int guides=0; for(size_t i=0;i+1<mesh.offsets.size();++i) guides+=regions[i]==2;
    output[8]=guides==guide_faces; output[9]=symmetry(mesh,plane,cancel);
    output[10]=output[9]<=1e-6*diagonal(envelope); output[11]=fidelity(mesh,envelope,cancel);
    output[12]=output[11]<=.005*diagonal(envelope);
}
}
int af_skin_topology_quality(uint64_t handle,uint64_t source,const int* regions,int guide_faces,
                            int patches,const double* plane,double* output,uint64_t cancel) {
    try {
        if(!regions||!output||guide_faces<0||patches<0) throw std::runtime_error("Invalid skin topology diagnostic buffers.");
        af::check_cancel(cancel); const auto mesh=af::mesh(handle),envelope=af::mesh(source);
        af::skin_validation::inspect(*mesh,*envelope,regions,guide_faces,patches,plane,output,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_deformed_quality(uint64_t handle,double* output,uint64_t cancel) {
    try {
        if(!output) throw std::runtime_error("Missing skin deformation quality output.");
        af::check_cancel(cancel); const auto mesh=af::mesh(handle);
        const auto topology=af::skin_validation::edges(*mesh,cancel);
        std::fill(output,output+16,0); output[0]=mesh->vertices.allFinite(); output[1]=topology.quads;
        output[5]=topology.degenerates==0; output[15]=topology.degenerates;
        af::skin_validation::edge_quality(topology,0,output,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
