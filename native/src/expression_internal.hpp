// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace af::expression {
enum class Kind { Integer, Real };
struct Type {
    Kind kind=Kind::Real;
    int length=0,angle=0;
    bool zero=false;
};
struct Value { Type type; int64_t integer=0; double real=0; };
enum class Op {
    Constant,Variable,Negate,Add,Subtract,Multiply,Divide,Power,Remainder,
    Less,LessEqual,Greater,GreaterEqual,Equal,NotEqual,
    Sin,Cos,Tan,Asin,Acos,Atan,Atan2,Sqrt,Abs,Exp,Log,Log10,Floor,Ceil,Round,Min,Max,Clamp
};
struct Symbol { std::string name; Type type; };
struct Instruction { Op op; Type type; int arity=0,index=0; Value constant; };
struct Program {
    std::string source;
    std::vector<Symbol> symbols;
    std::vector<Instruction> code;
    Type output;
};
struct Node { Type type; bool constant=false; Value value; };
struct Token { std::string text; size_t position=0; };
std::vector<Token> tokenize(const std::string& source);
Value literal(const Token& token);
Type result_type(Op op,const std::vector<Node>& args);
bool compatible(Type first,Type second);
double real(const Value& value);
Value checked(Value value);
Value operate(const Instruction& instruction,const Value* args);
std::shared_ptr<const Program> compile(const std::string& source,const std::vector<Symbol>& symbols);
Value evaluate(const Program& program,const Value* values,uint64_t cancel);
std::shared_ptr<const Program> program(uint64_t handle);
uint64_t retain(std::shared_ptr<const Program> value);
void release(uint64_t handle);
uint64_t bytes(const Program& value);
}
