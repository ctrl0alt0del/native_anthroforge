// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "mesh_internal.hpp"
#include "af_smoothing/height.h"

namespace af::tissue {
Vertices smooth_heights(const Vertices& base,const Vertices& own,const std::vector<int64_t>& faces,
                       const std::vector<int64_t>& labels,int part,const double* settings,AF_HeightReport& report);
}
