// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "tissue_inflation.hpp"
#include "tissue_shapes.hpp"

namespace af::tissue {
struct InflationWeights { std::vector<double> edge,fade; };
struct Connection {
    int boundary=0;
    std::vector<int> seam;
    std::vector<double> across,along;
    double width=.25,fullness=0;
};
InflationWeights prepared_weights(const Mesh& source,const MaterialGrid& grid,const std::vector<bool>& fixed,const AfTissueInflation& settings,bool branch,uint64_t cancel);
std::vector<Connection> connections(const std::vector<MaterialGrid>& grids,const double* parameters);
void share_displacements(const Mesh& source,const std::vector<MaterialGrid>& grids,const std::vector<Connection>& seams,std::vector<Points>& values);
void connect_parts(const std::vector<MaterialGrid>& grids,const std::vector<Connection>& seams,std::vector<Points>& values,bool flip,uint64_t cancel);
bool grid_reversed(const Mesh& source,const MaterialGrid& grid);
Points inflate_prepared_grid(const Mesh& source,const MaterialGrid& grid,const AfTissueInflation& settings,const InflationWeights* weights,uint64_t cancel);
std::shared_ptr<Mesh> inflate_parts(const Mesh& source,const AfTissueInflation* settings,int count,const double* connectors,bool envelope,uint64_t cancel);
}
