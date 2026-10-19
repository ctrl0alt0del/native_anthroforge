#include "construction_internal.hpp"
#include <numeric>

namespace af {
std::vector<int> allocate_edges(const std::vector<double>& lengths,int edges) {
    const int count=int(lengths.size()),remaining=edges-count; std::vector<int> result(count,1),order(count);
    if(count<1||remaining<0) throw std::runtime_error("Sampling budget must retain every required span.");
    const double total=std::accumulate(lengths.begin(),lengths.end(),0.0); std::vector<double> fractions(count);
    int left=remaining;
    for(int i=0;i<count;++i) {
        const double raw=remaining*(total>1e-12?lengths[i]/total:1.0/count),whole=std::floor(raw);
        result[i]+=int(whole); left-=int(whole); fractions[i]=raw-whole;
    }
    std::iota(order.begin(),order.end(),0);
    std::stable_sort(order.begin(),order.end(),[&](int a,int b){return fractions[a]>fractions[b];});
    for(int i=0;i<left;++i) ++result[order[i]];
    return result;
}
}
