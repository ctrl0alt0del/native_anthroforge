/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bmesh
 *
 * Core BMesh functions for adding, removing BMesh elements.
 */

#include "MEM_guardedalloc.h"

#include "BLI_alloca.h"
#include "BLI_linklist_stack.h"
#include "BLI_math_vector.h"
#include "BLI_utildefines_stack.h"
#include "BLI_vector.hh"

#include "BKE_customdata.hh"
#include "BKE_mesh.hh"

#include "bmesh.hh"
#include "intern/bmesh_private.hh"

using blender::Vector;

/* use so valgrinds memcheck alerts us when undefined index is used.
 * TESTING ONLY! */
// #define USE_DEBUG_INDEX_MEMCHECK

#ifdef USE_DEBUG_INDEX_MEMCHECK
#  define DEBUG_MEMCHECK_INDEX_INVALIDATE(ele) \
    { \
      int undef_idx; \
      BM_elem_index_set(ele, undef_idx); /* set_ok_invalid */ \
    } \
    (void)0

#endif

/* -------------------------------------------------------------------- */
/** \name Face Partial Overlap Helpers
 * \{ */

/**
 * Utilities to check two faces have overlapping vertices.
 * Useful to check if collapsing or splicing would create a duplicate face.
 *
 * Check loops have matching vertices over a partial span
 * over `l_a` -> `l_a_end` & `l_a` -> `l_a_end` (inclusive).
 */










































/**
 * A version of #bm_face_pair_overlap_check_subset_same_winding
 * that walks over `l_b` in the reverse direction.
 */









































/** \} */

BMVert *BM_vert_create(BMesh *bm,
                       const float co[3],
                       const BMVert *v_example,
                       const eBMCreateFlag create_flag)
{
  BMVert *v = static_cast<BMVert *>(BLI_mempool_alloc(bm->vpool));

  BLI_assert((v_example == nullptr) || (v_example->head.htype == BM_VERT));
  BLI_assert(!(create_flag & 1));

  /* --- assign all members --- */
  v->head.data = nullptr;

#ifdef USE_DEBUG_INDEX_MEMCHECK
  DEBUG_MEMCHECK_INDEX_INVALIDATE(v);
#else
  BM_elem_index_set(v, -1); /* set_ok_invalid */
#endif

  v->head.htype = BM_VERT;
  v->head.hflag = 0;
  v->head.api_flag = 0;

  /* allocate flags */
  if (bm->use_toolflags) {
    ((BMVert_OFlag *)v)->oflags = static_cast<BMFlagLayer *>(
        bm->vtoolflagpool ? BLI_mempool_calloc(bm->vtoolflagpool) : nullptr);
  }

  /* 'v->no' is handled by BM_elem_attrs_copy */
  if (co) {
    copy_v3_v3(v->co, co);
  }
  else {
    zero_v3(v->co);
  }
  /* 'v->no' set below */

  v->e = nullptr;
  /* --- done --- */

  /* disallow this flag for verts - its meaningless */
  BLI_assert((create_flag & BM_CREATE_NO_DOUBLE) == 0);

  /* may add to middle of the pool */
  bm->elem_index_dirty |= BM_VERT;
  bm->elem_table_dirty |= BM_VERT;
  bm->spacearr_dirty |= BM_SPACEARR_DIRTY_ALL;

  bm->totvert++;

  if (!(create_flag & BM_CREATE_SKIP_CD)) {
    if (v_example) {
      int *keyi;

      /* handles 'v->no' too */
      BM_elem_attrs_copy(bm, v_example, v);

      /* Exception: don't copy the original shape-key index. */
      keyi = static_cast<int *>(CustomData_bmesh_get(&bm->vdata, v->head.data, CD_SHAPE_KEYINDEX));
      if (keyi) {
        *keyi = ORIGINDEX_NONE;
      }
    }
    else {
      CustomData_bmesh_set_default(&bm->vdata, &v->head.data);
      zero_v3(v->no);
    }
  }
  else {
    if (v_example) {
      copy_v3_v3(v->no, v_example->no);
    }
    else {
      zero_v3(v->no);
    }
  }

  BM_CHECK_ELEMENT(v);

  return v;
}

BMEdge *BM_edge_create(
    BMesh *bm, BMVert *v1, BMVert *v2, const BMEdge *e_example, const eBMCreateFlag create_flag)
{
  BMEdge *e;

  BLI_assert(v1 != v2);
  BLI_assert(v1->head.htype == BM_VERT && v2->head.htype == BM_VERT);
  BLI_assert((e_example == nullptr) || (e_example->head.htype == BM_EDGE));
  BLI_assert(!(create_flag & 1));

  if ((create_flag & BM_CREATE_NO_DOUBLE) && (e = BM_edge_exists(v1, v2))) {
    return e;
  }

  e = static_cast<BMEdge *>(BLI_mempool_alloc(bm->epool));

  /* --- assign all members --- */
  e->head.data = nullptr;

#ifdef USE_DEBUG_INDEX_MEMCHECK
  DEBUG_MEMCHECK_INDEX_INVALIDATE(e);
#else
  BM_elem_index_set(e, -1); /* set_ok_invalid */
#endif

  e->head.htype = BM_EDGE;
  e->head.hflag = BM_ELEM_SMOOTH;
  e->head.api_flag = 0;

  /* allocate flags */
  if (bm->use_toolflags) {
    ((BMEdge_OFlag *)e)->oflags = static_cast<BMFlagLayer *>(
        bm->etoolflagpool ? BLI_mempool_calloc(bm->etoolflagpool) : nullptr);
  }

  e->v1 = v1;
  e->v2 = v2;
  e->l = nullptr;

  memset(&e->v1_disk_link, 0, sizeof(BMDiskLink));
  memset(&e->v2_disk_link, 0, sizeof(BMDiskLink));

  /* --- done --- */

  bmesh_disk_edge_append(e, e->v1);
  bmesh_disk_edge_append(e, e->v2);

  /* may add to middle of the pool */
  bm->elem_index_dirty |= BM_EDGE;
  bm->elem_table_dirty |= BM_EDGE;
  bm->spacearr_dirty |= BM_SPACEARR_DIRTY_ALL;

  bm->totedge++;

  if (!(create_flag & BM_CREATE_SKIP_CD)) {
    if (e_example) {
      BM_elem_attrs_copy(bm, e_example, e);
    }
    else {
      CustomData_bmesh_set_default(&bm->edata, &e->head.data);
    }
  }

  BM_CHECK_ELEMENT(e);

  return e;
}

/**
 * \note In most cases a \a l_example should be nullptr,
 * since this is a low level API and we shouldn't attempt to be clever and guess what's intended.
 * In cases where copying adjacent loop-data is useful, see #BM_face_copy_shared.
 */
