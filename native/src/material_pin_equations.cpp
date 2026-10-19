// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_pins.hpp"

namespace af {
struct PinInterval { int a,b; double weight; };
static PinInterval interval(const std::vector<double>& axis,double value,bool closed) {
    if(!std::isfinite(value)||value<0||value>1) throw std::runtime_error("Invalid retained material pin coordinate.");
    const int a=std::max(0,int(std::upper_bound(axis.begin(),axis.end(),value)-axis.begin())-1);
    const int b=closed?(a+1)%int(axis.size()):std::min(a+1,int(axis.size())-1);
    const double end=b==0?1:axis[size_t(b)];
    return {a,b,a==b?0:(value-axis[size_t(a)])/(end-axis[size_t(a)])};
}
static MaterialEquation grid_equation(const MaterialGrid& grid,const double* pin) {
    const auto u=interval(grid.across,pin[1],grid.closed_v),v=interval(grid.along,pin[2],grid.closed_u);
    MaterialEquation result;
    result[grid.indices[size_t(u.a*grid.columns+v.a)]]+=(1-u.weight)*(1-v.weight);
    result[grid.indices[size_t(u.a*grid.columns+v.b)]]+=(1-u.weight)*v.weight;
    result[grid.indices[size_t(u.b*grid.columns+v.a)]]+=u.weight*(1-v.weight);
    result[grid.indices[size_t(u.b*grid.columns+v.b)]]+=u.weight*v.weight;
    return result;
}
static MaterialEquation vertex_equation(const Mesh& mesh,const double* pin) {
    MaterialEquation result; double total=0;
    for(int i=0;i<4;++i) {
        const double index=pin[3+i],weight=pin[7+i];
        if(!std::isfinite(index)||index!=std::floor(index)||index<0||index>=mesh.vertices.rows()||!std::isfinite(weight)||weight<0)
            throw std::runtime_error("Invalid retained material pin weights.");
        if(weight) result[int64_t(index)]+=weight;
        total+=weight;
    }
    if(std::abs(total-1)>1e-10) throw std::runtime_error("Retained material pin weights must sum to one.");
    return result;
}
MaterialEquation material_equation(const Mesh& mesh,const std::vector<MaterialGrid>& grids,const double* pin) {
    const double part=pin[0];
    if(!std::isfinite(part)||part!=std::floor(part)||part<-1) throw std::runtime_error("Invalid retained material pin part.");
    if(part==-1) return vertex_equation(mesh,pin);
    if(part>=double(grids.size())) throw std::runtime_error("Retained structural pin references a missing material part.");
    return grid_equation(grids[size_t(part)],pin);
}
}
