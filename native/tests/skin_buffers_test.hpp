#pragma once
#include "skin_assembly.hpp"
#include "skin_fields.hpp"
#include <stdexcept>

inline void require_skin(bool value) {
    if(!value) throw std::runtime_error("Skin buffer contract failed.");
}
void test_skin_assembly();
void test_skin_fields();