static BMLoop *bm_loop_create(BMesh *bm,
                              BMVert *v,
                              BMEdge *e,
                              BMFace *f,
                              const BMLoop *l_example,
                              const eBMCreateFlag create_flag)
{
  BMLoop *l = nullptr;

  l = static_cast<BMLoop *>(BLI_mempool_alloc(bm->lpool));

  BLI_assert((l_example == nullptr) || (l_example->head.htype == BM_LOOP));
  BLI_assert(!(create_flag & 1));

#ifndef NDEBUG
  if (l_example) {
    /* ensure passing a loop is either sharing the same vertex, or entirely disconnected
     * use to catch mistake passing in loop offset-by-one. */
    BLI_assert((v == l_example->v) || !ELEM(v, l_example->prev->v, l_example->next->v));
  }
#endif

  /* --- assign all members --- */
  l->head.data = nullptr;

#ifdef USE_DEBUG_INDEX_MEMCHECK
  DEBUG_MEMCHECK_INDEX_INVALIDATE(l);
#else
  BM_elem_index_set(l, -1); /* set_ok_invalid */
#endif

  l->head.htype = BM_LOOP;
  l->head.hflag = 0;
  l->head.api_flag = 0;

  l->v = v;
  l->e = e;
  l->f = f;

  l->radial_next = nullptr;
  l->radial_prev = nullptr;
  l->next = nullptr;
  l->prev = nullptr;
  /* --- done --- */

  /* may add to middle of the pool */
  bm->elem_index_dirty |= BM_LOOP;
  bm->spacearr_dirty |= BM_SPACEARR_DIRTY_ALL;

  bm->totloop++;

  if (!(create_flag & BM_CREATE_SKIP_CD)) {
    if (l_example) {
      /* no need to copy attrs, just handle customdata */
      CustomData_bmesh_copy_block(bm->ldata, l_example->head.data, &l->head.data);
    }
    else {
      CustomData_bmesh_set_default(&bm->ldata, &l->head.data);
    }
  }

  return l;
}

static BMLoop *bm_face_boundary_add(
    BMesh *bm, BMFace *f, BMVert *startv, BMEdge *starte, const eBMCreateFlag create_flag)
{
#ifdef USE_BMESH_HOLES
  BMLoopList *lst = BLI_mempool_calloc(bm->looplistpool);
#endif
  BMLoop *l = bm_loop_create(bm, startv, starte, f, nullptr /* starte->l */, create_flag);

  bmesh_radial_loop_append(starte, l);

#ifdef USE_BMESH_HOLES
  lst->first = lst->last = l;
  BLI_addtail(&f->loops, lst);
#else
  f->l_first = l;
#endif

  return l;
}

static BMFace *bm_face_copy_impl(BMesh *bm_dst,
                                 BMFace *f,
                                 const bool copy_verts,
                                 const bool copy_edges)
{
  BMVert **verts = BLI_array_alloca(verts, f->len);
  BMEdge **edges = BLI_array_alloca(edges, f->len);
  BMLoop *l_iter;
  BMLoop *l_first;
  BMFace *f_copy;
  int i;

  l_iter = l_first = BM_FACE_FIRST_LOOP(f);
  i = 0;
  do {
    if (copy_verts) {
      verts[i] = BM_vert_create(bm_dst, l_iter->v->co, l_iter->v, BM_CREATE_NOP);
    }
    else {
      verts[i] = l_iter->v;
    }
    i++;
  } while ((l_iter = l_iter->next) != l_first);

  l_iter = l_first = BM_FACE_FIRST_LOOP(f);
  i = 0;
  do {
    if (copy_edges) {
      BMVert *v1, *v2;

      if (l_iter->e->v1 == verts[i]) {
        v1 = verts[i];
        v2 = verts[(i + 1) % f->len];
      }
      else {
        v2 = verts[i];
        v1 = verts[(i + 1) % f->len];
      }

      edges[i] = BM_edge_create(bm_dst, v1, v2, l_iter->e, BM_CREATE_NOP);
    }
    else {
      edges[i] = l_iter->e;
    }
    i++;
  } while ((l_iter = l_iter->next) != l_first);

  f_copy = BM_face_create(bm_dst, verts, edges, f->len, nullptr, BM_CREATE_SKIP_CD);

  return f_copy;
}

BMFace *BM_face_copy(BMesh *bm_dst,
                     const BMCustomDataCopyMap &cd_face_map,
                     const BMCustomDataCopyMap &cd_loop_map,
                     BMFace *f,
                     const bool copy_verts,
                     const bool copy_edges)
{
  BMFace *f_copy = bm_face_copy_impl(bm_dst, f, copy_verts, copy_edges);

  /* Copy custom-data. */
  BM_elem_attrs_copy(bm_dst, cd_face_map, f, f_copy);

  BMLoop *l_first = BM_FACE_FIRST_LOOP(f);
  BMLoop *l_copy = BM_FACE_FIRST_LOOP(f_copy);
  BMLoop *l_iter = l_first;
  do {
    BM_elem_attrs_copy(bm_dst, cd_loop_map, l_iter, l_copy);
    l_copy = l_copy->next;
  } while ((l_iter = l_iter->next) != l_first);
  return f_copy;
}

BMFace *BM_face_copy(BMesh *bm_dst, BMFace *f, const bool copy_verts, const bool copy_edges)
{
  BMFace *f_copy = bm_face_copy_impl(bm_dst, f, copy_verts, copy_edges);

  /* Copy custom-data. */
  BM_elem_attrs_copy(bm_dst, f, f_copy);

  BMLoop *l_first = BM_FACE_FIRST_LOOP(f);
  BMLoop *l_copy = BM_FACE_FIRST_LOOP(f_copy);
  BMLoop *l_iter = l_first;
  do {
    BM_elem_attrs_copy(bm_dst, l_iter, l_copy);
    l_copy = l_copy->next;
  } while ((l_iter = l_iter->next) != l_first);
  return f_copy;
}

/**
 * only create the face, since this calloc's the length is initialized to 0,
 * leave adding loops to the caller.
 *
 * \note Caller needs to handle customdata.
 */
