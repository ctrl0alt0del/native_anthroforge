#pragma once
#include "tissue_math.hpp"

namespace af::tissue::kernel {
#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-function"
#elif defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-function"
#elif defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable:4505)
#endif
#include "../migration/tissue/kernel_0.hpp"
#include "../migration/tissue/kernel_1.hpp"
#include "../migration/tissue/kernel_2.hpp"
#include "../migration/tissue/kernel_3.hpp"
#if defined(__clang__)
#pragma clang diagnostic pop
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
}
