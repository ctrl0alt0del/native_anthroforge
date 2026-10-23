// SPDX-License-Identifier: GPL-3.0-or-later
#include "expression_internal.hpp"
#include <charconv>
#include <cctype>
#include <cmath>
#include <stdexcept>

namespace af::expression {
static bool digit(char ch) { return ch>='0'&&ch<='9'; }
static bool alpha(char ch) { return (ch>='a'&&ch<='z')||(ch>='A'&&ch<='Z')||ch=='_'; }
static size_t number_end(const std::string& source,size_t start) {
    size_t end=start;
    while(end<source.size()&&digit(source[end])) ++end;
    if(end<source.size()&&source[end]=='.') {
        ++end; while(end<source.size()&&digit(source[end])) ++end;
    }
    if(end<source.size()&&(source[end]=='e'||source[end]=='E')) {
        ++end;
        if(end<source.size()&&(source[end]=='+'||source[end]=='-')) ++end;
        const auto digits=end; while(end<source.size()&&digit(source[end])) ++end;
        if(end==digits) throw std::runtime_error("Exponent requires digits.");
    }
    return end;
}
static Token next(const std::string& source,size_t& position) {
    const size_t start=position;
    if(digit(source[position])||source[position]=='.') position=number_end(source,position);
    else if(alpha(source[position])) {
        while(position<source.size()&&(alpha(source[position])||digit(source[position]))) ++position;
    } else {
        ++position;
        const std::string pair=source.substr(start,2);
        if(pair=="<="||pair==">="||pair=="=="||pair=="!="||pair=="**") ++position;
        else if(std::string("+-*/%^<>() ,").find(source[start])==std::string::npos)
            throw std::runtime_error("Unsupported expression token at column "+std::to_string(start+1));
    }
    return {source.substr(start,position-start),start};
}
std::vector<Token> tokenize(const std::string& source) {
    if(source.empty()||source.size()>8192) throw std::runtime_error("Expression requires 1..8192 bytes.");
    std::vector<Token> tokens;
    for(size_t position=0;position<source.size();) {
        const auto ch=static_cast<unsigned char>(source[position]);
        if(ch>=128) throw std::runtime_error("Expressions use ASCII identifiers and operators.");
        if(std::isspace(ch)) { ++position; continue; }
        tokens.push_back(next(source,position));
        if(tokens.size()>4096) throw std::runtime_error("Expression exceeds 4096 tokens.");
    }
    tokens.push_back({"",source.size()}); return tokens;
}
Value literal(const Token& token) {
    Value value;
    const char* start=token.text.data(); const char* end=start+token.text.size();
    if(token.text.find_first_of(".eE")==std::string::npos) {
        value.type.kind=Kind::Integer;
        const auto parsed=std::from_chars(start,end,value.integer);
        if(parsed.ec!=std::errc()||parsed.ptr!=end) throw std::runtime_error("Invalid or overflowing integer literal.");
        value.type.zero=value.integer==0;
    } else {
        const auto parsed=std::from_chars(start,end,value.real);
        if(parsed.ec!=std::errc()||parsed.ptr!=end||!std::isfinite(value.real)) throw std::runtime_error("Invalid real literal.");
        value.type.zero=value.real==0;
    }
    return value;
}
}
