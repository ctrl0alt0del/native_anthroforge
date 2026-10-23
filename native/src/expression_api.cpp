// SPDX-License-Identifier: GPL-3.0-or-later
#include "expression_internal.hpp"
#include "anthroforge/expressions.h"
#include <algorithm>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <unordered_map>

namespace af { void check_cancel(uint64_t token); void set_error(const std::string& message); }
namespace af::expression {
static std::mutex mutex;
static std::unordered_map<uint64_t,std::shared_ptr<const Program>> programs;
static uint64_t next_handle=1;
std::shared_ptr<const Program> program(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex);
    const auto found=programs.find(handle);
    if(found==programs.end()) throw std::runtime_error("Unknown compiled expression.");
    return found->second;
}
uint64_t retain(std::shared_ptr<const Program> value) {
    std::lock_guard<std::mutex> lock(mutex);
    const uint64_t handle=next_handle++; programs.emplace(handle,std::move(value)); return handle;
}
void release(uint64_t handle) { std::lock_guard<std::mutex> lock(mutex); programs.erase(handle); }
uint64_t bytes(const Program& value) {
    uint64_t total=sizeof(Program)+value.source.capacity()+value.code.capacity()*sizeof(Instruction);
    for(const auto& symbol:value.symbols) total+=sizeof(Symbol)+symbol.name.capacity();
    return total;
}
static std::vector<Symbol> symbols(const char* names,const int* types,int count) {
    if(!names||count<0||count>256||(!types&&count)) throw std::runtime_error("Invalid expression inputs.");
    std::istringstream stream(names); std::vector<Symbol> result;
    for(int index=0;index<count;++index) {
        std::string name;
        if(!std::getline(stream,name)||types[3*index]<0||types[3*index]>1||
           types[3*index+1]<-16||types[3*index+1]>16||types[3*index+2]<-16||types[3*index+2]>16)
            throw std::runtime_error("Invalid expression input declaration.");
        result.push_back({name,{Kind(types[3*index]),types[3*index+1],types[3*index+2],false}});
    }
    std::string extra;
    if(std::getline(stream,extra)) throw std::runtime_error("Too many expression input names.");
    return result;
}
static std::vector<Value> frame(const Program& program,const int64_t* integers,const double* reals) {
    std::vector<Value> result; result.reserve(program.symbols.size());
    for(size_t i=0;i<program.symbols.size();++i) result.push_back(checked({program.symbols[i].type,integers[i],reals[i]}));
    return result;
}
static void evaluate_rows(const Program& program,const int64_t* integers,const double* reals,
                          int rows,int64_t* output_integer,double* output_real,uint64_t cancel) {
    const size_t count=program.symbols.size();
    if(rows<1||rows>1000000||(!integers&&count)||(!reals&&count)||!output_integer||!output_real)
        throw std::runtime_error("Invalid expression frame buffers.");
    for(int row=0;row<rows;++row) {
        check_cancel(cancel);
        const auto values=frame(program,integers+size_t(row)*count,reals+size_t(row)*count);
        const auto result=evaluate(program,values.data(),cancel);
        output_integer[row]=result.integer; output_real[row]=result.real;
    }
}
}
uint64_t af_expression_compile(const char* source,const char* names,const int* types,int count,uint64_t cancel) {
    try {
        af::check_cancel(cancel);
        if(!source) throw std::runtime_error("Missing expression source.");
        return af::expression::retain(af::expression::compile(source,af::expression::symbols(names,types,count)));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
int af_expression_info(uint64_t handle,int* type,uint64_t* bytes) {
    try {
        if(!type||!bytes) throw std::runtime_error("Expression information requires output buffers.");
        const auto value=af::expression::program(handle);
        type[0]=int(value->output.kind); type[1]=value->output.length; type[2]=value->output.angle;
        type[3]=value->output.zero; *bytes=af::expression::bytes(*value); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_expression_evaluate(uint64_t handle,const int64_t* integers,const double* reals,int rows,
                           int64_t* output_integer,double* output_real,uint64_t cancel) {
    try {
        const auto value=af::expression::program(handle);
        af::expression::evaluate_rows(*value,integers,reals,rows,output_integer,output_real,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
void af_expression_release(uint64_t handle) { af::expression::release(handle); }