BLI_INLINE BMFace *bm_face_create__internal(BMesh *bm)
{
  BMFace *f;

  f = static_cast<BMFace *>(BLI_mempool_alloc(bm->fpool));

  /* --- assign all members --- */
  f->head.data = nullptr;
#ifdef USE_DEBUG_INDEX_MEMCHECK
  DEBUG_MEMCHECK_INDEX_INVALIDATE(f);
#else
  BM_elem_index_set(f, -1); /* set_ok_invalid */
#endif

  f->head.htype = BM_FACE;
  f->head.hflag = 0;
  f->head.api_flag = 0;

  /* allocate flags */
  if (bm->use_toolflags) {
    ((BMFace_OFlag *)f)->oflags = static_cast<BMFlagLayer *>(
        bm->ftoolflagpool ? BLI_mempool_calloc(bm->ftoolflagpool) : nullptr);
  }

#ifdef USE_BMESH_HOLES
  BLI_listbase_clear(&f->loops);
#else
  f->l_first = nullptr;
#endif
  f->len = 0;
  /* caller must initialize */
  // zero_v3(f->no);
  f->mat_nr = 0;
  /* --- done --- */

  /* may add to middle of the pool */
  bm->elem_index_dirty |= BM_FACE;
  bm->elem_table_dirty |= BM_FACE;
  bm->spacearr_dirty |= BM_SPACEARR_DIRTY_ALL;

  bm->totface++;

#ifdef USE_BMESH_HOLES
  f->totbounds = 0;
#endif

  return f;
}

BMFace *BM_face_create(BMesh *bm,
                       BMVert *const *verts,
                       BMEdge *const *edges,
                       const int len,
                       const BMFace *f_example,
                       const eBMCreateFlag create_flag)
{
  BMFace *f = nullptr;
  BMLoop *l, *startl, *lastl;
  int i;

  BLI_assert((f_example == nullptr) || (f_example->head.htype == BM_FACE));
  BLI_assert(!(create_flag & 1));

  if (len == 0) {
    /* just return nullptr for now */
    return nullptr;
  }

  if (create_flag & BM_CREATE_NO_DOUBLE) {
    /* Check if face already exists */
    f = BM_face_exists(verts, len);
    if (f != nullptr) {
      return f;
    }
  }

  f = bm_face_create__internal(bm);

  startl = lastl = bm_face_boundary_add(bm, f, verts[0], edges[0], create_flag);

  for (i = 1; i < len; i++) {
    l = bm_loop_create(bm, verts[i], edges[i], f, nullptr /* edges[i]->l */, create_flag);

    bmesh_radial_loop_append(edges[i], l);

    l->prev = lastl;
    lastl->next = l;
    lastl = l;
  }

  startl->prev = lastl;
  lastl->next = startl;

  f->len = len;

  if (!(create_flag & BM_CREATE_SKIP_CD)) {
    if (f_example) {
      BM_elem_attrs_copy(bm, f_example, f);
    }
    else {
      CustomData_bmesh_set_default(&bm->pdata, &f->head.data);
      zero_v3(f->no);
    }
  }
  else {
    if (f_example) {
      copy_v3_v3(f->no, f_example->no);
    }
    else {
      zero_v3(f->no);
    }
  }

  BM_CHECK_ELEMENT(f);

  return f;
}

BMFace *BM_face_create_verts(BMesh *bm,
                             BMVert **vert_arr,
                             const int len,
                             const BMFace *f_example,
                             const eBMCreateFlag create_flag,
                             const bool create_edges)
{
  BMEdge **edge_arr = BLI_array_alloca(edge_arr, len);

  if (create_edges) {
    BM_edges_from_verts_ensure(bm, edge_arr, vert_arr, len);
  }
  else {
    if (BM_edges_from_verts(edge_arr, vert_arr, len) == false) {
      return nullptr;
    }
  }

  return BM_face_create(bm, vert_arr, edge_arr, len, f_example, create_flag);
}

#ifndef NDEBUG

enum BMeshElemErrorFlag {
  IS_NULL = (1 << 0),
  IS_WRONG_TYPE = (1 << 1),

  IS_VERT_WRONG_EDGE_TYPE = (1 << 2),

  IS_EDGE_NULL_DISK_LINK = (1 << 3),
  IS_EDGE_WRONG_LOOP_TYPE = (1 << 4),
  IS_EDGE_WRONG_FACE_TYPE = (1 << 5),
  IS_EDGE_NULL_RADIAL_LINK = (1 << 6),
  IS_EDGE_ZERO_FACE_LENGTH = (1 << 7),

  IS_LOOP_WRONG_FACE_TYPE = (1 << 8),
  IS_LOOP_WRONG_EDGE_TYPE = (1 << 9),
  IS_LOOP_WRONG_VERT_TYPE = (1 << 10),
  IS_LOOP_VERT_NOT_IN_EDGE = (1 << 11),
  IS_LOOP_NULL_CYCLE_LINK = (1 << 12),
  IS_LOOP_ZERO_FACE_LENGTH = (1 << 13),
  IS_LOOP_WRONG_FACE_LENGTH = (1 << 14),
  IS_LOOP_WRONG_RADIAL_LENGTH = (1 << 15),

  IS_FACE_NULL_LOOP = (1 << 16),
  IS_FACE_WRONG_LOOP_FACE = (1 << 17),
  IS_FACE_NULL_EDGE = (1 << 18),
  IS_FACE_NULL_VERT = (1 << 19),
  IS_FACE_LOOP_VERT_NOT_IN_EDGE = (1 << 20),
  IS_FACE_LOOP_WRONG_RADIAL_LENGTH = (1 << 21),
  IS_FACE_LOOP_WRONG_DISK_LENGTH = (1 << 22),
  IS_FACE_LOOP_DUPE_LOOP = (1 << 23),
  IS_FACE_LOOP_DUPE_VERT = (1 << 24),
  IS_FACE_LOOP_DUPE_EDGE = (1 << 25),
  IS_FACE_WRONG_LENGTH = (1 << 26),
};
ENUM_OPERATORS(BMeshElemErrorFlag, IS_FACE_WRONG_LENGTH)

