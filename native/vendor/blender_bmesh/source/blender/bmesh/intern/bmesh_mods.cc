/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bmesh
 *
 * This file contains functions for locally modifying
 * the topology of existing mesh data. (split, join, flip etc).
 */

#include "BLI_math_vector.h"
#include "BLI_vector.hh"

#include "BKE_customdata.hh"

#include "bmesh.hh"
#include "intern/bmesh_private.hh"

using blender::Vector;


























































































































































































BMFace *BM_face_split(BMesh *bm,
                      BMFace *f,
                      BMLoop *l_a,
                      BMLoop *l_b,
                      BMLoop **r_l,
                      BMEdge *example,
                      const bool no_double)
{
  const int cd_loop_mdisp_offset = CustomData_get_offset(&bm->ldata, CD_MDISPS);
  BMFace *f_new, *f_tmp;

  BLI_assert(l_a != l_b);
  BLI_assert(f == l_a->f && f == l_b->f);
  BLI_assert(!BM_loop_is_adjacent(l_a, l_b));

  /* could be an assert */
  if (UNLIKELY(BM_loop_is_adjacent(l_a, l_b)) || UNLIKELY(f != l_a->f || f != l_b->f)) {
    if (r_l) {
      *r_l = nullptr;
    }
    return nullptr;
  }

  /* do we have a multires layer? */
  if (cd_loop_mdisp_offset != -1) {
    f_tmp = BM_face_copy(bm, f, false, false);
  }

#ifdef USE_BMESH_HOLES
  f_new = bmesh_kernel_split_face_make_edge(bm, f, l_a, l_b, r_l, nullptr, example, no_double);
#else
  f_new = bmesh_kernel_split_face_make_edge(bm, f, l_a, l_b, r_l, example, no_double);
#endif

  if (f_new) {
    /* handle multires update */
    if (cd_loop_mdisp_offset != -1) {
      float f_dst_center[3];
      float f_src_center[3];

      BM_face_calc_center_median(f_tmp, f_src_center);

      BM_face_calc_center_median(f, f_dst_center);
      BM_face_interp_multires_ex(bm, f, f_tmp, f_dst_center, f_src_center, cd_loop_mdisp_offset);

      BM_face_calc_center_median(f_new, f_dst_center);
      BM_face_interp_multires_ex(
          bm, f_new, f_tmp, f_dst_center, f_src_center, cd_loop_mdisp_offset);

#if 0
      /* BM_face_multires_bounds_smooth doesn't flip displacement correct */
      BM_face_multires_bounds_smooth(bm, f);
      BM_face_multires_bounds_smooth(bm, f_new);
#endif
    }
  }

  if (cd_loop_mdisp_offset != -1) {
    BM_face_kill(bm, f_tmp);
  }

  return f_new;
}








































































































































































































#undef DO_V_INTERP







BMVert *BM_edge_split(BMesh *bm, BMEdge *e, BMVert *v, BMEdge **r_e, float fac)
{
  BMVert *v_new, *v_other;
  BMEdge *e_new;

  Vector<BMFace *, 32> oldfaces;
  const int cd_loop_mdisp_offset = BM_edge_is_wire(e) ?
                                       -1 :
                                       CustomData_get_offset(&bm->ldata, CD_MDISPS);

  BLI_assert(BM_vert_in_edge(e, v) == true);

  /* do we have a multi-res layer? */
  if (cd_loop_mdisp_offset != -1) {
    BMLoop *l = e->l;
    do {
      oldfaces.append(l->f);
      l = l->radial_next;
    } while (l != e->l);

    /* flag existing faces so we can differentiate oldfaces from new faces */
    for (int64_t i = 0; i < oldfaces.size(); i++) {
      BM_ELEM_API_FLAG_ENABLE(oldfaces[i], _FLAG_OVERLAP);
      oldfaces[i] = BM_face_copy(bm, oldfaces[i], true, true);
      BM_ELEM_API_FLAG_DISABLE(oldfaces[i], _FLAG_OVERLAP);
    }
  }

  v_other = BM_edge_other_vert(e, v);
  v_new = bmesh_kernel_split_edge_make_vert(bm, v, e, &e_new);
  if (r_e != nullptr) {
    *r_e = e_new;
  }

  BLI_assert(v_new != nullptr);
  BLI_assert(BM_vert_in_edge(e_new, v) && BM_vert_in_edge(e_new, v_new));
  BLI_assert(BM_vert_in_edge(e, v_new) && BM_vert_in_edge(e, v_other));

  sub_v3_v3v3(v_new->co, v_other->co, v->co);
  madd_v3_v3v3fl(v_new->co, v->co, v_new->co, fac);

  e_new->head.hflag = e->head.hflag;
  BM_elem_attrs_copy(bm, e, e_new);

  /* v->v_new->v2 */
  BM_data_interp_face_vert_edge(bm, v_other, v, v_new, e, fac);
  BM_data_interp_from_verts(bm, v, v_other, v_new, fac);

  if (cd_loop_mdisp_offset != -1) {
    /* interpolate new/changed loop data from copied old faces */
    for (BMFace *oldface : oldfaces) {
      float f_center_old[3];

      BM_face_calc_center_median(oldface, f_center_old);

      for (int j = 0; j < 2; j++) {
        BMEdge *e1 = j ? e_new : e;
        BMLoop *l = e1->l;

        if (UNLIKELY(!l)) {
          BMESH_ASSERT(0);
          break;
        }

        do {
          /* check this is an old face */
          if (BM_ELEM_API_FLAG_TEST(l->f, _FLAG_OVERLAP)) {
            float f_center[3];

            BM_face_calc_center_median(l->f, f_center);
            BM_face_interp_multires_ex(
                bm, l->f, oldface, f_center, f_center_old, cd_loop_mdisp_offset);
          }
          l = l->radial_next;
        } while (l != e1->l);
      }
    }

    /* destroy the old faces */
    for (BMFace *oldface : oldfaces) {
      BM_face_verts_kill(bm, oldface);
    }

/* fix boundaries a bit, doesn't work too well quite yet */
#if 0
    for (int j = 0; j < 2; j++) {
      BMEdge *e1 = j ? e_new : e;
      BMLoop *l, *l2;

      l = e1->l;
      if (UNLIKELY(!l)) {
        BMESH_ASSERT(0);
        break;
      }

      do {
        BM_face_multires_bounds_smooth(bm, l->f);
        l = l->radial_next;
      } while (l != e1->l);
    }
#endif
  }

  return v_new;
}



















































































































































































































































































































