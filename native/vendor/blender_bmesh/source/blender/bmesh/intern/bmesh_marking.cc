/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bmesh
 *
 * Selection routines for bmesh structures.
 * This is actually all old code ripped from
 * editmesh_lib.c and slightly modified to work
 * for bmesh's. This also means that it has some
 * of the same problems.... something that
 * that should be addressed eventually.
 */

#include <cstddef>

#include "MEM_guardedalloc.h"

#include "DNA_scene_types.h"

#include "BLI_listbase.h"
#include "BLI_math_vector.h"
#include "BLI_task.h"

#include "bmesh.hh"
#include "bmesh_query_uv.hh"
#include "bmesh_structure.hh"

/* For '_FLAG_OVERLAP'. */
#include "bmesh_private.hh"

/* -------------------------------------------------------------------- */
/** \name Recounting total selection.
 * \{ */

struct SelectionCountChunkData {
  int selection_len;
};




































































































#ifndef NDEBUG






#endif

/** \} */

/* -------------------------------------------------------------------- */
/** \name BMesh helper functions for selection & hide flushing.
 * \{ */

static bool bm_vert_is_edge_select_any_other(const BMVert *v, const BMEdge *e_first)
{
  const BMEdge *e_iter = e_first;

  /* start by stepping over the current edge */
  while ((e_iter = bmesh_disk_edge_next(e_iter, v)) != e_first) {
    if (BM_elem_flag_test(e_iter, BM_ELEM_SELECT)) {
      return true;
    }
  }
  return false;
}

#if 0













#endif















static bool bm_edge_is_face_select_any_other(BMLoop *l_first)
{
  const BMLoop *l_iter = l_first;

  /* start by stepping over the current face */
  while ((l_iter = l_iter->radial_next) != l_first) {
    if (BM_elem_flag_test(l_iter->f, BM_ELEM_SELECT)) {
      return true;
    }
  }
  return false;
}

#if 0













#endif















/** \} */













































































/* -------------------------------------------------------------------- */
/** \name Select mode flush selection
 * \{ */

struct SelectionFlushChunkData {
  int delta_selection_len;
};
































































































/**
 * Flush down from edges to verts.
 *
 * \note This is not typically needed as settling the selection flushes down.
 */






























/**
 * Flush down from faces to verts & edges.
 *
 * \note This is not typically needed as settling the selection flushes down.
 */




















































































/** \} */









































































void BM_vert_select_set(BMesh *bm, BMVert *v, const bool select)
{
  BLI_assert(v->head.htype == BM_VERT);

  if (BM_elem_flag_test(v, BM_ELEM_HIDDEN)) {
    return;
  }

  if (select) {
    if (!BM_elem_flag_test(v, BM_ELEM_SELECT)) {
      BM_elem_flag_enable(v, BM_ELEM_SELECT);
      bm->totvertsel += 1;
    }
  }
  else {
    if (BM_elem_flag_test(v, BM_ELEM_SELECT)) {
      bm->totvertsel -= 1;
      BM_elem_flag_disable(v, BM_ELEM_SELECT);
    }
  }
}

void BM_edge_select_set(BMesh *bm, BMEdge *e, const bool select)
{
  BLI_assert(e->head.htype == BM_EDGE);

  if (BM_elem_flag_test(e, BM_ELEM_HIDDEN)) {
    return;
  }

  if (select) {
    if (!BM_elem_flag_test(e, BM_ELEM_SELECT)) {
      BM_elem_flag_enable(e, BM_ELEM_SELECT);
      bm->totedgesel += 1;
    }
    BM_vert_select_set(bm, e->v1, true);
    BM_vert_select_set(bm, e->v2, true);
  }
  else {
    if (BM_elem_flag_test(e, BM_ELEM_SELECT)) {
      BM_elem_flag_disable(e, BM_ELEM_SELECT);
      bm->totedgesel -= 1;
    }

    if ((bm->selectmode & SCE_SELECT_VERTEX) == 0) {
      int i;

      /* check if the vert is used by a selected edge */
      for (i = 0; i < 2; i++) {
        BMVert *v = *((&e->v1) + i);
        if (bm_vert_is_edge_select_any_other(v, e) == false) {
          BM_vert_select_set(bm, v, false);
        }
      }
    }
    else {
      BM_vert_select_set(bm, e->v1, false);
      BM_vert_select_set(bm, e->v2, false);
    }
  }
}

