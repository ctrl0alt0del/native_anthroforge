// Blender 5.0.1 mesh_calc_edges.cc: ordered insertion in low-vertex hash partitions.
#include "blender_mesh.hpp"
#include <set>
#include <thread>
namespace af::blender_mesh {
static unsigned partitions(const Mesh& mesh) {
    if(mesh.offsets.size()<=1000) return 1;
    const auto threads=std::max(1u,std::min(8u,std::thread::hardware_concurrency()));
    unsigned count=1; while(count*2<=threads) count*=2; return count;
}
static void append_edges(const Mesh& mesh,unsigned index,unsigned mask,std::vector<std::array<int,2>>& output,uint64_t cancel) {
    std::set<std::pair<int,int>> seen;
    for(size_t face=1;face<mesh.offsets.size();++face) {
        if(face%4096==0) check_cancel(cancel);
        const auto first=mesh.offsets[face-1],end=mesh.offsets[face];
        for(auto i=first;i<end;++i) {
            const int a=int(mesh.corners[i==first?end-1:i-1]),b=int(mesh.corners[i]);
            const auto edge=std::minmax(a,b);
            if((unsigned(edge.first)&mask)==index&&seen.insert(edge).second) output.push_back({edge.first,edge.second});
        }
    }
}
std::vector<std::array<int,2>> edge_order(const Mesh& source,uint64_t cancel) {
    if(!source.ordered_edges.empty()) return source.ordered_edges;
    std::vector<std::array<int,2>> result; const auto count=partitions(source);
    for(unsigned i=0;i<count;++i) append_edges(source,i,count-1,result,cancel);
    return result;
}
}