int bmesh_elem_check(void *element, const char htype)
{
  BMHeader *head = static_cast<BMHeader *>(element);
  BMeshElemErrorFlag err = BMeshElemErrorFlag(0);

  if (!element) {
    return IS_NULL;
  }

  if (head->htype != htype) {
    return IS_WRONG_TYPE;
  }

  switch (htype) {
    case BM_VERT: {
      BMVert *v = static_cast<BMVert *>(element);
      if (v->e && v->e->head.htype != BM_EDGE) {
        err |= IS_VERT_WRONG_EDGE_TYPE;
      }
      break;
    }
    case BM_EDGE: {
      BMEdge *e = static_cast<BMEdge *>(element);
      if (e->v1_disk_link.prev == nullptr || e->v2_disk_link.prev == nullptr ||
          e->v1_disk_link.next == nullptr || e->v2_disk_link.next == nullptr)
      {
        err |= IS_EDGE_NULL_DISK_LINK;
      }

      if (e->l && e->l->head.htype != BM_LOOP) {
        err |= IS_EDGE_WRONG_LOOP_TYPE;
      }
      if (e->l && e->l->f->head.htype != BM_FACE) {
        err |= IS_EDGE_WRONG_FACE_TYPE;
      }
      if (e->l && (e->l->radial_next == nullptr || e->l->radial_prev == nullptr)) {
        err |= IS_EDGE_NULL_RADIAL_LINK;
      }
      if (e->l && e->l->f->len <= 0) {
        err |= IS_EDGE_ZERO_FACE_LENGTH;
      }
      break;
    }
    case BM_LOOP: {
      BMLoop *l = static_cast<BMLoop *>(element);
      BMLoop *l2;
      int i;

      if (l->f->head.htype != BM_FACE) {
        err |= IS_LOOP_WRONG_FACE_TYPE;
      }
      if (l->e->head.htype != BM_EDGE) {
        err |= IS_LOOP_WRONG_EDGE_TYPE;
      }
      if (l->v->head.htype != BM_VERT) {
        err |= IS_LOOP_WRONG_VERT_TYPE;
      }
      if (!BM_vert_in_edge(l->e, l->v)) {
        fprintf(stderr,
                "%s: fatal bmesh error (vert not in edge)! (bmesh internal error)\n",
                __func__);
        err |= IS_LOOP_VERT_NOT_IN_EDGE;
      }

      if (l->radial_next == nullptr || l->radial_prev == nullptr) {
        err |= IS_LOOP_NULL_CYCLE_LINK;
      }
      if (l->f->len <= 0) {
        err |= IS_LOOP_ZERO_FACE_LENGTH;
      }

      /* validate boundary loop -- invalid for hole loops, of course,
       * but we won't be allowing those for a while yet */
      l2 = l;
      i = 0;
      do {
        if (i >= BM_NGON_MAX) {
          break;
        }

        i++;
      } while ((l2 = l2->next) != l);

      if (i != l->f->len || l2 != l) {
        err |= IS_LOOP_WRONG_FACE_LENGTH;
      }

      if (!bmesh_radial_validate(bmesh_radial_length(l), l)) {
        err |= IS_LOOP_WRONG_RADIAL_LENGTH;
      }

      break;
    }
    case BM_FACE: {
      BMFace *f = static_cast<BMFace *>(element);
      BMLoop *l_iter;
      BMLoop *l_first;
      int len = 0;

#  ifdef USE_BMESH_HOLES
      if (!f->loops.first)
#  else
      if (!f->l_first)
#  endif
      {
        err |= IS_FACE_NULL_LOOP;
      }
      l_iter = l_first = BM_FACE_FIRST_LOOP(f);
      do {
        if (l_iter->f != f) {
          fprintf(stderr,
                  "%s: loop inside one face points to another! (bmesh internal error)\n",
                  __func__);
          err |= IS_FACE_WRONG_LOOP_FACE;
        }

        if (!l_iter->e) {
          err |= IS_FACE_NULL_EDGE;
        }
        if (!l_iter->v) {
          err |= IS_FACE_NULL_VERT;
        }
        if (l_iter->e && l_iter->v) {
          if (!BM_vert_in_edge(l_iter->e, l_iter->v) ||
              !BM_vert_in_edge(l_iter->e, l_iter->next->v))
          {
            err |= IS_FACE_LOOP_VERT_NOT_IN_EDGE;
          }

          if (!bmesh_radial_validate(bmesh_radial_length(l_iter), l_iter)) {
            err |= IS_FACE_LOOP_WRONG_RADIAL_LENGTH;
          }

          if (bmesh_disk_count_at_most(l_iter->v, 2) < 2) {
            err |= IS_FACE_LOOP_WRONG_DISK_LENGTH;
          }
        }

        /* check for duplicates */
        if (BM_ELEM_API_FLAG_TEST(l_iter, _FLAG_ELEM_CHECK)) {
          err |= IS_FACE_LOOP_DUPE_LOOP;
        }
        BM_ELEM_API_FLAG_ENABLE(l_iter, _FLAG_ELEM_CHECK);
        if (l_iter->v) {
          if (BM_ELEM_API_FLAG_TEST(l_iter->v, _FLAG_ELEM_CHECK)) {
            err |= IS_FACE_LOOP_DUPE_VERT;
          }
          BM_ELEM_API_FLAG_ENABLE(l_iter->v, _FLAG_ELEM_CHECK);
        }
        if (l_iter->e) {
          if (BM_ELEM_API_FLAG_TEST(l_iter->e, _FLAG_ELEM_CHECK)) {
            err |= IS_FACE_LOOP_DUPE_EDGE;
          }
          BM_ELEM_API_FLAG_ENABLE(l_iter->e, _FLAG_ELEM_CHECK);
        }

        len++;
      } while ((l_iter = l_iter->next) != l_first);

      /* cleanup duplicates flag */
      l_iter = l_first = BM_FACE_FIRST_LOOP(f);
      do {
        BM_ELEM_API_FLAG_DISABLE(l_iter, _FLAG_ELEM_CHECK);
        if (l_iter->v) {
          BM_ELEM_API_FLAG_DISABLE(l_iter->v, _FLAG_ELEM_CHECK);
        }
        if (l_iter->e) {
          BM_ELEM_API_FLAG_DISABLE(l_iter->e, _FLAG_ELEM_CHECK);
        }
      } while ((l_iter = l_iter->next) != l_first);

      if (len != f->len) {
        err |= IS_FACE_WRONG_LENGTH;
      }
      break;
    }
    default:
      BLI_assert(0);
      break;
  }

  BMESH_ASSERT(err == 0);

  return err;
}

#endif /* !NDEBUG */

/**
 * low level function, only frees the vert,
 * doesn't change or adjust surrounding geometry
 */
static void bm_kill_only_vert(BMesh *bm, BMVert *v)
{
  bm->totvert--;
  bm->elem_index_dirty |= BM_VERT;
  bm->elem_table_dirty |= BM_VERT;
  bm->spacearr_dirty |= BM_SPACEARR_DIRTY_ALL;

  BM_select_history_remove(bm, v);

  if (v->head.data) {
    CustomData_bmesh_free_block(&bm->vdata, &v->head.data);
  }

  if (bm->vtoolflagpool) {
    BLI_mempool_free(bm->vtoolflagpool, ((BMVert_OFlag *)v)->oflags);
  }
  BLI_mempool_free(bm->vpool, v);
}

/**
 * low level function, only frees the edge,
 * doesn't change or adjust surrounding geometry
 */
static void bm_kill_only_edge(BMesh *bm, BMEdge *e)
{
  bm->totedge--;
  bm->elem_index_dirty |= BM_EDGE;
  bm->elem_table_dirty |= BM_EDGE;
  bm->spacearr_dirty |= BM_SPACEARR_DIRTY_ALL;

  BM_select_history_remove(bm, (BMElem *)e);

  if (e->head.data) {
    CustomData_bmesh_free_block(&bm->edata, &e->head.data);
  }

  if (bm->etoolflagpool) {
    BLI_mempool_free(bm->etoolflagpool, ((BMEdge_OFlag *)e)->oflags);
  }
  BLI_mempool_free(bm->epool, e);
}

