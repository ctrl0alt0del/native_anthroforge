/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bmesh
 *
 * Beautify the mesh by rotating edges between triangles
 * to more attractive positions until no more rotations can be made.
 *
 * In principle this is very simple however there is the possibility of
 * going into an eternal loop where edges keep rotating.
 * To avoid this - each edge stores a set of it previous
 * states so as not to rotate back.
 *
 * TODO
 * - Take face normals into account.
 */

#include "BLI_heap.h"
#include "BLI_math_geom.h"
#include "BLI_math_vector.h"
#include "BLI_polyfill_2d_beautify.h"

#include "MEM_guardedalloc.h"

#include "bmesh.hh"
#include "bmesh_beautify.hh" /* own include */

// #define DEBUG_TIME

#ifdef DEBUG_TIME
#  include "BLI_time.h"
#  include "BLI_time_utildefines.h"
#endif

/* -------------------------------------------------------------------- */
/* GSet for edge rotation */

struct EdRotState {
  /**
   * Edge vert indices (ordered small -> large).
   */
  int v_pair[2];
  /**
   * Face vert indices (small -> large).
   *
   * Each face-vertex points to a connected triangles vertex
   * that's isn't part of the edge defined by `v_pair`.
   */
  int f_pair[2];
};

#if 0
/* use BLI_ghashutil_inthash_v4 direct */





#endif
#if 0






























#endif





/* ensure v0 is smaller */


































/* -------------------------------------------------------------------- */
/* Calculate the improvement of rotating the edge */

static float bm_edge_calc_rotate_beauty__angle(const float v1[3],
                                               const float v2[3],
                                               const float v3[3],
                                               const float v4[3])
{
  /* not a loop (only to be able to break out) */
  do {
    float no_a[3], no_b[3];
    float angle_24, angle_13;

    /* edge (2-4), current state */
    normal_tri_v3(no_a, v2, v3, v4);
    normal_tri_v3(no_b, v2, v4, v1);
    angle_24 = angle_normalized_v3v3(no_a, no_b);

    /* edge (1-3), new state */
    /* only check new state for degenerate outcome */
    if ((normal_tri_v3(no_a, v1, v2, v3) == 0.0f) || (normal_tri_v3(no_b, v1, v3, v4) == 0.0f)) {
      break;
    }
    angle_13 = angle_normalized_v3v3(no_a, no_b);

    return angle_13 - angle_24;
  } while (false);

  return FLT_MAX;
}

float BM_verts_calc_rotate_beauty(const BMVert *v1,
                                  const BMVert *v2,
                                  const BMVert *v3,
                                  const BMVert *v4,
                                  const short flag,
                                  const short method)
{
  /* not a loop (only to be able to break out) */
  do {
    if (flag & VERT_RESTRICT_TAG) {
      const BMVert *v_a = v1, *v_b = v3;
      if (BM_elem_flag_test(v_a, BM_ELEM_TAG) == BM_elem_flag_test(v_b, BM_ELEM_TAG)) {
        break;
      }
    }

    if (UNLIKELY(v1 == v3)) {
      // printf("This should never happen, but does sometimes!\n");
      break;
    }

    switch (method) {
      case 0:
        return BLI_polyfill_edge_calc_rotate_beauty__area(
            v1->co, v2->co, v3->co, v4->co, flag & EDGE_RESTRICT_DEGENERATE);
      default:
        return bm_edge_calc_rotate_beauty__angle(v1->co, v2->co, v3->co, v4->co);
    }
  } while (false);

  return FLT_MAX;
}












/* -------------------------------------------------------------------- */
/* Update the edge cost of rotation in the heap */







/* recalc an edge in the heap (surrounding geometry has changed) */














































/* we have rotated an edge, tag other edges and clear this one */





























/* -------------------------------------------------------------------- */
/* Beautify Fill */











































































































