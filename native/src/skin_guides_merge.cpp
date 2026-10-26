#include "skin_guides.hpp"
#include <map>
namespace af::skin_guides {
static void validate(const AFGuideInput& row,uint64_t cancel) {
    if(row.sample_count<0||row.point_count<0||row.path_count<0||row.sample_count>16777216
       ||row.point_count>16777216||row.path_count>16777216)
        throw std::runtime_error("Invalid FLOW batch sizes.");
    if((row.sample_count&&!row.samples)||(row.point_count&&!row.points)||!row.offsets
       ||row.offsets[0]!=0||row.offsets[row.path_count]!=row.point_count)
        throw std::runtime_error("Invalid FLOW batch buffers.");
    for(int64_t i=0;i<row.path_count;++i) {
        if(i%4096==0) check_cancel(cancel);
        if(row.offsets[i]<0||row.offsets[i]>row.point_count||row.offsets[i+1]>row.point_count||row.offsets[i+1]<row.offsets[i]+2)
            throw std::runtime_error("A FLOW path requires at least two points.");
    }
}
static int owner(Guides& result,std::map<int,int>& mapping,int source,double value) {
    if(!std::isfinite(value)||value<0||value>INT_MAX||value!=std::floor(value))
        throw std::runtime_error("Invalid local FLOW owner.");
    const int local=int(value); auto found=mapping.find(local);
    if(found!=mapping.end()) return found->second;
    const int next=int(result.regions.size()); mapping.emplace(local,next);
    result.regions.push_back({source,local}); return next;
}
static void samples(Guides& result,const AFGuideInput& row,int source,uint64_t cancel) {
    std::map<int,int> mapping;
    for(int64_t i=0;i<row.sample_count;++i) {
        if(i%4096==0) check_cancel(cancel);
        std::array<double,10> value{}; std::copy(row.samples+10*i,row.samples+10*i+10,value.begin());
        for(double x:value) if(!std::isfinite(x)) throw std::runtime_error("Nonfinite FLOW sample.");
        value[9]=owner(result,mapping,source,value[9]); result.samples.push_back(value);
    }
}
static void paths(Guides& result,const AFGuideInput& row,uint64_t cancel) {
    const auto start=int64_t(result.points.size()/3);
    for(int64_t i=0;i<row.point_count;++i) {
        if(i%4096==0) check_cancel(cancel);
        const V3 p(row.points+3*i);
        if(!p.allFinite()) throw std::runtime_error("Nonfinite FLOW path.");
        result.points.insert(result.points.end(),p.data(),p.data()+3);
    }
    for(int64_t i=1;i<=row.path_count;++i) result.offsets.push_back(start+row.offsets[i]);
}
Guides merge(const AFGuideInput* inputs,int count,uint64_t cancel) {
    if(count<0||count>1000000||(count&&!inputs)) throw std::runtime_error("Invalid FLOW source count.");
    Guides result; check_cancel(cancel);
    for(int i=0;i<count;++i) {
        check_cancel(cancel); validate(inputs[i],cancel);
        if(result.samples.size()+inputs[i].sample_count>16777216||result.points.size()/3+inputs[i].point_count>16777216)
            throw std::runtime_error("FLOW batch exceeds storage budget.");
        samples(result,inputs[i],i,cancel); paths(result,inputs[i],cancel);
    }
    return result;
}
}