/**
 * low level function, only frees the face,
 * doesn't change or adjust surrounding geometry
 */
static void bm_kill_only_face(BMesh *bm, BMFace *f)
{
  if (bm->act_face == f) {
    bm->act_face = nullptr;
  }

  bm->totface--;
  bm->elem_index_dirty |= BM_FACE;
  bm->elem_table_dirty |= BM_FACE;
  bm->spacearr_dirty |= BM_SPACEARR_DIRTY_ALL;

  BM_select_history_remove(bm, (BMElem *)f);

  if (f->head.data) {
    CustomData_bmesh_free_block(&bm->pdata, &f->head.data);
  }

  if (bm->ftoolflagpool) {
    BLI_mempool_free(bm->ftoolflagpool, ((BMFace_OFlag *)f)->oflags);
  }
  BLI_mempool_free(bm->fpool, f);
}

/**
 * low level function, only frees the loop,
 * doesn't change or adjust surrounding geometry
 */
static void bm_kill_only_loop(BMesh *bm, BMLoop *l)
{
  bm->totloop--;
  bm->elem_index_dirty |= BM_LOOP;
  bm->spacearr_dirty |= BM_SPACEARR_DIRTY_ALL;

  if (l->head.data) {
    CustomData_bmesh_free_block(&bm->ldata, &l->head.data);
  }

  BLI_mempool_free(bm->lpool, l);
}


















void BM_face_verts_kill(BMesh *bm, BMFace *f)
{
  BMVert **verts = BLI_array_alloca(verts, f->len);
  BMLoop *l_iter;
  BMLoop *l_first;
  int i = 0;

  l_iter = l_first = BM_FACE_FIRST_LOOP(f);
  do {
    verts[i++] = l_iter->v;
  } while ((l_iter = l_iter->next) != l_first);

  for (i = 0; i < f->len; i++) {
    BM_vert_kill(bm, verts[i]);
  }
}

void BM_face_kill(BMesh *bm, BMFace *f)
{
#ifdef USE_BMESH_HOLES
  BMLoopList *ls, *ls_next;
#endif

#ifdef NDEBUG
  /* check length since we may be removing degenerate faces */
  if (f->len >= 3) {
    BM_CHECK_ELEMENT(f);
  }
#endif

#ifdef USE_BMESH_HOLES
  for (ls = f->loops.first; ls; ls = ls_next)
#else
  if (f->l_first)
#endif
  {
    BMLoop *l_iter, *l_next, *l_first;

#ifdef USE_BMESH_HOLES
    ls_next = ls->next;
    l_iter = l_first = ls->first;
#else
    l_iter = l_first = f->l_first;
#endif

    do {
      l_next = l_iter->next;

      bmesh_radial_loop_remove(l_iter->e, l_iter);
      bm_kill_only_loop(bm, l_iter);

    } while ((l_iter = l_next) != l_first);

#ifdef USE_BMESH_HOLES
    BLI_mempool_free(bm->looplistpool, ls);
#endif
  }

  bm_kill_only_face(bm, f);
}
























































void BM_edge_kill(BMesh *bm, BMEdge *e)
{
  while (e->l) {
    BM_face_kill(bm, e->l->f);
  }

  bmesh_disk_edge_remove(e, e->v1);
  bmesh_disk_edge_remove(e, e->v2);

  bm_kill_only_edge(bm, e);
}

void BM_vert_kill(BMesh *bm, BMVert *v)
{
  while (v->e) {
    BM_edge_kill(bm, v->e);
  }

  bm_kill_only_vert(bm, v);
}

/********** private disk and radial cycle functions ********** */

/**
 * return the length of the face, should always equal \a l->f->len
 */
























































































static void bm_elements_systag_enable(void *veles, int tot, const char api_flag)
{
  BMHeader **eles = static_cast<BMHeader **>(veles);
  int i;

  for (i = 0; i < tot; i++) {
    BM_ELEM_API_FLAG_ENABLE((BMElemF *)eles[i], api_flag);
  }
}

static void bm_elements_systag_disable(void *veles, int tot, const char api_flag)
{
  BMHeader **eles = static_cast<BMHeader **>(veles);
  int i;

  for (i = 0; i < tot; i++) {
    BM_ELEM_API_FLAG_DISABLE((BMElemF *)eles[i], api_flag);
  }
}

static int bm_loop_systag_count_radial(BMLoop *l, const char api_flag)
{
  BMLoop *l_iter = l;
  int i = 0;
  do {
    i += BM_ELEM_API_FLAG_TEST(l_iter->f, api_flag) ? 1 : 0;
  } while ((l_iter = l_iter->radial_next) != l);

  return i;
}

















/**
 * Return true when the vertex is manifold,
 * attached to faces which are all flagged.
 */
static bool bm_vert_is_manifold_flagged(BMVert *v, const char api_flag)
{
  BMEdge *e = v->e;

  if (!e) {
    return false;
  }

  do {
    BMLoop *l = e->l;

    if (!l) {
      return false;
    }

    if (BM_edge_is_boundary(l->e)) {
      return false;
    }

    do {
      if (!BM_ELEM_API_FLAG_TEST(l->f, api_flag)) {
        return false;
      }
    } while ((l = l->radial_next) != e->l);
  } while ((e = bmesh_disk_edge_next(e, v)) != v->e);

  return true;
}

/* Mid-level Topology Manipulation Functions */

