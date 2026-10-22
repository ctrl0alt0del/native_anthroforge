// SPDX-License-Identifier: GPL-3.0-or-later
#include "expression_internal.hpp"
#include "path_internal.hpp"
#include <array>

namespace af {
namespace ex=expression;
using Equations=std::array<std::shared_ptr<const ex::Program>,3>;
static Equations equations(const uint64_t* handles) {
    if(!handles) throw std::runtime_error("Missing parametric equations.");
    Equations result{ex::program(handles[0]),ex::program(handles[1]),ex::program(handles[2])};
    for(const auto& program:result) {
        const auto type=program->output;
        if(!type.zero&&(type.length!=1||type.angle!=0))
            throw std::runtime_error("XYZ expressions must produce lengths in metres.");
        if(program->symbols.empty()||program->symbols[0].name!="t")
            throw std::runtime_error("Parametric equations require t as their first input.");
    }
    return result;
}
static void require_symbols(const Equations& programs,int count) {
    for(const auto& program:programs) {
        if(program->symbols.size()!=size_t(count)||count<1||count>256)
            throw std::runtime_error("Parametric equation inputs disagree.");
        for(int i=0;i<count;++i) {
            const auto& a=program->symbols[i]; const auto& b=programs[0]->symbols[i];
            if(a.name!=b.name||a.type.kind!=b.type.kind||a.type.length!=b.type.length||a.type.angle!=b.type.angle)
                throw std::runtime_error("Parametric equation input declarations disagree.");
        }
    }
    const auto type=programs[0]->symbols[0].type;
    if(type.kind!=ex::Kind::Real||type.length||type.angle)
        throw std::runtime_error("Parameter t must be a real dimensionless value.");
}
static std::vector<ex::Value> inputs(const Equations& programs,int count,const int64_t* integers,const double* reals) {
    require_symbols(programs,count);
    if(!integers||!reals) throw std::runtime_error("Missing parametric input values.");
    std::vector<ex::Value> result;
    for(int i=0;i<count;++i) result.push_back(ex::checked({programs[0]->symbols[i].type,integers[i],reals[i]}));
    return result;
}
static void point_record(const Equations& programs,std::vector<ex::Value>& values,
                         const double* metadata,int previous,int index,double t,double* output,uint64_t cancel) {
    values[0].real=t;
    for(int axis=0;axis<3;++axis) {
        const double value=ex::real(ex::evaluate(*programs[axis],values.data(),cancel));
        output[axis]=output[axis+3]=output[axis+6]=value;
    }
    output[9]=index<previous?metadata[index*13+9]:1;
    output[10]=index<previous?metadata[index*13+10]:0;
    output[11]=output[12]=3;
}
static void sample_equations(const Equations& programs,std::vector<ex::Value>& values,
                             const double* metadata,int previous,int count,bool closed,
                             double start,double end,double* records,uint64_t cancel) {
    if(!records||(!metadata&&previous)||previous<0||count<(closed?3:2)||count>1000000)
        throw std::runtime_error("Invalid parametric point buffers or resolution.");
    if(!std::isfinite(start)||!std::isfinite(end)||start==end||!std::isfinite(end-start))
        throw std::runtime_error("Parameter interval must have finite, distinct endpoints.");
    for(int i=0;i<count;++i) {
        check_cancel(cancel);
        const double t=start+(end-start)*(double(i)/(count-int(!closed)));
        point_record(programs,values,metadata,previous,i,t,records+13*i,cancel);
    }
}
}
uint64_t af_parametric_path(const uint64_t* handles,int variables,const int64_t* integers,const double* reals,
                            const double* metadata,int previous,int count,int closed,double start,double end,
                            double* records,uint64_t cancel) {
    try {
        const auto programs=af::equations(handles);
        auto values=af::inputs(programs,variables,integers,reals);
        af::sample_equations(programs,values,metadata,previous,count,closed!=0,start,end,records,cancel);
        const auto samples=af::authored_path(records,count,1,closed!=0,1,cancel);
        return af::retain_path(af::make_path(samples,closed!=0,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
