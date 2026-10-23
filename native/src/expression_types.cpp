// SPDX-License-Identifier: GPL-3.0-or-later
#include "expression_internal.hpp"
#include <stdexcept>

namespace af::expression {
bool compatible(Type a,Type b) { return a.zero||b.zero||(a.length==b.length&&a.angle==b.angle); }
static bool scalar(Type type) { return !type.length&&!type.angle; }
static void require(bool valid,const char* message) { if(!valid) throw std::runtime_error(message); }
static Type common(Type a,Type b) {
    require(compatible(a,b),"Incompatible physical dimensions.");
    Type result=a.zero?b:a;
    result.kind=a.kind==Kind::Integer&&b.kind==Kind::Integer?Kind::Integer:Kind::Real;
    result.zero=a.zero&&b.zero; return result;
}
static Type product(Op op,Type a,Type b) {
    const int sign=op==Op::Divide?-1:1;
    Type result{a.kind==Kind::Integer&&b.kind==Kind::Integer?Kind::Integer:Kind::Real,
                a.length+sign*b.length,a.angle+sign*b.angle,a.zero||(op==Op::Multiply&&b.zero)};
    if(op==Op::Divide) result.kind=Kind::Real;
    require(result.length>=-16&&result.length<=16&&result.angle>=-16&&result.angle<=16,"Dimension exponent exceeds supported bounds.");
    return result;
}
static Type power(const std::vector<Node>& args) {
    const Type a=args[0].type,b=args[1].type;
    const bool constant=args[1].constant&&b.kind==Kind::Integer;
    require(scalar(b),"A power exponent must be dimensionless.");
    require(scalar(a)||constant,"Dimensioned powers require a constant integer exponent.");
    const int64_t exponent=constant?args[1].value.integer:0;
    require(scalar(a)||(exponent>=-16&&exponent<=16&&std::abs(a.length*exponent)<=16&&std::abs(a.angle*exponent)<=16),"Dimension exponent exceeds supported bounds.");
    const bool integral=a.kind==Kind::Integer&&constant&&exponent>=0;
    return {integral?Kind::Integer:Kind::Real,int(a.length*exponent),int(a.angle*exponent),false};
}
static Type unary(Op op,Type value) {
    if(op==Op::Negate||op==Op::Abs) return value;
    if(op==Op::Floor||op==Op::Ceil||op==Op::Round) { value.kind=Kind::Integer; return value; }
    if(op==Op::Sqrt) {
        require(value.length%2==0&&value.angle%2==0,"Square root requires even dimension exponents.");
        return {Kind::Real,value.length/2,value.angle/2,value.zero};
    }
    if(op==Op::Sin||op==Op::Cos||op==Op::Tan)
        require(scalar(value)||(!value.length&&value.angle==1),"Trigonometry requires an angle or dimensionless argument.");
    else require(scalar(value),"This function requires a dimensionless argument.");
    return {Kind::Real,0,(op==Op::Asin||op==Op::Acos||op==Op::Atan)?1:0,false};
}
Type result_type(Op op,const std::vector<Node>& args) {
    if(args.size()==1) return unary(op,args[0].type);
    const Type a=args[0].type,b=args[1].type;
    if(op==Op::Multiply||op==Op::Divide) return product(op,a,b);
    if(op==Op::Power) return power(args);
    const Type result=common(a,b);
    if(op>=Op::Less&&op<=Op::NotEqual) return {Kind::Integer,0,0,false};
    if(op==Op::Atan2) return {Kind::Real,0,1,false};
    if(op==Op::Clamp) return common(result,args[2].type);
    return result;
}
}