BMFace *BM_faces_join(BMesh *bm, BMFace **faces, int totface, const bool do_del, BMFace **r_double)
{
  BMFace *f, *f_new;
#ifdef USE_BMESH_HOLES
  BMLoopList *lst;
  ListBase holes = {nullptr, nullptr};
#endif
  BMLoop *l_iter;
  BMLoop *l_first;
  BMVert *v1 = nullptr, *v2 = nullptr;
  int i;
  const int cd_loop_mdisp_offset = CustomData_get_offset(&bm->ldata, CD_MDISPS);
  BMFace *f_existing;
  const bool had_active_face = (bm->act_face != nullptr);

  /* Initialize the return value if provided. This ensures it will be nullptr if the join fails. */
  if (r_double) {
    *r_double = nullptr;
  }

  if (UNLIKELY(!totface)) {
    BMESH_ASSERT(0);
    return nullptr;
  }

  if (totface == 1) {
    return faces[0];
  }

  bm_elements_systag_enable(faces, totface, _FLAG_JF);

  Vector<BMEdge *, BM_DEFAULT_NGON_STACK_SIZE> edges;
  Vector<BMEdge *, BM_DEFAULT_NGON_STACK_SIZE> deledges;
  Vector<BMVert *, BM_DEFAULT_NGON_STACK_SIZE> delverts;

  for (i = 0; i < totface; i++) {
    f = faces[i];
    l_iter = l_first = BM_FACE_FIRST_LOOP(f);
    do {
      int rlen = bm_loop_systag_count_radial(l_iter, _FLAG_JF);

      if (rlen > 2) {
        /* Input faces do not form a contiguous manifold region.
         * Clean up flags and fail. */
        bm_elements_systag_disable(faces, totface, _FLAG_JF);
        return nullptr;
      }
      if (rlen == 1) {
        edges.append(l_iter->e);

        if (!v1) {
          v1 = l_iter->v;
          v2 = BM_edge_other_vert(l_iter->e, l_iter->v);
        }
      }
      else if (rlen == 2) {
        const bool d1 = bm_vert_is_manifold_flagged(l_iter->e->v1, _FLAG_JF);
        const bool d2 = bm_vert_is_manifold_flagged(l_iter->e->v2, _FLAG_JF);

        if (!d1 && !d2 && !BM_ELEM_API_FLAG_TEST(l_iter->e, _FLAG_JF)) {
          /* don't remove an edge it makes up the side of another face
           * else this will remove the face as well - campbell */
          if (!BM_edge_face_count_is_over(l_iter->e, 2)) {
            if (do_del) {
              deledges.append(l_iter->e);
            }
            BM_ELEM_API_FLAG_ENABLE(l_iter->e, _FLAG_JF);
          }
        }
        else {
          if (d1 && !BM_ELEM_API_FLAG_TEST(l_iter->e->v1, _FLAG_JF)) {
            if (do_del) {
              delverts.append(l_iter->e->v1);
            }
            BM_ELEM_API_FLAG_ENABLE(l_iter->e->v1, _FLAG_JF);
          }

          if (d2 && !BM_ELEM_API_FLAG_TEST(l_iter->e->v2, _FLAG_JF)) {
            if (do_del) {
              delverts.append(l_iter->e->v2);
            }
            BM_ELEM_API_FLAG_ENABLE(l_iter->e->v2, _FLAG_JF);
          }
        }
      }
    } while ((l_iter = l_iter->next) != l_first);

#ifdef USE_BMESH_HOLES
    for (lst = f->loops.first; lst; lst = lst->next) {
      if (lst == f->loops.first) {
        continue;
      }

      BLI_remlink(&f->loops, lst);
      BLI_addtail(&holes, lst);
    }
#endif
  }

  /* create region face */
  f_new = !edges.is_empty() ?
              BM_face_create_ngon(
                  bm, v1, v2, edges.data(), edges.size(), faces[0], BM_CREATE_NOP) :
              nullptr;
  if (UNLIKELY(f_new == nullptr)) {
    /* Invalid boundary region to join faces
     * Clean up flags and fail */
    bm_elements_systag_disable(faces, totface, _FLAG_JF);
    return nullptr;
  }

  /* If a new face was created, check whether it is a double of an existing face. */
  f_existing = BM_face_find_double(f_new);
  if (f_existing) {

    /* Return the double to the calling function if that was requested. */
    if (r_double) {
      *r_double = f_existing;
    }

    /* Otherwise, automatically reuse the existing face. */
    else {
      BM_face_kill(bm, f_new);
      f_new = f_existing;
    }
  }

  bool reusing_face = (f_existing && r_double == nullptr);

  /* If we are *not* reusing an existing face, we need to transfer data from the faces being joined
   * to the newly created joined face. */
  if (LIKELY(reusing_face == false)) {

    /* copy over loop data */
    l_iter = l_first = BM_FACE_FIRST_LOOP(f_new);
    do {
      BMLoop *l2 = l_iter->radial_next;

      do {
        if (BM_ELEM_API_FLAG_TEST(l2->f, _FLAG_JF)) {
          break;
        }
        l2 = l2->radial_next;
      } while (l2 != l_iter);

      if (l2 != l_iter) {
        /* loops share an edge, shared vert depends on winding */
        if (l2->v != l_iter->v) {
          l2 = l2->next;
        }
        BLI_assert(l_iter->v == l2->v);

        BM_elem_attrs_copy(bm, l2, l_iter);
      }
    } while ((l_iter = l_iter->next) != l_first);

#ifdef USE_BMESH_HOLES
    /* add holes */
    BLI_movelisttolist(&f_new->loops, &holes);

    /* update loop face pointer */
    for (lst = f_new->loops.first; lst; lst = lst->next) {
      l_iter = l_first = lst->first;
      do {
        l_iter->f = f_new;
      } while ((l_iter = l_iter->next) != l_first);
    }
#endif

    /* handle multi-res data */
    if (cd_loop_mdisp_offset != -1) {
      float f_center[3];
      float (*faces_center)[3] = BLI_array_alloca(faces_center, totface);

      BM_face_calc_center_median(f_new, f_center);
      for (i = 0; i < totface; i++) {
        BM_face_calc_center_median(faces[i], faces_center[i]);
      }

      l_iter = l_first = BM_FACE_FIRST_LOOP(f_new);
      do {
        for (i = 0; i < totface; i++) {
          BM_loop_interp_multires_ex(
              bm, l_iter, faces[i], f_center, faces_center[i], cd_loop_mdisp_offset);
        }
      } while ((l_iter = l_iter->next) != l_first);
    }
  }

  /* Clean up the internal flags. */
  bm_elements_systag_disable(faces, totface, _FLAG_JF);
  BM_ELEM_API_FLAG_DISABLE(f_new, _FLAG_JF);

  if (do_del) {
    /* If `do_del`, delete all the edges and verts that were identified while walking the mesh. */
    for (BMEdge *edge : deledges) {
      BM_edge_kill(bm, edge);
    }

    for (BMVert *vert : delverts) {
      BM_vert_kill(bm, vert);
    }
  }
  else {
    /* Otherwise, delete only the faces that were merged
     * (do not leave the mesh with both the old and new faces). */
    for (i = 0; i < totface; i++) {
      BM_face_kill(bm, faces[i]);
    }
  }

  /* If the mesh started with an active face, but no longer has one, then the active face was one
   * of the faces that was joined then deleted. Set the active face to preserve it. */
  if (had_active_face && bm->act_face == nullptr) {
    bm->act_face = f_new;
  }

  BM_CHECK_ELEMENT(f_new);
  return f_new;
}

static BMFace *bm_face_create__sfme(BMesh *bm, BMFace *f_example)
{
  BMFace *f;
#ifdef USE_BMESH_HOLES
  BMLoopList *lst;
#endif

  f = bm_face_create__internal(bm);

#ifdef USE_BMESH_HOLES
  lst = BLI_mempool_calloc(bm->looplistpool);
  BLI_addtail(&f->loops, lst);
#endif

#ifdef USE_BMESH_HOLES
  f->totbounds = 1;
#endif

  BM_elem_attrs_copy(bm, f_example, f);

  return f;
}

