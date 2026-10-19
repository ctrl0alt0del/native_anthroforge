#pragma once
#include "material_domain.hpp"
#include "anthroforge/material_pins.h"
#include <map>

namespace af {
constexpr size_t material_pin_width=11;
using MaterialEquation=std::map<int64_t,double>;
MaterialEquation material_equation(const Mesh& mesh,const std::vector<MaterialGrid>& grids,const double* pin);
std::vector<double> material_capture(const Mesh& mesh,const AfSurfacePins& inputs,uint64_t cancel);
}