void BM_face_select_set(BMesh *bm, BMFace *f, const bool select)
{
  BMLoop *l_iter;
  BMLoop *l_first;

  BLI_assert(f->head.htype == BM_FACE);

  if (BM_elem_flag_test(f, BM_ELEM_HIDDEN)) {
    return;
  }

  if (select) {
    if (!BM_elem_flag_test(f, BM_ELEM_SELECT)) {
      BM_elem_flag_enable(f, BM_ELEM_SELECT);
      bm->totfacesel += 1;
    }

    l_iter = l_first = BM_FACE_FIRST_LOOP(f);
    do {
      BM_vert_select_set(bm, l_iter->v, true);
      BM_edge_select_set(bm, l_iter->e, true);
    } while ((l_iter = l_iter->next) != l_first);
  }
  else {

    if (BM_elem_flag_test(f, BM_ELEM_SELECT)) {
      BM_elem_flag_disable(f, BM_ELEM_SELECT);
      bm->totfacesel -= 1;
    }
    /**
     * \note This allows a temporarily invalid state - where for eg
     * an edge bay be de-selected, but an adjacent face remains selected.
     *
     * Rely on #BM_mesh_select_mode_flush to correct these cases.
     *
     * \note flushing based on mode, see #46494
     */
    if (bm->selectmode & SCE_SELECT_VERTEX) {
      l_iter = l_first = BM_FACE_FIRST_LOOP(f);
      do {
        BM_vert_select_set(bm, l_iter->v, false);
        BM_edge_select_set_noflush(bm, l_iter->e, false);
      } while ((l_iter = l_iter->next) != l_first);
    }
    else {
      /**
       * \note use #BM_edge_select_set_noflush,
       * vertex flushing is handled last.
       */
      if (bm->selectmode & SCE_SELECT_EDGE) {
        l_iter = l_first = BM_FACE_FIRST_LOOP(f);
        do {
          BM_edge_select_set_noflush(bm, l_iter->e, false);
        } while ((l_iter = l_iter->next) != l_first);
      }
      else {
        l_iter = l_first = BM_FACE_FIRST_LOOP(f);
        do {
          if (bm_edge_is_face_select_any_other(l_iter) == false) {
            BM_edge_select_set_noflush(bm, l_iter->e, false);
          }
        } while ((l_iter = l_iter->next) != l_first);
      }

      /* flush down to verts */
      l_iter = l_first = BM_FACE_FIRST_LOOP(f);
      do {
        if (bm_vert_is_edge_select_any_other(l_iter->v, l_iter->e) == false) {
          BM_vert_select_set(bm, l_iter->v, false);
        }
      } while ((l_iter = l_iter->next) != l_first);
    }
  }
}

/* -------------------------------------------------------------------- */
/** \name Non Flushing Versions Element Selection
 * \{ */

void BM_edge_select_set_noflush(BMesh *bm, BMEdge *e, const bool select)
{
  BLI_assert(e->head.htype == BM_EDGE);

  if (BM_elem_flag_test(e, BM_ELEM_HIDDEN)) {
    return;
  }

  if (select) {
    if (!BM_elem_flag_test(e, BM_ELEM_SELECT)) {
      BM_elem_flag_enable(e, BM_ELEM_SELECT);
      bm->totedgesel += 1;
    }
  }
  else {
    if (BM_elem_flag_test(e, BM_ELEM_SELECT)) {
      BM_elem_flag_disable(e, BM_ELEM_SELECT);
      bm->totedgesel -= 1;
    }
  }
}























/** \} */



















































/**
 * counts number of elements with flag enabled/disabled
 */






























