BMFace *bmesh_kernel_split_face_make_edge(BMesh *bm,
                                          BMFace *f,
                                          BMLoop *l_v1,
                                          BMLoop *l_v2,
                                          BMLoop **r_l,
#ifdef USE_BMESH_HOLES
                                          ListBase *holes,
#endif
                                          BMEdge *e_example,
                                          const bool no_double)
{
#ifdef USE_BMESH_HOLES
  BMLoopList *lst, *lst2;
#else
  int first_loop_f1;
#endif

  BMFace *f2;
  BMLoop *l_iter, *l_first;
  BMLoop *l_f1 = nullptr, *l_f2 = nullptr;
  BMEdge *e;
  BMVert *v1 = l_v1->v, *v2 = l_v2->v;
  int f1len, f2len;

  BLI_assert(f == l_v1->f && f == l_v2->f);

  /* allocate new edge between v1 and v2 */
  e = BM_edge_create(bm, v1, v2, e_example, no_double ? BM_CREATE_NO_DOUBLE : BM_CREATE_NOP);

  f2 = bm_face_create__sfme(bm, f);
  l_f1 = bm_loop_create(bm, v2, e, f, l_v2, eBMCreateFlag(0));
  l_f2 = bm_loop_create(bm, v1, e, f2, l_v1, eBMCreateFlag(0));

  l_f1->prev = l_v2->prev;
  l_f2->prev = l_v1->prev;
  l_v2->prev->next = l_f1;
  l_v1->prev->next = l_f2;

  l_f1->next = l_v1;
  l_f2->next = l_v2;
  l_v1->prev = l_f1;
  l_v2->prev = l_f2;

#ifdef USE_BMESH_HOLES
  lst = f->loops.first;
  lst2 = f2->loops.first;

  lst2->first = lst2->last = l_f2;
  lst->first = lst->last = l_f1;
#else
  /* find which of the faces the original first loop is in */
  l_iter = l_first = l_f1;
  first_loop_f1 = 0;
  do {
    if (l_iter == f->l_first) {
      first_loop_f1 = 1;
    }
  } while ((l_iter = l_iter->next) != l_first);

  if (first_loop_f1) {
    /* Original first loop was in f1, find a suitable first loop for f2
     * which is as similar as possible to f1. the order matters for tools
     * such as dupli-faces. */
    if (f->l_first->prev == l_f1) {
      f2->l_first = l_f2->prev;
    }
    else if (f->l_first->next == l_f1) {
      f2->l_first = l_f2->next;
    }
    else {
      f2->l_first = l_f2;
    }
  }
  else {
    /* original first loop was in f2, further do same as above */
    f2->l_first = f->l_first;

    if (f->l_first->prev == l_f2) {
      f->l_first = l_f1->prev;
    }
    else if (f->l_first->next == l_f2) {
      f->l_first = l_f1->next;
    }
    else {
      f->l_first = l_f1;
    }
  }
#endif

  /* validate both loop */
  /* I don't know how many loops are supposed to be in each face at this point! FIXME */

  /* go through all of f2's loops and make sure they point to it properly */
  l_iter = l_first = BM_FACE_FIRST_LOOP(f2);
  f2len = 0;
  do {
    l_iter->f = f2;
    f2len++;
  } while ((l_iter = l_iter->next) != l_first);

  /* link up the new loops into the new edges radial */
  bmesh_radial_loop_append(e, l_f1);
  bmesh_radial_loop_append(e, l_f2);

  f2->len = f2len;

  f1len = 0;
  l_iter = l_first = BM_FACE_FIRST_LOOP(f);
  do {
    f1len++;
  } while ((l_iter = l_iter->next) != l_first);

  f->len = f1len;

  if (r_l) {
    *r_l = l_f2;
  }

#ifdef USE_BMESH_HOLES
  if (holes) {
    BLI_movelisttolist(&f2->loops, holes);
  }
  else {
    /* this code is not significant until holes actually work */
    // printf("WARNING: call to split face euler without holes argument; holes will be tossed.\n");
    for (lst = f->loops.last; lst != f->loops.first; lst = lst2) {
      lst2 = lst->prev;
      BLI_mempool_free(bm->looplistpool, lst);
    }
  }
#endif

  BM_CHECK_ELEMENT(e);
  BM_CHECK_ELEMENT(f);
  BM_CHECK_ELEMENT(f2);

  return f2;
}

