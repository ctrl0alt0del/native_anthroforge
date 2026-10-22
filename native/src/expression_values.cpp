// SPDX-License-Identifier: GPL-3.0-or-later
#include "expression_internal.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

namespace af::expression {
double real(const Value& value) { return value.type.kind==Kind::Integer?double(value.integer):value.real; }
Value checked(Value value) {
    if(value.type.kind==Kind::Real&&!std::isfinite(value.real)) throw std::runtime_error("Expression produced a non-finite result.");
    return value;
}
static int64_t add(int64_t a,int64_t b) {
    if((b>0&&a>INT64_MAX-b)||(b<0&&a<INT64_MIN-b)) throw std::runtime_error("Integer addition overflow.");
    return a+b;
}
static int64_t subtract(int64_t a,int64_t b) {
    if((b<0&&a>INT64_MAX+b)||(b>0&&a<INT64_MIN+b)) throw std::runtime_error("Integer subtraction overflow.");
    return a-b;
}
static int64_t multiply(int64_t a,int64_t b) {
    if(a>0? (b>0?a>INT64_MAX/b:b<INT64_MIN/a) :
       (a<0&&(b>0?a<INT64_MIN/b:(b<0&&a<INT64_MAX/b))))
        throw std::runtime_error("Integer multiplication overflow.");
    return a*b;
}
static int64_t power(int64_t base,int64_t exponent) {
    int64_t result=1;
    while(exponent>0) {
        if(exponent%2) result=multiply(result,base);
        exponent/=2;
        if(exponent) base=multiply(base,base);
    }
    return result;
}
static int64_t integer_binary(Op op,int64_t a,int64_t b) {
    switch(op) {
    case Op::Add:return add(a,b);
    case Op::Subtract:return subtract(a,b);
    case Op::Multiply:return multiply(a,b);
    case Op::Power:return power(a,b);
    case Op::Remainder:
        if(b==0||(a==INT64_MIN&&b==-1)) throw std::runtime_error("Invalid integer remainder.");
        return a%b;
    case Op::Min:return std::min(a,b);
    case Op::Max:return std::max(a,b);
    default:throw std::runtime_error("Invalid integer operation.");
    }
}
static double real_binary(Op op,double a,double b) {
    switch(op) {
    case Op::Add:return a+b;
    case Op::Subtract:return a-b;
    case Op::Multiply:return a*b;
    case Op::Divide:return a/b;
    case Op::Power:return std::pow(a,b);
    case Op::Remainder:return std::fmod(a,b);
    case Op::Min:return std::min(a,b);
    case Op::Max:return std::max(a,b);
    case Op::Atan2:return std::atan2(a,b);
    default:throw std::runtime_error("Invalid real operation.");
    }
}
template<class T> static bool comparison(Op op,T a,T b) {
    switch(op) {
    case Op::Less:return a<b;
    case Op::LessEqual:return a<=b;
    case Op::Greater:return a>b;
    case Op::GreaterEqual:return a>=b;
    case Op::Equal:return a==b;
    case Op::NotEqual:return a!=b;
    default:throw std::runtime_error("Invalid comparison.");
    }
}
static double trigonometry(Op op,double value) {
    switch(op) {
    case Op::Sin:return std::sin(value);
    case Op::Cos:return std::cos(value);
    case Op::Tan:return std::tan(value);
    case Op::Asin:return std::asin(value);
    case Op::Acos:return std::acos(value);
    case Op::Atan:return std::atan(value);
    default:throw std::runtime_error("Invalid trigonometric function.");
    }
}
static double real_unary(Op op,double value) {
    switch(op) {
    case Op::Negate:return -value;
    case Op::Abs:return std::abs(value);
    case Op::Sqrt:return std::sqrt(value);
    case Op::Exp:return std::exp(value);
    case Op::Log:return std::log(value);
    case Op::Log10:return std::log10(value);
    case Op::Floor:return std::floor(value);
    case Op::Ceil:return std::ceil(value);
    case Op::Round:return std::round(value);
    default:return trigonometry(op,value);
    }
}
static int64_t converted_integer(double value) {
    if(!std::isfinite(value)||value<double(INT64_MIN)||value>=-double(INT64_MIN))
        throw std::runtime_error("Integer conversion exceeds signed 64-bit range.");
    return int64_t(value);
}
static Value unary_value(const Instruction& instruction,Value value) {
    Value result{instruction.type,0,0};
    if(value.type.kind==Kind::Integer&&instruction.type.kind==Kind::Integer) {
        result.integer=value.integer;
        if(instruction.op==Op::Negate||(instruction.op==Op::Abs&&value.integer<0))
            result.integer=subtract(0,value.integer);
    } else {
        const double evaluated=real_unary(instruction.op,real(value));
        if(result.type.kind==Kind::Integer) result.integer=converted_integer(evaluated);
        else result.real=evaluated;
    }
    return checked(result);
}
static Value binary_value(const Instruction& instruction,const Value* args) {
    Value result{instruction.type,0,0};
    if(instruction.op>=Op::Less&&instruction.op<=Op::NotEqual)
        result.integer=args[0].type.kind==Kind::Integer&&args[1].type.kind==Kind::Integer?
            comparison(instruction.op,args[0].integer,args[1].integer):comparison(instruction.op,real(args[0]),real(args[1]));
    else if(result.type.kind==Kind::Integer)
        result.integer=integer_binary(instruction.op,args[0].integer,args[1].integer);
    else result.real=real_binary(instruction.op,real(args[0]),real(args[1]));
    return checked(result);
}
Value operate(const Instruction& instruction,const Value* args) {
    if(instruction.arity==1) return unary_value(instruction,args[0]);
    if(instruction.op!=Op::Clamp) return binary_value(instruction,args);
    const bool invalid=instruction.type.kind==Kind::Integer?args[1].integer>args[2].integer:real(args[1])>real(args[2]);
    if(invalid) throw std::runtime_error("Clamp minimum exceeds maximum.");
    Value result{instruction.type,0,0};
    if(result.type.kind==Kind::Integer) result.integer=std::clamp(args[0].integer,args[1].integer,args[2].integer);
    else result.real=std::clamp(real(args[0]),real(args[1]),real(args[2]));
    return checked(result);
}
}
