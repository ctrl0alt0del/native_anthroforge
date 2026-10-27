#pragma once
#include "skin_gap_internal.hpp"
#include "skin_fields.hpp"

namespace af::skin {
using Tiles=kernel::af_skin::SkinTiles;
Grid protected_grid(Scene& scene,const Fields& fields,const std::vector<float>& coarse,uint64_t cancel);
std::unique_ptr<Tiles> prepare_tiles(Scene& scene,const Fields& fields,uint64_t budget,uint64_t cancel);
std::shared_ptr<Mesh> extract_envelope(Tiles& tiles,double* diagnostics,uint64_t cancel);
void diagnose(Tiles& tiles,const Mesh& mesh,double* output,uint64_t cancel);
}