BMVert *bmesh_kernel_split_edge_make_vert(BMesh *bm, BMVert *tv, BMEdge *e, BMEdge **r_e)
{
  BMLoop *l_next;
  BMEdge *e_new;
  BMVert *v_new, *v_old;
#ifndef NDEBUG
  int valence1, valence2;
  bool edok;
  int i;
#endif

  BLI_assert(BM_vert_in_edge(e, tv) != false);

  v_old = BM_edge_other_vert(e, tv);

#ifndef NDEBUG
  valence1 = bmesh_disk_count(v_old);
  valence2 = bmesh_disk_count(tv);
#endif

  /* order of 'e_new' verts should match 'e'
   * (so extruded faces don't flip) */
  v_new = BM_vert_create(bm, tv->co, tv, BM_CREATE_NOP);
  e_new = BM_edge_create(bm, tv, v_new, e, BM_CREATE_NOP);

  bmesh_disk_edge_remove(e_new, tv);
  bmesh_disk_edge_remove(e_new, v_new);

  bmesh_disk_vert_replace(e, v_new, tv);

  /* add e_new to v_new's disk cycle */
  bmesh_disk_edge_append(e_new, v_new);

  /* add e_new to tv's disk cycle */
  bmesh_disk_edge_append(e_new, tv);

#ifndef NDEBUG
  /* verify disk cycles */
  edok = bmesh_disk_validate(valence1, v_old->e, v_old);
  BMESH_ASSERT(edok != false);
  edok = bmesh_disk_validate(valence2, tv->e, tv);
  BMESH_ASSERT(edok != false);
  edok = bmesh_disk_validate(2, v_new->e, v_new);
  BMESH_ASSERT(edok != false);
#endif

  /* Split the radial cycle if present */
  l_next = e->l;
  e->l = nullptr;
  if (l_next) {
    BMLoop *l_new, *l;
#ifndef NDEBUG
    int radlen = bmesh_radial_length(l_next);
#endif
    bool is_first = true;

    /* Take the next loop. Remove it from radial. Split it. Append to appropriate radials */
    while (l_next) {
      l = l_next;
      l->f->len++;
      l_next = l_next != l_next->radial_next ? l_next->radial_next : nullptr;
      bmesh_radial_loop_unlink(l);

      l_new = bm_loop_create(bm, nullptr, nullptr, l->f, l, eBMCreateFlag(0));
      l_new->prev = l;
      l_new->next = l->next;
      l_new->prev->next = l_new;
      l_new->next->prev = l_new;
      l_new->v = v_new;

      /* assign the correct edge to the correct loop */
      if (BM_verts_in_edge(l_new->v, l_new->next->v, e)) {
        l_new->e = e;
        l->e = e_new;

        /* append l into e_new's rad cycle */
        if (is_first) {
          is_first = false;
          l->radial_next = l->radial_prev = nullptr;
        }

        bmesh_radial_loop_append(l_new->e, l_new);
        bmesh_radial_loop_append(l->e, l);
      }
      else if (BM_verts_in_edge(l_new->v, l_new->next->v, e_new)) {
        l_new->e = e_new;
        l->e = e;

        /* append l into e_new's rad cycle */
        if (is_first) {
          is_first = false;
          l->radial_next = l->radial_prev = nullptr;
        }

        bmesh_radial_loop_append(l_new->e, l_new);
        bmesh_radial_loop_append(l->e, l);
      }
    }

#ifndef NDEBUG
    /* verify length of radial cycle */
    edok = bmesh_radial_validate(radlen, e->l);
    BMESH_ASSERT(edok != false);
    edok = bmesh_radial_validate(radlen, e_new->l);
    BMESH_ASSERT(edok != false);

    /* verify loop->v and loop->next->v pointers for e */
    for (i = 0, l = e->l; i < radlen; i++, l = l->radial_next) {
      BMESH_ASSERT(l->e == e);
      // BMESH_ASSERT(l->radial_next == l);
      BMESH_ASSERT(!(l->prev->e != e_new && l->next->e != e_new));

      edok = BM_verts_in_edge(l->v, l->next->v, e);
      BMESH_ASSERT(edok != false);
      BMESH_ASSERT(l->v != l->next->v);
      BMESH_ASSERT(l->e != l->next->e);

      /* verify loop cycle for kloop->f */
      BM_CHECK_ELEMENT(l);
      BM_CHECK_ELEMENT(l->v);
      BM_CHECK_ELEMENT(l->e);
      BM_CHECK_ELEMENT(l->f);
    }
    /* verify loop->v and loop->next->v pointers for e_new */
    for (i = 0, l = e_new->l; i < radlen; i++, l = l->radial_next) {
      BMESH_ASSERT(l->e == e_new);
      // BMESH_ASSERT(l->radial_next == l);
      BMESH_ASSERT(!(l->prev->e != e && l->next->e != e));
      edok = BM_verts_in_edge(l->v, l->next->v, e_new);
      BMESH_ASSERT(edok != false);
      BMESH_ASSERT(l->v != l->next->v);
      BMESH_ASSERT(l->e != l->next->e);

      BM_CHECK_ELEMENT(l);
      BM_CHECK_ELEMENT(l->v);
      BM_CHECK_ELEMENT(l->e);
      BM_CHECK_ELEMENT(l->f);
    }
#endif
  }

  BM_CHECK_ELEMENT(e_new);
  BM_CHECK_ELEMENT(v_new);
  BM_CHECK_ELEMENT(v_old);
  BM_CHECK_ELEMENT(e);
  BM_CHECK_ELEMENT(tv);

  if (r_e) {
    *r_e = e_new;
  }
  return v_new;
}






















































































































































































































































































































































































































































































































































































































bool BM_vert_splice(BMesh *bm, BMVert *v_dst, BMVert *v_src)
{
  BMEdge *e;

  /* verts already spliced */
  if (v_src == v_dst) {
    return false;
  }

  BLI_assert(BM_vert_pair_share_face_check(v_src, v_dst) == false);

  /* move all the edges from 'v_src' disk to 'v_dst' */
  while ((e = v_src->e)) {
    bmesh_edge_vert_swap(e, v_dst, v_src);
    BLI_assert(e->v1 != e->v2);
  }

  BM_CHECK_ELEMENT(v_src);
  BM_CHECK_ELEMENT(v_dst);

  /* 'v_src' is unused now, and can be killed */
  BM_vert_kill(bm, v_src);

  return true;
}

/* -------------------------------------------------------------------- */
/** \name BM_vert_separate, bmesh_kernel_vert_separate and friends
 * \{ */

/* BM_edge_face_count(e) >= 1 */


















































































































/**
 * Utility function for #BM_vert_separate
 *
 * Takes a list of edges, which have been split from their original.
 *
 * Any edges which failed to split off in #bmesh_kernel_vert_separate
 * will be merged back into the original edge.
 *
 * \param edges_separate:
 * A list-of-lists, each list is from a single original edge (the first edge is the original),
 * Check for duplicates (not just with the first) but between all.
 * This is O(n2) but radial edges are very rarely >2 and almost never >~10.
 *
 * \note typically its best to avoid creating the data in the first place,
 * but inspecting all loops connectivity is quite involved.
 *
 * \note this function looks like it could become slow,
 * but in common cases its only going to iterate a few times.
 */





















































































































/** \} */

bool BM_edge_splice(BMesh *bm, BMEdge *e_dst, BMEdge *e_src)
{
  BMLoop *l;

  if (!BM_vert_in_edge(e_src, e_dst->v1) || !BM_vert_in_edge(e_src, e_dst->v2)) {
    /* not the same vertices can't splice */

    /* the caller should really make sure this doesn't happen ever
     * so assert on release builds */
    BLI_assert(0);

    return false;
  }

  while (e_src->l) {
    l = e_src->l;
    BLI_assert(BM_vert_in_edge(e_dst, l->v));
    BLI_assert(BM_vert_in_edge(e_dst, l->next->v));
    bmesh_radial_loop_remove(e_src, l);
    bmesh_radial_loop_append(e_dst, l);
  }

  BLI_assert(bmesh_radial_length(e_src->l) == 0);

  BM_CHECK_ELEMENT(e_src);
  BM_CHECK_ELEMENT(e_dst);

  /* removes from disks too */
  BM_edge_kill(bm, e_src);

  return true;
}































































































































































































































































































void bmesh_face_swap_data(BMFace *f_a, BMFace *f_b)
{
  BMLoop *l_iter, *l_first;

  BLI_assert(f_a != f_b);

  l_iter = l_first = BM_FACE_FIRST_LOOP(f_a);
  do {
    l_iter->f = f_b;
  } while ((l_iter = l_iter->next) != l_first);

  l_iter = l_first = BM_FACE_FIRST_LOOP(f_b);
  do {
    l_iter->f = f_a;
  } while ((l_iter = l_iter->next) != l_first);

  std::swap((*f_a), (*f_b));

  /* swap back */
  std::swap(f_a->head.data, f_b->head.data);
  std::swap(f_a->head.index, f_b->head.index);
}
