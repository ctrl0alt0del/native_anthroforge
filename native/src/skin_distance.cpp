#include "skin_fields.hpp"
#include "mesh_internal.hpp"
#include <algorithm>
#include <cmath>
#include <limits>

namespace af::skin {
struct Hull { std::vector<int> sites; Values edges, input, output; };
static double crossing(const Values& f,int q,int p) {
    return ((f[q]+double(q)*q)-(f[p]+double(p)*p))/(2.0*(q-p));
}
static void add_site(Hull& h,int q) {
    double edge=-INFINITY;
    while(!h.sites.empty()) {
        edge=crossing(h.input,q,h.sites.back());
        if(edge>h.edges.back()) break;
        h.sites.pop_back(); h.edges.pop_back();
    }
    h.sites.push_back(q); h.edges.push_back(h.sites.size()==1?-INFINITY:edge);
}
static void transform(Hull& h) {
    h.sites.clear(); h.edges.clear();
    for(int q=0;q<int(h.input.size());++q) if(std::isfinite(h.input[q])) add_site(h,q);
    h.output.assign(h.input.size(),INFINITY); size_t k=0;
    if(h.sites.empty()) return;
    for(int q=0;q<int(h.input.size());++q) {
        while(k+1<h.sites.size()&&h.edges[k+1]<q) ++k;
        const double delta=q-h.sites[k]; h.output[q]=delta*delta+h.input[h.sites[k]];
    }
}
static void axis(const Grid& g,Values& values,int a) {
    const uint64_t stride=a==0?uint64_t(g.shape[1])*g.shape[2]:a==1?g.shape[2]:1;
    const uint64_t block=stride*g.shape[a]; Hull h; h.input.resize(g.shape[a]);
    for(uint64_t start=0;start<g.count;start+=block) for(uint64_t offset=0;offset<stride;++offset) {
        if((offset&1023)==0) check_cancel(g.cancel);
        for(int q=0;q<g.shape[a];++q) h.input[q]=values[start+offset+q*stride];
        transform(h);
        for(int q=0;q<g.shape[a];++q) values[start+offset+q*stride]=h.output[q];
    }
}
static Values unseeded(const Grid& g) {
    Values result(g.count);
    for(uint64_t i=0;i<g.count;++i) {
        if((i&8191)==0) check_cancel(g.cancel);
        const auto c=coordinates(g,i);
        result[i]=g.voxel*std::sqrt(double(c[0]+1)*(c[0]+1)+double(c[1])*c[1]+double(c[2])*c[2]);
    }
    return result;
}
Values distance(const Grid& g,const Mask& seeds) {
    if(seeds.size()!=g.count) throw std::runtime_error("Invalid skin distance grid.");
    if(std::none_of(seeds.begin(),seeds.end(),[](uint8_t v){return v!=0;})) return unseeded(g);
    Values values(g.count);
    for(uint64_t i=0;i<g.count;++i) values[i]=seeds[i]?0:INFINITY;
    for(int a=0;a<3;++a) axis(g,values,a);
    for(auto& v:values) v=std::sqrt(v)*g.voxel;
    return values;
}
Mask dilate(const Grid& g,const Mask& seeds) {
    Mask result=seeds;
    for(uint64_t i=0;i<g.count;++i) {
        if((i&8191)==0) check_cancel(g.cancel);
        if(!seeds[i]) continue;
        const auto c=coordinates(g,i);
        for(int a=0;a<3;++a) for(int step:{-1,1}) {
            auto p=c; p[a]+=step;
            if(p[a]>=0&&p[a]<g.shape[a]) result[index(g,p[0],p[1],p[2])]=1;
        }
    }
    return result;
}
}
