// SPDX-License-Identifier: GPL-3.0-or-later
#include "expression_internal.hpp"
#include <stdexcept>

namespace af { void check_cancel(uint64_t token); }
namespace af::expression {
Value evaluate(const Program& program,const Value* values,uint64_t cancel) {
    check_cancel(cancel);
    std::vector<Value> stack; stack.reserve(program.code.size());
    for(const auto& instruction:program.code) {
        if(instruction.op==Op::Constant) stack.push_back(instruction.constant);
        else if(instruction.op==Op::Variable) stack.push_back(checked(values[instruction.index]));
        else {
            const size_t position=stack.size()-size_t(instruction.arity);
            const Value result=operate(instruction,stack.data()+position);
            stack.resize(position); stack.push_back(result);
        }
    }
    return stack.back();
}
}
