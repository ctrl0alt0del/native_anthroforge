/* SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bli
 */

#include "BLI_math_rotation.h"

#include "BLI_math_base_safe.h"
#include "BLI_math_geom.h"
#include "BLI_math_matrix.h"
#include "BLI_math_vector.h"

#include "BLI_strict_flags.h" /* IWYU pragma: keep. Keep last. */

/******************************** Quaternions ********************************/

/* used to test is a quat is not normalized (only used for debug prints) */
#ifndef NDEBUG
#  define QUAT_EPSILON 0.0001
#endif

/**
 * The threshold for using a zeroed 3rd (typically Z) value when calculating the euler.
 * NOTE(@ideasman42): A reasonable range for this value is (0.0002 .. 0.00002).
 * This was previously `16 * FLT_EPSILON` however it caused imprecision at times,
 * see examples from: #116880.
 */
#define EULER_HYPOT_EPSILON 0.0000375









void unit_qt(float q[4])
{
  q[0] = 1.0f;
  q[1] = q[2] = q[3] = 0.0f;
}

void copy_qt_qt(float q[4], const float a[4])
{
  q[0] = a[0];
  q[1] = a[1];
  q[2] = a[2];
  q[3] = a[3];
}






void mul_qt_qtqt(float q[4], const float a[4], const float b[4])
{
  float t0, t1, t2;

  t0 = a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3];
  t1 = a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2];
  t2 = a[0] * b[2] + a[2] * b[0] + a[3] * b[1] - a[1] * b[3];
  q[3] = a[0] * b[3] + a[3] * b[0] + a[1] * b[2] - a[2] * b[1];
  q[0] = t0;
  q[1] = t1;
  q[2] = t2;
}

void mul_qt_v3(const float q[4], float r[3])
{
  float t0, t1, t2;

  t0 = -q[1] * r[0] - q[2] * r[1] - q[3] * r[2];
  t1 = q[0] * r[0] + q[2] * r[2] - q[3] * r[1];
  t2 = q[0] * r[1] + q[3] * r[0] - q[1] * r[2];
  r[2] = q[0] * r[2] + q[1] * r[1] - q[2] * r[0];
  r[0] = t1;
  r[1] = t2;

  t1 = t0 * -q[1] + r[0] * q[0] - r[1] * q[3] + r[2] * q[2];
  t2 = t0 * -q[2] + r[1] * q[0] - r[2] * q[1] + r[0] * q[3];
  r[2] = t0 * -q[3] + r[2] * q[0] - r[0] * q[2] + r[1] * q[1];
  r[0] = t1;
  r[1] = t2;
}
















float dot_qtqt(const float a[4], const float b[4])
{
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3];
}































void mul_qt_fl(float q[4], const float f)
{
  q[0] *= f;
  q[1] *= f;
  q[2] *= f;
  q[3] *= f;
}













































/* Skip error check, currently only needed by #mat3_to_quat_legacy. */
static void quat_to_mat3_no_error(float m[3][3], const float q[4])
{
  double q0, q1, q2, q3, qda, qdb, qdc, qaa, qab, qac, qbb, qbc, qcc;

  q0 = M_SQRT2 * double(q[0]);
  q1 = M_SQRT2 * double(q[1]);
  q2 = M_SQRT2 * double(q[2]);
  q3 = M_SQRT2 * double(q[3]);

  qda = q0 * q1;
  qdb = q0 * q2;
  qdc = q0 * q3;
  qaa = q1 * q1;
  qab = q1 * q2;
  qac = q1 * q3;
  qbb = q2 * q2;
  qbc = q2 * q3;
  qcc = q3 * q3;

  m[0][0] = float(1.0 - qbb - qcc);
  m[0][1] = float(qdc + qab);
  m[0][2] = float(-qdb + qac);

  m[1][0] = float(-qdc + qab);
  m[1][1] = float(1.0 - qaa - qcc);
  m[1][2] = float(qda + qbc);

  m[2][0] = float(qdb + qac);
  m[2][1] = float(-qda + qbc);
  m[2][2] = float(1.0 - qaa - qbb);
}

void quat_to_mat3(float m[3][3], const float q[4])
{
#ifndef NDEBUG
  float f;
  if (!((f = dot_qtqt(q, q)) == 0.0f || (fabsf(f - 1.0f) < float(QUAT_EPSILON)))) {
    fprintf(stderr,
            "Warning! quat_to_mat3() called with non-normalized: size %.8f *** report a bug ***\n",
            f);
  }
#endif

  quat_to_mat3_no_error(m, q);
}





































































































































































































































