// SPDX-License-Identifier: GPL-3.0-or-later
#include "expression_internal.hpp"
#include <algorithm>
#include <cmath>
#include <cctype>
#include <map>
#include <stdexcept>

namespace af::expression {
static const std::map<std::string,std::pair<Op,int>> operators={
    {"<",{Op::Less,1}},{"<=",{Op::LessEqual,1}},{">",{Op::Greater,1}},{">=",{Op::GreaterEqual,1}},
    {"==",{Op::Equal,1}},{"!=",{Op::NotEqual,1}},{"+",{Op::Add,2}},{"-",{Op::Subtract,2}},
    {"*",{Op::Multiply,3}},{"/",{Op::Divide,3}},{"%",{Op::Remainder,3}},
    {"^",{Op::Power,5}},{"**",{Op::Power,5}}};
static const std::map<std::string,std::pair<Op,int>> functions={
    {"sin",{Op::Sin,1}},{"cos",{Op::Cos,1}},{"tan",{Op::Tan,1}},
    {"asin",{Op::Asin,1}},{"acos",{Op::Acos,1}},{"atan",{Op::Atan,1}},{"atan2",{Op::Atan2,2}},
    {"sqrt",{Op::Sqrt,1}},{"abs",{Op::Abs,1}},{"exp",{Op::Exp,1}},{"log",{Op::Log,1}},
    {"log10",{Op::Log10,1}},{"floor",{Op::Floor,1}},{"ceil",{Op::Ceil,1}},{"round",{Op::Round,1}},
    {"min",{Op::Min,2}},{"max",{Op::Max,2}},{"clamp",{Op::Clamp,3}},{"pow",{Op::Power,2}}};
class Parser {
    Program value;
    std::vector<Token> tokens;
    size_t cursor=0;
    Node constant(Value input);
    Node identifier(const Token& token,int depth);
    Node function(const Token& token,int depth);
    Node prefix(int depth);
    Node expression(int precedence,int depth);
    Node append(Op op,const std::vector<Node>& args);
    void expect(const char* text);
public:
    Parser(const std::string& source,const std::vector<Symbol>& symbols):value{source,symbols,{},{}},tokens(tokenize(source)) {}
    std::shared_ptr<const Program> parse();
};
void Parser::expect(const char* text) {
    if(tokens[cursor].text!=text) throw std::runtime_error(std::string("Expected '")+text+"' at column "+std::to_string(tokens[cursor].position+1));
    ++cursor;
}
Node Parser::constant(Value input) {
    value.code.push_back({Op::Constant,input.type,0,0,input});
    return {input.type,true,input};
}
Node Parser::append(Op op,const std::vector<Node>& args) {
    const Type type=result_type(op,args);
    value.code.push_back({op,type,int(args.size()),0,{}});
    const bool constant=std::all_of(args.begin(),args.end(),[](const Node& node){return node.constant;});
    std::vector<Value> values;
    if(constant) for(const auto& node:args) values.push_back(node.value);
    return {type,constant,constant?operate(value.code.back(),values.data()):Value{}};
}
Node Parser::function(const Token& token,int depth) {
    const auto found=functions.find(token.text);
    if(found==functions.end()) throw std::runtime_error("Unknown or forbidden function: "+token.text);
    expect("("); std::vector<Node> args;
    if(tokens[cursor].text!=")") do {
        if(args.size()==3) throw std::runtime_error("Too many function arguments.");
        args.push_back(expression(0,depth+1));
        if(tokens[cursor].text!=",") break;
        ++cursor;
    } while(true);
    expect(")");
    if(int(args.size())!=found->second.second) throw std::runtime_error("Wrong argument count for "+token.text);
    return append(found->second.first,args);
}
Node Parser::identifier(const Token& token,int depth) {
    if(tokens[cursor].text=="(") return function(token,depth);
    if(token.text=="pi") return constant({{Kind::Real,0,0,false},0,std::acos(-1.)});
    if(token.text=="e") return constant({{Kind::Real,0,0,false},0,std::exp(1.)});
    if(token.text=="m") return constant({{Kind::Real,1,0,false},0,1.});
    if(token.text=="rad") return constant({{Kind::Real,0,1,false},0,1.});
    for(size_t i=0;i<value.symbols.size();++i) if(value.symbols[i].name==token.text) {
        value.code.push_back({Op::Variable,value.symbols[i].type,0,int(i),{}});
        return {value.symbols[i].type,false,{}};
    }
    throw std::runtime_error("Unknown expression input: "+token.text);
}
Node Parser::prefix(int depth) {
    if(depth>64) throw std::runtime_error("Expression nesting exceeds 64 levels.");
    const Token token=tokens[cursor++];
    if(token.text=="+"||token.text=="-") {
        const Node node=expression(4,depth+1);
        return token.text=="-"?append(Op::Negate,{node}):node;
    }
    if(token.text=="(") { const Node node=expression(0,depth+1); expect(")"); return node; }
    if(token.text.empty()) throw std::runtime_error("Unexpected end of expression.");
    if(token.text[0]=='.'||(token.text[0]>='0'&&token.text[0]<='9')) return constant(literal(token));
    return identifier(token,depth);
}
Node Parser::expression(int precedence,int depth) {
    Node left=prefix(depth);
    while(cursor<tokens.size()) {
        const auto found=operators.find(tokens[cursor].text);
        if(found==operators.end()||found->second.second<precedence) break;
        const auto [op,level]=found->second; ++cursor;
        const Node right=expression(level+(op==Op::Power?0:1),depth+1);
        left=append(op,{left,right});
    }
    return left;
}
std::shared_ptr<const Program> Parser::parse() {
    value.output=expression(0,0).type;
    if(cursor!=tokens.size()-1) throw std::runtime_error("Unexpected expression suffix at column "+std::to_string(tokens[cursor].position+1));
    return std::make_shared<const Program>(std::move(value));
}
static void validate_symbols(const std::vector<Symbol>& symbols) {
    if(symbols.size()>256) throw std::runtime_error("Expressions support at most 256 inputs.");
    std::map<std::string,int> names;
    for(const auto& symbol:symbols) {
        const auto tokens=tokenize(symbol.name);
        if(tokens.size()!=2||tokens[0].text.empty()||!std::isalpha(static_cast<unsigned char>(tokens[0].text[0]))||
           functions.count(symbol.name)||
           symbol.name=="pi"||symbol.name=="e"||symbol.name=="m"||symbol.name=="rad"||!names.emplace(symbol.name,0).second)
            throw std::runtime_error("Invalid, reserved or duplicate expression input: "+symbol.name);
    }
}
std::shared_ptr<const Program> compile(const std::string& source,const std::vector<Symbol>& symbols) {
    validate_symbols(symbols); return Parser(source,symbols).parse();
}
}
