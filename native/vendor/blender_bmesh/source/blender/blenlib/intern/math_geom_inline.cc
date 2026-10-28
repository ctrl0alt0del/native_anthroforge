/* SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bli
 */

#ifndef __MATH_GEOM_INLINE_C__
#define __MATH_GEOM_INLINE_C__

#include "BLI_math_vector.h"

#include <cstring>

/* A few small defines. Keep them local! */
#define SMALL_NUMBER 1.e-8f

/********************************** Polygons *********************************/

MINLINE float cross_tri_v2(const float v1[2], const float v2[2], const float v3[2])
{
  return (v1[0] - v2[0]) * (v2[1] - v3[1]) + (v1[1] - v2[1]) * (v3[0] - v2[0]);
}
































































































MINLINE float plane_point_side_v3(const float plane[4], const float co[3])
{
  return dot_v3v3(co, plane) + plane[3];
}










































#undef SMALL_NUMBER

#endif /* __MATH_GEOM_INLINE_C__ */
