/* SPDX-FileCopyrightText: 2007 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bmesh
 *
 * BM construction functions.
 */

#include "MEM_guardedalloc.h"

#include "BLI_alloca.h"
#include "BLI_listbase.h"
#include "BLI_math_vector.h"
#include "BLI_sort_utils.h"

#include "BKE_customdata.hh"

#include "DNA_mesh_types.h"

#include "bmesh.hh"
#include "intern/bmesh_private.hh"














bool BM_edges_from_verts(BMEdge **edge_arr, BMVert **vert_arr, const int len)
{
  int i, i_prev = len - 1;
  for (i = 0; i < len; i++) {
    edge_arr[i_prev] = BM_edge_exists(vert_arr[i_prev], vert_arr[i]);
    if (edge_arr[i_prev] == nullptr) {
      return false;
    }
    i_prev = i;
  }
  return true;
}

void BM_edges_from_verts_ensure(BMesh *bm, BMEdge **edge_arr, BMVert **vert_arr, const int len)
{
  int i, i_prev = len - 1;
  for (i = 0; i < len; i++) {
    edge_arr[i_prev] = BM_edge_create(
        bm, vert_arr[i_prev], vert_arr[i], nullptr, BM_CREATE_NO_DOUBLE);
    i_prev = i;
  }
}

BMFace *BM_face_create_quad_tri(BMesh *bm,
                                BMVert *v1,
                                BMVert *v2,
                                BMVert *v3,
                                BMVert *v4,
                                const BMFace *f_example,
                                const eBMCreateFlag create_flag)
{
  BMVert *vtar[4] = {v1, v2, v3, v4};
  return BM_face_create_verts(bm, vtar, v4 ? 4 : 3, f_example, create_flag, true);
}

















































/**
 * Given an array of edges,
 * order them using the winding defined by \a v1 & \a v2
 * into \a edges_sort & \a verts_sort.
 *
 * All arrays must be \a len long.
 */
static bool bm_edges_sort_winding(BMVert *v1,
                                  BMVert *v2,
                                  BMEdge **edges,
                                  const int len,
                                  BMEdge **edges_sort,
                                  BMVert **verts_sort)
{
  BMEdge *e_iter, *e_first;
  BMVert *v_iter;
  int i;

  /* all flags _must_ be cleared on exit! */
  for (i = 0; i < len; i++) {
    BM_ELEM_API_FLAG_ENABLE(edges[i], _FLAG_MF);
    BM_ELEM_API_FLAG_ENABLE(edges[i]->v1, _FLAG_MV);
    BM_ELEM_API_FLAG_ENABLE(edges[i]->v2, _FLAG_MV);
  }

  /* find first edge */
  i = 0;
  v_iter = v1;
  e_iter = e_first = v1->e;
  do {
    if (BM_ELEM_API_FLAG_TEST(e_iter, _FLAG_MF) && (BM_edge_other_vert(e_iter, v_iter) == v2)) {
      i = 1;
      break;
    }
  } while ((e_iter = bmesh_disk_edge_next(e_iter, v_iter)) != e_first);
  if (i == 0) {
    goto error;
  }

  i = 0;
  do {
    /* entering loop will always succeed */
    if (BM_ELEM_API_FLAG_TEST(e_iter, _FLAG_MF)) {
      if (UNLIKELY(BM_ELEM_API_FLAG_TEST(v_iter, _FLAG_MV) == false)) {
        /* vert is in loop multiple times */
        goto error;
      }

      BM_ELEM_API_FLAG_DISABLE(e_iter, _FLAG_MF);
      edges_sort[i] = e_iter;

      BM_ELEM_API_FLAG_DISABLE(v_iter, _FLAG_MV);
      verts_sort[i] = v_iter;

      i += 1;

      /* walk onto the next vertex */
      v_iter = BM_edge_other_vert(e_iter, v_iter);
      if (i == len) {
        if (UNLIKELY(v_iter != verts_sort[0])) {
          goto error;
        }
        break;
      }

      e_first = e_iter;
    }
  } while ((e_iter = bmesh_disk_edge_next(e_iter, v_iter)) != e_first);

  if (i == len) {
    return true;
  }

error:
  for (i = 0; i < len; i++) {
    BM_ELEM_API_FLAG_DISABLE(edges[i], _FLAG_MF);
    BM_ELEM_API_FLAG_DISABLE(edges[i]->v1, _FLAG_MV);
    BM_ELEM_API_FLAG_DISABLE(edges[i]->v2, _FLAG_MV);
  }

  return false;
}

