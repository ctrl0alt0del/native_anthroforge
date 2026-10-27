#include "skin_execution.hpp"
#include "skin_kernel.hpp"

namespace af::skin {
int field_workers(uint64_t lines) {
    return kernel::af_parallel_workers(int(std::min(lines,uint64_t(std::numeric_limits<int>::max()))));
}
}
