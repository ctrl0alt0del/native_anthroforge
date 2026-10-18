// Batched evaluation of authored deformer membership and vertex-group influence.
#include "construction_internal.hpp"

namespace af {
static double influence_value(const double* weights,int index,int invert) {
    return weights?(invert?1-weights[index]:weights[index]):1;
}
static void initial_influence(const double* weights,int count,int invert,bool masked,double* output,uint64_t cancel) {
    for(int i=0;i<count;++i) {
        if(i%1024==0) check_cancel(cancel);
        output[i]=masked?0:influence_value(weights,i,invert);
    }
}
static void restricted_influence(const double* weights,int count,int invert,const int* indices,
                                 int index_count,double* output,uint64_t cancel) {
    for(int i=0;i<index_count;++i) {
        if(i%1024==0) check_cancel(cancel);
        const int index=indices[i];
        if(index<0) throw std::runtime_error("Influence indices must be nonnegative.");
        if(index<count) output[index]=influence_value(weights,index,invert);
    }
}
}
int af_influence(const double* weights,int count,int invert,const int* indices,
                 int index_count,int restricted,double* output,uint64_t cancel) {
    try {
        af::check_cancel(cancel);
        if(count<0||index_count<0||(!output&&count)||(!indices&&index_count))
            throw std::runtime_error("Invalid influence buffers.");
        const bool masked=restricted||index_count;
        af::initial_influence(weights,count,invert,masked,output,cancel);
        if(masked) af::restricted_influence(weights,count,invert,indices,index_count,output,cancel);
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