void BM_elem_select_set(BMesh *bm, BMElem *ele, const bool select)
{
  switch (ele->head.htype) {
    case BM_VERT:
      BM_vert_select_set(bm, (BMVert *)ele, select);
      break;
    case BM_EDGE:
      BM_edge_select_set(bm, (BMEdge *)ele, select);
      break;
    case BM_FACE:
      BM_face_select_set(bm, (BMFace *)ele, select);
      break;
    default:
      BLI_assert(0);
      break;
  }
}



















































































































































































































/* --- Macro wrapped functions. --- */






bool _bm_select_history_remove(BMesh *bm, BMHeader *ele)
{
  BMEditSelection *ese = static_cast<BMEditSelection *>(
      BLI_findptr(&bm->selected, ele, offsetof(BMEditSelection, ele)));
  if (ese) {
    BLI_freelinkN(&bm->selected, ese);
    return true;
  }
  return false;
}







































/* --- End macro wrapped functions --- */

void BM_select_history_clear(BMesh *bm)
{
  BLI_freelistN(&bm->selected);
}














































































































































void BM_mesh_elem_hflag_disable_test(BMesh *bm,
                                     const char htype,
                                     const char hflag,
                                     const bool respecthide,
                                     const bool overwrite,
                                     const char hflag_test)
{
  const char iter_types[3] = {BM_VERTS_OF_MESH, BM_EDGES_OF_MESH, BM_FACES_OF_MESH};

  const char flag_types[3] = {BM_VERT, BM_EDGE, BM_FACE};

  const char hflag_nosel = hflag & ~BM_ELEM_SELECT;

  int i;

  BLI_assert((htype & ~BM_ALL_NOLOOP) == 0);

  if (hflag & BM_ELEM_SELECT) {
    BM_select_history_clear(bm);
  }

  if ((htype == (BM_VERT | BM_EDGE | BM_FACE)) && (hflag == BM_ELEM_SELECT) &&
      (respecthide == false) && (hflag_test == 0))
  {
    /* fast path for deselect all, avoid topology loops
     * since we know all will be de-selected anyway. */
    for (i = 0; i < 3; i++) {
      BMIter iter;
      BMElem *ele;

      ele = static_cast<BMElem *>(BM_iter_new(&iter, bm, iter_types[i], nullptr));
      for (; ele; ele = static_cast<BMElem *>(BM_iter_step(&iter))) {
        BM_elem_flag_disable(ele, BM_ELEM_SELECT);
      }
    }

    bm->totvertsel = bm->totedgesel = bm->totfacesel = 0;
  }
  else {
    for (i = 0; i < 3; i++) {
      BMIter iter;
      BMElem *ele;

      if (htype & flag_types[i]) {
        ele = static_cast<BMElem *>(BM_iter_new(&iter, bm, iter_types[i], nullptr));
        for (; ele; ele = static_cast<BMElem *>(BM_iter_step(&iter))) {

          if (UNLIKELY(respecthide && BM_elem_flag_test(ele, BM_ELEM_HIDDEN))) {
            /* pass */
          }
          else if (!hflag_test || BM_elem_flag_test(ele, hflag_test)) {
            if (hflag & BM_ELEM_SELECT) {
              BM_elem_select_set(bm, ele, false);
            }
            BM_elem_flag_disable(ele, hflag);
          }
          else if (overwrite) {
            /* no match! */
            if (hflag & BM_ELEM_SELECT) {
              BM_elem_select_set(bm, ele, true);
            }
            BM_elem_flag_enable(ele, hflag_nosel);
          }
        }
      }
    }
  }
}























































void BM_mesh_elem_hflag_disable_all(BMesh *bm,
                                    const char htype,
                                    const char hflag,
                                    const bool respecthide)
{
  /* call with 0 hflag_test */
  BM_mesh_elem_hflag_disable_test(bm, htype, hflag, respecthide, false, 0);
}










/***************** Mesh Hiding stuff *********** */

/**
 * Hide unless any connected elements are visible.
 * Run this after hiding a connected edge or face.
 */





/**
 * Hide unless any connected elements are visible.
 * Run this after hiding a connected face.
 */



























































































































