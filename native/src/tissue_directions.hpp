// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "tissue_inflation.hpp"

namespace af::tissue {
Vertices inflation_directions(const Mesh& source,const MaterialGrid& grid,double distance,uint64_t cancel);
}