BMFace *BM_face_create_ngon(BMesh *bm,
                            BMVert *v1,
                            BMVert *v2,
                            BMEdge **edges,
                            const int len,
                            const BMFace *f_example,
                            const eBMCreateFlag create_flag)
{
  BMEdge **edges_sort = BLI_array_alloca(edges_sort, len);
  BMVert **verts_sort = BLI_array_alloca(verts_sort, len);

  BLI_assert(len && v1 && v2 && edges && bm);

  if (bm_edges_sort_winding(v1, v2, edges, len, edges_sort, verts_sort)) {
    return BM_face_create(bm, verts_sort, edges_sort, len, f_example, create_flag);
  }

  return nullptr;
}






























































































/*************************************************************/

void BM_elem_attrs_copy(BMesh *bm, const BMCustomDataCopyMap &map, const BMVert *src, BMVert *dst)
{
  BLI_assert(src != dst);
  CustomData_bmesh_copy_block(bm->vdata, map, src->head.data, &dst->head.data);
  constexpr char hflag_mask = BM_ELEM_SELECT;
  dst->head.hflag = (dst->head.hflag & hflag_mask) | (src->head.hflag & ~hflag_mask);
  copy_v3_v3(dst->no, src->no);
}
void BM_elem_attrs_copy(BMesh *bm, const BMCustomDataCopyMap &map, const BMEdge *src, BMEdge *dst)
{
  BLI_assert(src != dst);
  CustomData_bmesh_copy_block(bm->edata, map, src->head.data, &dst->head.data);
  constexpr char hflag_mask = BM_ELEM_SELECT;
  dst->head.hflag = (dst->head.hflag & hflag_mask) | (src->head.hflag & ~hflag_mask);
}
void BM_elem_attrs_copy(BMesh *bm, const BMCustomDataCopyMap &map, const BMFace *src, BMFace *dst)
{
  BLI_assert(src != dst);
  CustomData_bmesh_copy_block(bm->pdata, map, src->head.data, &dst->head.data);
  constexpr char hflag_mask = BM_ELEM_SELECT | BM_ELEM_SELECT_UV;
  dst->head.hflag = (dst->head.hflag & hflag_mask) | (src->head.hflag & ~hflag_mask);
  copy_v3_v3(dst->no, src->no);
  dst->mat_nr = src->mat_nr;
}
void BM_elem_attrs_copy(BMesh *bm, const BMCustomDataCopyMap &map, const BMLoop *src, BMLoop *dst)
{
  BLI_assert(src != dst);
  CustomData_bmesh_copy_block(bm->ldata, map, src->head.data, &dst->head.data);
  constexpr char hflag_mask = BM_ELEM_SELECT | BM_ELEM_SELECT_UV | BM_ELEM_SELECT_UV_EDGE;
  dst->head.hflag = (dst->head.hflag & hflag_mask) | (src->head.hflag & ~hflag_mask);
}

void BM_elem_attrs_copy(BMesh *bm, const BMVert *src, BMVert *dst)
{
  BLI_assert(src != dst);
  CustomData_bmesh_copy_block(bm->vdata, src->head.data, &dst->head.data);
  constexpr char hflag_mask = BM_ELEM_SELECT;
  dst->head.hflag = (dst->head.hflag & hflag_mask) | (src->head.hflag & ~hflag_mask);
  copy_v3_v3(dst->no, src->no);
}
void BM_elem_attrs_copy(BMesh *bm, const BMEdge *src, BMEdge *dst)
{
  BLI_assert(src != dst);
  CustomData_bmesh_copy_block(bm->edata, src->head.data, &dst->head.data);
  constexpr char hflag_mask = BM_ELEM_SELECT;
  dst->head.hflag = (dst->head.hflag & hflag_mask) | (src->head.hflag & ~hflag_mask);
}
void BM_elem_attrs_copy(BMesh *bm, const BMFace *src, BMFace *dst)
{
  BLI_assert(src != dst);
  constexpr char hflag_mask = BM_ELEM_SELECT | BM_ELEM_SELECT_UV;
  CustomData_bmesh_copy_block(bm->pdata, src->head.data, &dst->head.data);
  dst->head.hflag = (dst->head.hflag & hflag_mask) | (src->head.hflag & ~hflag_mask);
  copy_v3_v3(dst->no, src->no);
  dst->mat_nr = src->mat_nr;
}
void BM_elem_attrs_copy(BMesh *bm, const BMLoop *src, BMLoop *dst)
{
  BLI_assert(src != dst);
  constexpr char hflag_mask = BM_ELEM_SELECT | BM_ELEM_SELECT_UV | BM_ELEM_SELECT_UV_EDGE;
  CustomData_bmesh_copy_block(bm->ldata, src->head.data, &dst->head.data);
  dst->head.hflag = (dst->head.hflag & hflag_mask) | (src->head.hflag & ~hflag_mask);
}













/* helper function for 'BM_mesh_copy' */





























































































































































































































































































