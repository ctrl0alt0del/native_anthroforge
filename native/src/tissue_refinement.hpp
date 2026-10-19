// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "tissue_branches.hpp"

namespace af::tissue {
std::vector<double> refine_axis(const std::vector<double>& source,int resolution,bool closed);
V3 material_sample(const Mesh& source,const MaterialGrid& grid,double row,double column);
std::shared_ptr<Mesh> refine_parts(const Mesh& source,const std::vector<MaterialGrid>& grids,int resolution,uint64_t cancel);
}
