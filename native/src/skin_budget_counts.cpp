#include "anthroforge/skin_density.h"
#include "mesh_internal.hpp"
#include <map>

namespace af::skin {
static int majority(const Mesh& mesh,int face,const int* owners) {
    std::map<int,int> votes;
    for(auto i=mesh.offsets[face];i<mesh.offsets[face+1];++i) {
        const int owner=owners[mesh.corners[i]]; if(owner>=0) ++votes[owner];
    }
    int chosen=-1,best=0;
    for(const auto& [owner,count]:votes) if(count>best) { chosen=owner; best=count; }
    return chosen;
}
static void validate(const Mesh& mesh,const int* owners,const int* mapping,int n,int regions) {
    if(!owners||!mapping||n<0||regions<1) throw std::runtime_error("Invalid topology budget inputs.");
    for(int i=0;i<mesh.vertices.rows();++i) if(owners[i]<-1||owners[i]>=n)
        throw std::runtime_error("Unknown topology budget owner.");
    for(int i=0;i<n;++i) if(mapping[i]<0||mapping[i]>=regions)
        throw std::runtime_error("Unknown topology budget region.");
}
}
int af_skin_budget_counts(uint64_t handle,const int* owners,const int* mapping,
    int owner_count,int region_count,int64_t* counts,uint64_t cancel) {
    try {
        if(!counts) throw std::runtime_error("Missing topology budget counts.");
        af::check_cancel(cancel); const auto mesh=af::mesh(handle);
        af::skin::validate(*mesh,owners,mapping,owner_count,region_count);
        std::fill(counts,counts+region_count,0);
        for(int face=0;face<int(mesh->offsets.size())-1;++face) {
            if(face%4096==0) af::check_cancel(cancel);
            const int owner=af::skin::majority(*mesh,face,owners);
            ++counts[owner<0?region_count-1:mapping[owner]];
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
