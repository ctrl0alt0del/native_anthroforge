#pragma once
#include <cstdint>

namespace af::skin {
// Shares the pinned skin kernels' team limit; admission remains coordinator-owned.
int field_workers(uint64_t lines);
}
