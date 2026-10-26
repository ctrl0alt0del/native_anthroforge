#pragma once
#include <array>
#include <cstdint>
#include <vector>

namespace af::skin {
struct TileMesh { std::vector<float> vertices; std::vector<int32_t> faces; };
TileMesh extract_tile(const float* values,const std::array<int,3>& shape,uint64_t cancel);
}
