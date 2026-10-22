// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "tissue_directions.hpp"
#include "tissue_profile.hpp"
#include <optional>

namespace af::tissue {
struct PreparedGrid {
    MaterialGrid grid;
    std::vector<kernel::Vec> base,normals;
    std::vector<double> areas;
    double limit=0;
    int mode=0,direction=0;
    bool reversed=false;
    std::optional<DirectionOperators> diffusion;
};
struct InflationPreparation {
    std::shared_ptr<Mesh> source;
    std::vector<PreparedGrid> parts;
};
int preparation_mode(const AfTissueInflation& settings);
InflationPreparation prepare_inflation(std::shared_ptr<Mesh> source,const AfTissueInflation* settings,int count,uint64_t cancel);
uint64_t preparation_bytes(const InflationPreparation& value);
}
