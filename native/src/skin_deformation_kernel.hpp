#pragma once
#include "skin_deformation.hpp"
#include <igl/bbw.h>
#include <igl/arap_dof.h>
#include <igl/lbs_matrix.h>
#include <igl/in_element.h>
#include <igl/boundary_facets.h>
#if defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable:4100 4189 4244 4267 4505)
#elif defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-variable"
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#endif
#include "../migration/deformation/model.hpp"
#include "../migration/deformation/elastic.hpp"
#include "../migration/deformation/reduced.hpp"
#if defined(_MSC_VER)
#pragma warning(pop)
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#endif
