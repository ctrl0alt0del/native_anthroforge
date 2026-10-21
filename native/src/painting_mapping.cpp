#include "painting_internal.hpp"
namespace af::painting {
static void validate(binding::Weights& row,int count) {
    double sum=0;
    for(auto& [index,weight]:row) {
        if(index<0||index>=count||!std::isfinite(weight)||weight<-1e-8) throw std::runtime_error("Invalid field correspondence.");
        weight=std::max(0.0,weight);
        sum+=weight;
    }
    if(std::abs(sum-1)>1e-7) throw std::runtime_error("Incomplete field correspondence.");
    for(auto& [index,weight]:row) weight/=sum;
}
Mapping correspondence(const Mesh& target,const Mesh* reference,bool source,int count,uint64_t cancel) {
    if(count<1||(source&&target.tissue.source_count!=count)||(!source&&(!reference||reference->vertices.rows()!=count)))
        throw std::runtime_error("Field domain does not match the displayed tissue. Reevaluate before painting.");
    Mapping rows(size_t(target.vertices.rows()));
    const bool direct=!source&&inspection::canonical(target,*reference);
    std::unique_ptr<binding::Index> index;
    if(!source&&!direct) index=std::make_unique<binding::Index>(binding::index(*reference,cancel));
    for(int64_t i=0;i<target.vertices.rows();++i) {
        check_cancel(cancel); auto& row=rows[size_t(i)];
        row=direct?binding::Weights{{i,1}}:binding::weights(target.tissue,i);
        if(index) row=binding::material_coordinates(*index,row,target.tissue.sides[size_t(i)],cancel);
        validate(row,count);
    }
    return rows;
}
}
