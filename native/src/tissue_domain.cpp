// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_domain.hpp"
#include <numeric>
#include <stdexcept>
#include <cmath>

namespace af {
uint64_t tissue_storage(const TissueDomain& d) {
    return (d.offsets.capacity()+d.indices.capacity()+d.sides.capacity()+d.parts.capacity()+d.faces.capacity())*sizeof(int64_t)
        +d.weights.capacity()*sizeof(double);
}
TissueDomain tissue_identity(int64_t kind,int64_t count,int64_t faces,int64_t copies) {
    TissueDomain result; result.kind=kind; result.source_count=count;
    const size_t n=size_t(count*copies);
    result.offsets.resize(n+1); std::iota(result.offsets.begin(),result.offsets.end(),0);
    result.weights.resize(n,1); result.indices.resize(n); result.sides.resize(n);
    for(size_t i=0;i<n;++i) { result.indices[i]=int64_t(i)%count; result.sides[i]=1+int64_t(i)/count; }
    result.parts.resize(size_t(faces),0); result.faces.resize(size_t(faces));
    std::iota(result.faces.begin(),result.faces.end(),0);
    return result;
}
std::vector<int64_t> tissue_records(const TissueDomain& d) {
    if(!d.kind) return {};
    std::vector<int64_t> data{1,d.kind,d.source_count,d.ring_size,d.closed,int64_t(d.sides.size()),int64_t(d.parts.size()),int64_t(d.indices.size())};
    for(const auto* values:{&d.offsets,&d.indices,&d.sides,&d.parts,&d.faces})
        data.insert(data.end(),values->begin(),values->end());
    return data;
}
static void row(const TissueDomain& d,size_t i) {
    const auto start=d.offsets[i],end=d.offsets[i+1];
    if(start<0||end<=start||end>int64_t(d.indices.size())) throw std::runtime_error("Invalid tissue material row.");
    double total=0;
    for(auto j=start;j<end;++j) {
        const auto index=d.indices[size_t(j)]; const double weight=d.weights[size_t(j)];
        if(index<0||index>=d.source_count||!std::isfinite(weight)||weight<0) throw std::runtime_error("Invalid tissue correspondence.");
        total+=weight;
    }
    if(std::abs(total-1)>1e-10||d.sides[i]<0||d.sides[i]>2) throw std::runtime_error("Invalid tissue material weights or side.");
}
void tissue_validate(const TissueDomain& d,int64_t vertices,int64_t faces) {
    if(!d.kind) return;
    if(d.kind<1||d.kind>5||d.source_count<1||d.source_count>262144||d.ring_size<0||d.closed<0||d.closed>1)
        throw std::runtime_error("Invalid tissue domain header.");
    if(d.offsets.size()!=size_t(vertices+1)||d.sides.size()!=size_t(vertices)||d.parts.size()!=size_t(faces)||d.faces.size()!=size_t(faces))
        throw std::runtime_error("Tissue correspondence does not match mesh topology.");
    if(d.weights.size()!=d.indices.size()||d.offsets.front()!=0||d.offsets.back()!=int64_t(d.indices.size()))
        throw std::runtime_error("Invalid tissue material buffers.");
    for(size_t i=0;i<d.sides.size();++i) row(d,i);
    for(size_t i=0;i<d.parts.size();++i) if(d.parts[i]<0||d.faces[i]<-1) throw std::runtime_error("Invalid tissue face labels.");
}
static std::vector<int64_t> take(const int64_t*& data,int64_t count) {
    const std::vector<int64_t> result(data,data+count); data+=count; return result;
}
TissueDomain tissue_restore(const int64_t* p,int64_t count,const double* weights,int64_t entries,int64_t vertices,int64_t faces) {
    if(!count&&!entries) return {};
    if(!p||!weights||count<8||entries<1||entries>8388608) throw std::runtime_error("Invalid tissue domain storage.");
    if(p[0]!=1||p[5]!=vertices||p[6]!=faces||p[7]!=entries||count!=9+2*vertices+2*faces+entries)
        throw std::runtime_error("Tissue domain storage dimensions disagree.");
    TissueDomain d; d.kind=p[1]; d.source_count=p[2]; d.ring_size=p[3]; d.closed=p[4]; p+=8;
    d.offsets=take(p,vertices+1); d.indices=take(p,entries); d.sides=take(p,vertices);
    d.parts=take(p,faces); d.faces=take(p,faces); d.weights.assign(weights,weights+entries);
    tissue_validate(d,vertices,faces); return d;
}
}