float normalize_qt(float q[4])
{
  const float len = sqrtf(dot_qtqt(q, q));

  if (len != 0.0f) {
    mul_qt_fl(q, 1.0f / len);
  }
  else {
    q[1] = 1.0f;
    q[0] = q[2] = q[3] = 0.0f;
  }

  return len;
}


































































































































/* -------------------------------------------------------------------- */
/** \name Quaternion Angle
 *
 * Unlike the angle between vectors, this does NOT return the shortest angle.
 * See signed functions below for this.
 *
 * \{ */






































/** \} */

/* -------------------------------------------------------------------- */
/** \name Quaternion Angle (Signed)
 *
 * Angles with quaternion calculation can exceed 180d,
 * Having signed versions of these functions allows 'fabsf(angle_signed_qtqt(...))'
 * to give us the shortest angle between quaternions.
 * With higher precision than subtracting pi afterwards.
 *
 * \{ */










































/** \} */

void vec_to_quat(float q[4], const float vec[3], short axis, const short upflag)
{
  const float eps = 1e-4f;
  float nor[3], tvec[3];
  float angle, si, co, len;

  BLI_assert(axis >= 0 && axis <= 5);
  BLI_assert(upflag >= 0 && upflag <= 2);

  /* first set the quat to unit */
  unit_qt(q);

  len = len_v3(vec);

  if (UNLIKELY(len == 0.0f)) {
    return;
  }

  /* rotate to axis */
  if (axis > 2) {
    copy_v3_v3(tvec, vec);
    axis = short(axis - 3);
  }
  else {
    negate_v3_v3(tvec, vec);
  }

  /* nasty! I need a good routine for this...
   * problem is a rotation of an Y axis to the negative Y-axis for example.
   */

  if (axis == 0) { /* x-axis */
    nor[0] = 0.0;
    nor[1] = -tvec[2];
    nor[2] = tvec[1];

    if (fabsf(tvec[1]) + fabsf(tvec[2]) < eps) {
      nor[1] = 1.0f;
    }

    co = tvec[0];
  }
  else if (axis == 1) { /* y-axis */
    nor[0] = tvec[2];
    nor[1] = 0.0;
    nor[2] = -tvec[0];

    if (fabsf(tvec[0]) + fabsf(tvec[2]) < eps) {
      nor[2] = 1.0f;
    }

    co = tvec[1];
  }
  else { /* z-axis */
    nor[0] = -tvec[1];
    nor[1] = tvec[0];
    nor[2] = 0.0;

    if (fabsf(tvec[0]) + fabsf(tvec[1]) < eps) {
      nor[0] = 1.0f;
    }

    co = tvec[2];
  }
  co /= len;

  normalize_v3(nor);

  axis_angle_normalized_to_quat(q, nor, safe_acosf(co));

  if (axis != upflag) {
    float mat[3][3];
    float q2[4];
    const float *fp = mat[2];
    quat_to_mat3(mat, q);

    if (axis == 0) {
      if (upflag == 1) {
        angle = 0.5f * atan2f(fp[2], fp[1]);
      }
      else {
        angle = -0.5f * atan2f(fp[1], fp[2]);
      }
    }
    else if (axis == 1) {
      if (upflag == 0) {
        angle = -0.5f * atan2f(fp[2], fp[0]);
      }
      else {
        angle = 0.5f * atan2f(fp[0], fp[2]);
      }
    }
    else {
      if (upflag == 0) {
        angle = 0.5f * atan2f(-fp[1], -fp[0]);
      }
      else {
        angle = -0.5f * atan2f(-fp[0], -fp[1]);
      }
    }

    co = cosf(angle);
    si = sinf(angle) / len;
    q2[0] = co;
    q2[1] = tvec[0] * si;
    q2[2] = tvec[1] * si;
    q2[3] = tvec[2] * si;

    mul_qt_qtqt(q, q2, q);
  }
}

#if 0

/* A & M Watt, Advanced animation and rendering techniques, 1992 ACM press */







































#endif






















































































































































































/******************************** Axis Angle *********************************/

void axis_angle_normalized_to_quat(float r[4], const float axis[3], const float angle)
{
  const float phi = 0.5f * angle;
  const float si = sinf(phi);
  const float co = cosf(phi);
  BLI_ASSERT_UNIT_V3(axis);
  r[0] = co;
  mul_v3_v3fl(r + 1, axis, si);
}

void axis_angle_to_quat(float r[4], const float axis[3], const float angle)
{
  float nor[3];

  if (LIKELY(normalize_v3_v3(nor, axis) != 0.0f)) {
    axis_angle_normalized_to_quat(r, nor, angle);
  }
  else {
    unit_qt(r);
  }
}







































































































































































































































