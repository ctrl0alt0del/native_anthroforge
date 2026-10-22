#pragma once
#include "tissue_math.hpp"

namespace af::tissue::kernel {
#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-function"
#endif
#include "../migration/tissue/kernel_0.hpp"
#include "../migration/tissue/kernel_1.hpp"
#include "../migration/tissue/kernel_2.hpp"
#include "../migration/tissue/kernel_3.hpp"
#if defined(__clang__)
#pragma clang diagnostic pop
#endif
}
