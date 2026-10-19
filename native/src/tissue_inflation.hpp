#pragma once
#include "construction_internal.hpp"
#include "material_domain.hpp"
#include "anthroforge/tissue.h"

namespace af::tissue {
void validate_inflation(const AfTissueInflation& settings,const MaterialGrid& grid);
Points inflate_grid(const Mesh& source,const MaterialGrid& grid,const AfTissueInflation& settings,uint64_t cancel);
}