/****************************** Exponential Map ******************************/


































/******************************** XYZ Eulers *********************************/
























































/* returns two euler calculation methods, so we can pick the best */

/* XYZ order */





























































































































































/* uses 2 methods to retrieve eulers, and picks the closest */




































/************************** Arbitrary Order Eulers ***************************/

/* Euler Rotation Order Code:
 * was adapted from
 *      ANSI C code from the article
 *      "Euler Angle Conversion"
 *      by Ken Shoemake <shoemake@graphics.cis.upenn.edu>
 *      in "Graphics Gems IV", Academic Press, 1994
 * for use in Blender
 */

/* Type for rotation order info - see wiki for derivation details */
struct RotOrderInfo {
  short axis[3];
  short parity; /* parity of axis permutation (even=0, odd=1) - 'n' in original code */
};

/* Array of info for Rotation Order calculations
 * WARNING: must be kept in same order as eEulerRotationOrders
 */
static const RotOrderInfo rotOrders[] = {
    /* i, j, k, n */
    {{0, 1, 2}, 0}, /* XYZ */
    {{0, 2, 1}, 1}, /* XZY */
    {{1, 0, 2}, 1}, /* YXZ */
    {{1, 2, 0}, 0}, /* YZX */
    {{2, 0, 1}, 0}, /* ZXY */
    {{2, 1, 0}, 1}  /* ZYX */
};

/* Get relevant pointer to rotation order set from the array
 * NOTE: since we start at 1 for the values, but arrays index from 0,
 *       there is -1 factor involved in this process...
 */


































































































/* returns two euler calculation methods, so we can pick the best */





























































































































































/* rotate the given euler by the given angle on the specified axis */
/* NOTE: is this safe to do with different axis orders? */










































































/******************************* Dual Quaternions ****************************/

/* Conversion routines between (regular quaternion, translation) and dual quaternion.
 *
 * Version 1.0.0, February 7th, 2007
 *
 * SPDX-License-Identifier: Zlib
 * Copyright 2006-2007 University of Dublin, Trinity College, All Rights Reserved.
 *
 * Changes for Blender:
 * - renaming, style changes and optimization's
 * - added support for scaling
 */

























































































































































































































































































































































/* `mod_inline(-3, 4)= 1`, `fmod(-3, 4)= -3` */




















/* axis conversion */
static float _axis_convert_matrix[23][3][3] = {
    {{-1.0, 0.0, 0.0}, {0.0, -1.0, 0.0}, {0.0, 0.0, 1.0}},
    {{-1.0, 0.0, 0.0}, {0.0, 0.0, -1.0}, {0.0, -1.0, 0.0}},
    {{-1.0, 0.0, 0.0}, {0.0, 0.0, 1.0}, {0.0, 1.0, 0.0}},
    {{-1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, -1.0}},
    {{0.0, -1.0, 0.0}, {-1.0, 0.0, 0.0}, {0.0, 0.0, -1.0}},
    {{0.0, 0.0, 1.0}, {-1.0, 0.0, 0.0}, {0.0, -1.0, 0.0}},
    {{0.0, 0.0, -1.0}, {-1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}},
    {{0.0, 1.0, 0.0}, {-1.0, 0.0, 0.0}, {0.0, 0.0, 1.0}},
    {{0.0, -1.0, 0.0}, {0.0, 0.0, 1.0}, {-1.0, 0.0, 0.0}},
    {{0.0, 0.0, -1.0}, {0.0, -1.0, 0.0}, {-1.0, 0.0, 0.0}},
    {{0.0, 0.0, 1.0}, {0.0, 1.0, 0.0}, {-1.0, 0.0, 0.0}},
    {{0.0, 1.0, 0.0}, {0.0, 0.0, -1.0}, {-1.0, 0.0, 0.0}},
    {{0.0, -1.0, 0.0}, {0.0, 0.0, -1.0}, {1.0, 0.0, 0.0}},
    {{0.0, 0.0, 1.0}, {0.0, -1.0, 0.0}, {1.0, 0.0, 0.0}},
    {{0.0, 0.0, -1.0}, {0.0, 1.0, 0.0}, {1.0, 0.0, 0.0}},
    {{0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}, {1.0, 0.0, 0.0}},
    {{0.0, -1.0, 0.0}, {1.0, 0.0, 0.0}, {0.0, 0.0, 1.0}},
    {{0.0, 0.0, -1.0}, {1.0, 0.0, 0.0}, {0.0, -1.0, 0.0}},
    {{0.0, 0.0, 1.0}, {1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}},
    {{0.0, 1.0, 0.0}, {1.0, 0.0, 0.0}, {0.0, 0.0, -1.0}},
    {{1.0, 0.0, 0.0}, {0.0, -1.0, 0.0}, {0.0, 0.0, -1.0}},
    {{1.0, 0.0, 0.0}, {0.0, 0.0, 1.0}, {0.0, -1.0, 0.0}},
    {{1.0, 0.0, 0.0}, {0.0, 0.0, -1.0}, {0.0, 1.0, 0.0}},
};

