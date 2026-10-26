#include "mesh_internal.hpp"
#include "anthroforge/skin_flow.h"
#include <set>
namespace af::skin_flow {
static std::pair<int,int> edge(int a,int b) { return {std::min(a,b),std::max(a,b)}; }
static std::set<std::pair<int,int>> desired(const Mesh& mesh,const int* edges,int count,uint64_t cancel) {
    if(count<0||(count&&!edges)) throw std::runtime_error("Invalid FLOW feature edges.");
    std::set<std::pair<int,int>> result;
    for(int i=0;i<count;++i) {
        if(i%4096==0) check_cancel(cancel);
        const int a=edges[2LL*i],b=edges[2LL*i+1];
        if(a<0||b<0||a>=mesh.vertices.rows()||b>=mesh.vertices.rows())
            throw std::runtime_error("FLOW feature vertex outside mesh.");
        result.insert(edge(a,b));
    }
    return result;
}
static int rows(const Mesh& mesh,std::set<std::pair<int,int>>& wanted,int* output,uint64_t cancel) {
    int count=0;
    for(int i=0;i<mesh.triangles.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        for(int j=0;j<3;++j) {
            if(!wanted.erase(edge(mesh.triangles(i,j),mesh.triangles(i,(j+1)%3)))) continue;
            output[3LL*count]=1; output[3LL*count+1]=i; output[3LL*count+2]=j; ++count;
        }
    }
    return count;
}
}
int af_skin_flow_features(uint64_t source,const int* edges,int count,int* output,uint64_t cancel) {
    try {
        if(count&&!output) throw std::runtime_error("Missing FLOW feature output.");
        const auto mesh=af::mesh(source); auto wanted=af::skin_flow::desired(*mesh,edges,count,cancel);
        return af::skin_flow::rows(*mesh,wanted,output,cancel);
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}

int af_skin_quad_step(int target,int count,double* state) {
    try {
        if(target<1||count<1||!state||!std::isfinite(state[0])||state[0]<=0||std::isnan(state[1])||state[1]<0)
            throw std::runtime_error("Invalid QuadWild calibration state.");
        const double error=std::abs(double(count)-target); const bool keep=error<state[1],done=error<=.15*target;
        if(keep) state[1]=error;
        if(!done) state[0]*=std::sqrt(double(count)/target);
        return int(keep)+2*int(done);
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
