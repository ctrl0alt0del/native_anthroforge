// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "mesh_internal.hpp"

namespace af::quality {
void validate(const Mesh& before,const Mesh& after,uint64_t cancel);
void validate_tissue(const Mesh& before,const Mesh& after,uint64_t cancel);
}