static int _axis_convert_lut[23][24] = {
    {0x8C8, 0x4D0, 0x2E0, 0xAE8, 0x701, 0x511, 0x119, 0xB29, 0x682, 0x88A, 0x09A, 0x2A2,
     0x80B, 0x413, 0x223, 0xA2B, 0x644, 0x454, 0x05C, 0xA6C, 0x745, 0x94D, 0x15D, 0x365},
    {0xAC8, 0x8D0, 0x4E0, 0x2E8, 0x741, 0x951, 0x159, 0x369, 0x702, 0xB0A, 0x11A, 0x522,
     0xA0B, 0x813, 0x423, 0x22B, 0x684, 0x894, 0x09C, 0x2AC, 0x645, 0xA4D, 0x05D, 0x465},
    {0x4C8, 0x2D0, 0xAE0, 0x8E8, 0x681, 0x291, 0x099, 0x8A9, 0x642, 0x44A, 0x05A, 0xA62,
     0x40B, 0x213, 0xA23, 0x82B, 0x744, 0x354, 0x15C, 0x96C, 0x705, 0x50D, 0x11D, 0xB25},
    {0x2C8, 0xAD0, 0x8E0, 0x4E8, 0x641, 0xA51, 0x059, 0x469, 0x742, 0x34A, 0x15A, 0x962,
     0x20B, 0xA13, 0x823, 0x42B, 0x704, 0xB14, 0x11C, 0x52C, 0x685, 0x28D, 0x09D, 0x8A5},
    {0x708, 0xB10, 0x120, 0x528, 0x8C1, 0xAD1, 0x2D9, 0x4E9, 0x942, 0x74A, 0x35A, 0x162,
     0x64B, 0xA53, 0x063, 0x46B, 0x804, 0xA14, 0x21C, 0x42C, 0x885, 0x68D, 0x29D, 0x0A5},
    {0xB08, 0x110, 0x520, 0x728, 0x941, 0x151, 0x359, 0x769, 0x802, 0xA0A, 0x21A, 0x422,
     0xA4B, 0x053, 0x463, 0x66B, 0x884, 0x094, 0x29C, 0x6AC, 0x8C5, 0xACD, 0x2DD, 0x4E5},
    {0x508, 0x710, 0xB20, 0x128, 0x881, 0x691, 0x299, 0x0A9, 0x8C2, 0x4CA, 0x2DA, 0xAE2,
     0x44B, 0x653, 0xA63, 0x06B, 0x944, 0x754, 0x35C, 0x16C, 0x805, 0x40D, 0x21D, 0xA25},
    {0x108, 0x510, 0x720, 0xB28, 0x801, 0x411, 0x219, 0xA29, 0x882, 0x08A, 0x29A, 0x6A2,
     0x04B, 0x453, 0x663, 0xA6B, 0x8C4, 0x4D4, 0x2DC, 0xAEC, 0x945, 0x14D, 0x35D, 0x765},
    {0x748, 0x350, 0x160, 0x968, 0xAC1, 0x2D1, 0x4D9, 0x8E9, 0xA42, 0x64A, 0x45A, 0x062,
     0x68B, 0x293, 0x0A3, 0x8AB, 0xA04, 0x214, 0x41C, 0x82C, 0xB05, 0x70D, 0x51D, 0x125},
    {0x948, 0x750, 0x360, 0x168, 0xB01, 0x711, 0x519, 0x129, 0xAC2, 0x8CA, 0x4DA, 0x2E2,
     0x88B, 0x693, 0x2A3, 0x0AB, 0xA44, 0x654, 0x45C, 0x06C, 0xA05, 0x80D, 0x41D, 0x225},
    {0x348, 0x150, 0x960, 0x768, 0xA41, 0x051, 0x459, 0x669, 0xA02, 0x20A, 0x41A, 0x822,
     0x28B, 0x093, 0x8A3, 0x6AB, 0xB04, 0x114, 0x51C, 0x72C, 0xAC5, 0x2CD, 0x4DD, 0x8E5},
    {0x148, 0x950, 0x760, 0x368, 0xA01, 0x811, 0x419, 0x229, 0xB02, 0x10A, 0x51A, 0x722,
     0x08B, 0x893, 0x6A3, 0x2AB, 0xAC4, 0x8D4, 0x4DC, 0x2EC, 0xA45, 0x04D, 0x45D, 0x665},
    {0x688, 0x890, 0x0A0, 0x2A8, 0x4C1, 0x8D1, 0xAD9, 0x2E9, 0x502, 0x70A, 0xB1A, 0x122,
     0x74B, 0x953, 0x163, 0x36B, 0x404, 0x814, 0xA1C, 0x22C, 0x445, 0x64D, 0xA5D, 0x065},
    {0x888, 0x090, 0x2A0, 0x6A8, 0x501, 0x111, 0xB19, 0x729, 0x402, 0x80A, 0xA1A, 0x222,
     0x94B, 0x153, 0x363, 0x76B, 0x444, 0x054, 0xA5C, 0x66C, 0x4C5, 0x8CD, 0xADD, 0x2E5},
    {0x288, 0x690, 0x8A0, 0x0A8, 0x441, 0x651, 0xA59, 0x069, 0x4C2, 0x2CA, 0xADA, 0x8E2,
     0x34B, 0x753, 0x963, 0x16B, 0x504, 0x714, 0xB1C, 0x12C, 0x405, 0x20D, 0xA1D, 0x825},
    {0x088, 0x290, 0x6A0, 0x8A8, 0x401, 0x211, 0xA19, 0x829, 0x442, 0x04A, 0xA5A, 0x662,
     0x14B, 0x353, 0x763, 0x96B, 0x4C4, 0x2D4, 0xADC, 0x8EC, 0x505, 0x10D, 0xB1D, 0x725},
    {0x648, 0x450, 0x060, 0xA68, 0x2C1, 0x4D1, 0x8D9, 0xAE9, 0x282, 0x68A, 0x89A, 0x0A2,
     0x70B, 0x513, 0x123, 0xB2B, 0x204, 0x414, 0x81C, 0xA2C, 0x345, 0x74D, 0x95D, 0x165},
    {0xA48, 0x650, 0x460, 0x068, 0x341, 0x751, 0x959, 0x169, 0x2C2, 0xACA, 0x8DA, 0x4E2,
     0xB0B, 0x713, 0x523, 0x12B, 0x284, 0x694, 0x89C, 0x0AC, 0x205, 0xA0D, 0x81D, 0x425},
    {0x448, 0x050, 0xA60, 0x668, 0x281, 0x091, 0x899, 0x6A9, 0x202, 0x40A, 0x81A, 0xA22,
     0x50B, 0x113, 0xB23, 0x72B, 0x344, 0x154, 0x95C, 0x76C, 0x2C5, 0x4CD, 0x8DD, 0xAE5},
    {0x048, 0xA50, 0x660, 0x468, 0x201, 0xA11, 0x819, 0x429, 0x342, 0x14A, 0x95A, 0x762,
     0x10B, 0xB13, 0x723, 0x52B, 0x2C4, 0xAD4, 0x8DC, 0x4EC, 0x285, 0x08D, 0x89D, 0x6A5},
    {0x808, 0xA10, 0x220, 0x428, 0x101, 0xB11, 0x719, 0x529, 0x142, 0x94A, 0x75A, 0x362,
     0x8CB, 0xAD3, 0x2E3, 0x4EB, 0x044, 0xA54, 0x65C, 0x46C, 0x085, 0x88D, 0x69D, 0x2A5},
    {0xA08, 0x210, 0x420, 0x828, 0x141, 0x351, 0x759, 0x969, 0x042, 0xA4A, 0x65A, 0x462,
     0xACB, 0x2D3, 0x4E3, 0x8EB, 0x084, 0x294, 0x69C, 0x8AC, 0x105, 0xB0D, 0x71D, 0x525},
    {0x408, 0x810, 0xA20, 0x228, 0x081, 0x891, 0x699, 0x2A9, 0x102, 0x50A, 0x71A, 0xB22,
     0x4CB, 0x8D3, 0xAE3, 0x2EB, 0x144, 0x954, 0x75C, 0x36C, 0x045, 0x44D, 0x65D, 0xA65},
};

// _axis_convert_num = {'X': 0, 'Y': 1, 'Z': 2, '-X': 3, '-Y': 4, '-Z': 5}

























































