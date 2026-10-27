#pragma once
#include "skin_deformation_kernel.hpp"
#if defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable:4100 4189 4244 4267 4505)
#elif defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-function"
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-variable"
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#endif
namespace af_ad { static thread_local std::string error; }
#define API [[maybe_unused]] static
#include "../migration/deformation/contact.hpp"
#undef API
#if defined(_MSC_VER)
#pragma warning(pop)
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#endif
