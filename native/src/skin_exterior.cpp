#include "skin_fields.hpp"
#include "mesh_internal.hpp"
#include <algorithm>

namespace af::skin {
static void visit(const Grid& g,const Mask& free,Mask& outside,std::vector<uint64_t>& queue,uint64_t i) {
    const auto c=coordinates(g,i);
    for(int x=-1;x<=1;++x) for(int y=-1;y<=1;++y) for(int z=-1;z<=1;++z) {
        const int a=c[0]+x,b=c[1]+y,d=c[2]+z;
        if(a<0||b<0||d<0||a>=g.shape[0]||b>=g.shape[1]||d>=g.shape[2]) continue;
        const auto next=index(g,a,b,d);
        if(free[next]&&!outside[next]) { outside[next]=1; queue.push_back(next); }
    }
}
static Mask connected(const Grid& g,const Mask& free) {
    Mask outside(g.count);
    if(!free[0]) {
        for(uint64_t i=0;i<g.count;++i) outside[i]=!free[i];
        return outside;
    }
    std::vector<uint64_t> queue; queue.reserve(g.count); queue.push_back(0); outside[0]=1;
    for(size_t head=0;head<queue.size();++head) {
        if((head&8191)==0) check_cancel(g.cancel);
        visit(g,free,outside,queue,queue[head]);
    }
    return outside;
}
Values exterior(const Grid& g,const Mask& surface,double probe,double offset) {
    Mask free(g.count);
    {
        const auto distances=distance(g,surface);
        for(uint64_t i=0;i<g.count;++i) free[i]=distances[i]>probe+offset;
    }
    auto result=distance(g,connected(g,free));
    for(auto& value:result) value-=probe;
    return result;
}
}
