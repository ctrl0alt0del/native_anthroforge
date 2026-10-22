// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "tissue_math.hpp"

namespace af::tissue {
std::vector<kernel::Vec> section_directions(const std::vector<kernel::Vec>& base,int rows,int columns,
    int mode,std::vector<double>& areas);
int section_profile(const std::vector<kernel::Vec>& base,int rows,int columns,const double* settings,
    int mode,int sign,std::vector<kernel::Vec>& output);
}
