/* SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bli
 */

#include <algorithm>

#include "BLI_math_base.h"
#include "BLI_math_vector.h"

#include "BLI_math_base_safe.h"
#include "BLI_math_geom.h"
#include "BLI_math_rotation.h"

#include "BLI_strict_flags.h" /* IWYU pragma: keep. Keep last. */

/* -------------------------------------------------------------------- */
/** \name Interpolation
 * \{ */

void interp_v2_v2v2(float r[2], const float a[2], const float b[2], const float t)
{
  const float s = 1.0f - t;

  r[0] = s * a[0] + t * b[0];
  r[1] = s * a[1] + t * b[1];
}








void interp_v3_v3v3(float r[3], const float a[3], const float b[3], const float t)
{
  const float s = 1.0f - t;

  r[0] = s * a[0] + t * b[0];
  r[1] = s * a[1] + t * b[1];
  r[2] = s * a[2] + t * b[2];
}






































































































































void mid_v3_v3v3(float r[3], const float a[3], const float b[3])
{
  r[0] = 0.5f * (a[0] + b[0]);
  r[1] = 0.5f * (a[1] + b[1]);
  r[2] = 0.5f * (a[2] + b[2]);
}




















void mid_v3_v3v3v3v3(
    float v[3], const float v1[3], const float v2[3], const float v3[3], const float v4[3])
{
  v[0] = (v1[0] + v2[0] + v3[0] + v4[0]) / 4.0f;
  v[1] = (v1[1] + v2[1] + v3[1] + v4[1]) / 4.0f;
  v[2] = (v1[2] + v2[2] + v3[2] + v4[2]) / 4.0f;
}






























/** \} */

/* -------------------------------------------------------------------- */
/** \name Angles
 * \{ */





















































































float angle_normalized_v3v3(const float v1[3], const float v2[3])
{
  /* double check they are normalized */
  BLI_ASSERT_UNIT_V3(v1);
  BLI_ASSERT_UNIT_V3(v2);

  /* this is the same as acos(dot_v3v3(v1, v2)), but more accurate */
  if (dot_v3v3(v1, v2) >= 0.0f) {
    return 2.0f * safe_asinf(len_v3v3(v1, v2) / 2.0f);
  }

  float v2_n[3];
  negate_v3_v3(v2_n, v2);
  return float(M_PI) - 2.0f * safe_asinf(len_v3v3(v1, v2_n) / 2.0f);
}































































































































/** \} */

/* -------------------------------------------------------------------- */
/** \name Geometry
 * \{ */












void project_v3_v3v3(float out[3], const float p[3], const float v_proj[3])
{
  if (UNLIKELY(is_zero_v3(v_proj))) {
    zero_v3(out);
    return;
  }

  const float mul = dot_v3v3(p, v_proj) / dot_v3v3(v_proj, v_proj);
  mul_v3_v3fl(out, v_proj, mul);
}

















void project_plane_v3_v3v3(float out[3], const float p[3], const float v_plane[3])
{
  const float mul = dot_v3v3(p, v_plane) / dot_v3v3(v_plane, v_plane);
  /* out[x] = p[x] - (mul * v_plane[x]) */
  madd_v3_v3v3fl(out, p, v_plane, -mul);
}





















void bisect_v3_v3v3v3(float r[3], const float a[3], const float b[3], const float c[3])
{
  float d_12[3], d_23[3];
  sub_v3_v3v3(d_12, b, a);
  sub_v3_v3v3(d_23, c, b);
  normalize_v3(d_12);
  normalize_v3(d_23);
  add_v3_v3v3(r, d_12, d_23);
  normalize_v3(r);
}









void ortho_basis_v3v3_v3(float r_n1[3], float r_n2[3], const float n[3])
{
  const float eps = FLT_EPSILON;
  const float f = len_squared_v2(n);

  if (f > eps) {
    const float d = 1.0f / sqrtf(f);

    BLI_assert(isfinite(d));

    r_n1[0] = n[1] * d;
    r_n1[1] = -n[0] * d;
    r_n1[2] = 0.0f;
    r_n2[0] = -n[2] * r_n1[1];
    r_n2[1] = n[2] * r_n1[0];
    r_n2[2] = n[0] * r_n1[1] - n[1] * r_n1[0];
  }
  else {
    /* degenerate case */
    r_n1[0] = (n[2] < 0.0f) ? -1.0f : 1.0f;
    r_n1[1] = r_n1[2] = r_n2[0] = r_n2[2] = 0.0f;
    r_n2[1] = 1.0f;
  }
}
















































































/** \} */

/* -------------------------------------------------------------------- */
/** \name Other
 * \{ */

















































































































/** \} */

/* -------------------------------------------------------------------- */
/** \name Array Functions
 * \{ */




































































































































































































































/** \} */

/* -------------------------------------------------------------------- */
/** \name Double precision versions 'db'.
 * \{ */

void add_vn_vn_d(double *array_tar, const double *array_src, const int size)
{
  double *tar = array_tar + (size - 1);
  const double *src = array_src + (size - 1);
  int i = size;
  while (i--) {
    *(tar--) += *(src--);
  }
}

void add_vn_vnvn_d(double *array_tar,
                   const double *array_src_a,
                   const double *array_src_b,
                   const int size)
{
  double *tar = array_tar + (size - 1);
  const double *src_a = array_src_a + (size - 1);
  const double *src_b = array_src_b + (size - 1);
  int i = size;
  while (i--) {
    *(tar--) = *(src_a--) + *(src_b--);
  }
}

void mul_vn_db(double *array_tar, const int size, const double f)
{
  double *array_pt = array_tar + (size - 1);
  int i = size;
  while (i--) {
    *(array_pt--) *= f;
  }
}


















/** \} */
