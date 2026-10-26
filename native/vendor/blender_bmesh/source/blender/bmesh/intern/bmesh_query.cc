/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bmesh
 *
 * This file contains functions for answering common
 * Topological and geometric queries about a mesh, such
 * as, "What is the angle between these two faces?" or,
 * "How many faces are incident upon this vertex?" Tool
 * authors should use the functions in this file instead
 * of inspecting the mesh structure directly.
 */

#include "MEM_guardedalloc.h"

#include "BLI_alloca.h"
#include "BLI_linklist.h"
#include "BLI_math_base.h"
#include "BLI_math_geom.h"
#include "BLI_math_matrix.h"
#include "BLI_math_rotation.h"
#include "BLI_math_vector.h"
#include "BLI_utildefines_stack.h"

#include "BKE_customdata.hh"

#include "bmesh.hh"
#include "intern/bmesh_private.hh"











































































bool BM_vert_pair_share_face_check(BMVert *v_a, BMVert *v_b)
{
  if (v_a->e && v_b->e) {
    BMIter iter;
    BMFace *f;

    BM_ITER_ELEM (f, &iter, v_a, BM_FACES_OF_VERT) {
      if (BM_vert_in_face(v_b, f)) {
        return true;
      }
    }
  }

  return false;
}

































































































































































































bool BM_vert_in_face(BMVert *v, BMFace *f)
{
  BMLoop *l_iter, *l_first;

#ifdef USE_BMESH_HOLES
  BMLoopList *lst;
  for (lst = f->loops.first; lst; lst = lst->next)
#endif
  {
#ifdef USE_BMESH_HOLES
    l_iter = l_first = lst->first;
#else
    l_iter = l_first = f->l_first;
#endif
    do {
      if (l_iter->v == v) {
        return true;
      }
    } while ((l_iter = l_iter->next) != l_first);
  }

  return false;
}











































































































BMLoop *BM_edge_other_loop(BMEdge *e, BMLoop *l)
{
  BMLoop *l_other;

  // BLI_assert(BM_edge_is_manifold(e)); /* Too strict, just check there is another radial face. */
  BLI_assert(e->l && e->l->radial_next != e->l);
  BLI_assert(BM_vert_in_edge(e, l->v));

  l_other = (l->e == e) ? l : l->prev;
  l_other = l_other->radial_next;
  BLI_assert(l_other->e == e);

  if (l_other->v == l->v) {
    /* pass */
  }
  else if (l_other->next->v == l->v) {
    l_other = l_other->next;
  }
  else {
    BLI_assert(0);
  }

  return l_other;
}

BMLoop *BM_vert_step_fan_loop(BMLoop *l, BMEdge **e_step)
{
  BMEdge *e_prev = *e_step;
  BMEdge *e_next;
  if (l->e == e_prev) {
    e_next = l->prev->e;
  }
  else if (l->prev->e == e_prev) {
    e_next = l->e;
  }
  else {
    BLI_assert(0);
    return nullptr;
  }

  if (BM_edge_is_manifold(e_next)) {
    return BM_edge_other_loop((*e_step = e_next), l);
  }
  return nullptr;
}















































float BM_edge_calc_length(const BMEdge *e)
{
  return len_v3v3(e->v1->co, e->v2->co);
}





















bool BM_edge_loop_pair(BMEdge *e, BMLoop **r_la, BMLoop **r_lb)
{
  BMLoop *la, *lb;

  if ((la = e->l) && (lb = la->radial_next) && (la != lb) && (lb->radial_next == la)) {
    *r_la = la;
    *r_lb = lb;
    return true;
  }

  *r_la = nullptr;
  *r_lb = nullptr;
  return false;
}






























































int BM_edge_face_count(const BMEdge *e)
{
  int count = 0;

  if (e->l) {
    BMLoop *l_iter, *l_first;

    l_iter = l_first = e->l;
    do {
      count++;
    } while ((l_iter = l_iter->radial_next) != l_first);
  }

  return count;
}

int BM_edge_face_count_at_most(const BMEdge *e, const int count_max)
{
  int count = 0;

  if (e->l) {
    BMLoop *l_iter, *l_first;

    l_iter = l_first = e->l;
    do {
      count++;
      if (count == count_max) {
        break;
      }
    } while ((l_iter = l_iter->radial_next) != l_first);
  }

  return count;
}





































































































#define LOOP_VISIT _FLAG_WALK
#define EDGE_VISIT _FLAG_WALK









































































#undef LOOP_VISIT
#undef EDGE_VISIT











































































































































































































































bool BM_edge_share_vert_check(BMEdge *e1, BMEdge *e2)
{
  return (e1->v1 == e2->v1 || e1->v1 == e2->v2 || e1->v2 == e2->v1 || e1->v2 == e2->v2);
}

BMVert *BM_edge_share_vert(BMEdge *e1, BMEdge *e2)
{
  BLI_assert(e1 != e2);
  if (BM_vert_in_edge(e2, e1->v1)) {
    return e1->v1;
  }
  if (BM_vert_in_edge(e2, e1->v2)) {
    return e1->v2;
  }
  return nullptr;
}










BMLoop *BM_face_vert_share_loop(BMFace *f, BMVert *v)
{
  BMLoop *l_first;
  BMLoop *l_iter;

  l_iter = l_first = BM_FACE_FIRST_LOOP(f);
  do {
    if (l_iter->v == v) {
      return l_iter;
    }
  } while ((l_iter = l_iter->next) != l_first);

  return nullptr;
}
































































































































































































































































































































































































































/**
 * Returns the edge existing between \a v_a and \a v_b, or nullptr if there isn't one.
 *
 * \note multiple edges may exist between any two vertices, and therefore
 * this function only returns the first one found.
 */
#if 0
BMEdge *BM_edge_exists(BMVert *v_a, BMVert *v_b)
{
  BMIter iter;
  BMEdge *e;

  BLI_assert(v_a != v_b);
  BLI_assert(v_a->head.htype == BM_VERT && v_b->head.htype == BM_VERT);

  BM_ITER_ELEM (e, &iter, v_a, BM_EDGES_OF_VERT) {
    if (e->v1 == v_b || e->v2 == v_b) {
      return e;
    }
  }

  return nullptr;
}
#else
BMEdge *BM_edge_exists(BMVert *v_a, BMVert *v_b)
{
  /* speedup by looping over both edges verts
   * where one vert may connect to many edges but not the other. */

  BMEdge *e_a, *e_b;

  BLI_assert(v_a != v_b);
  BLI_assert(v_a->head.htype == BM_VERT && v_b->head.htype == BM_VERT);

  if ((e_a = v_a->e) && (e_b = v_b->e)) {
    BMEdge *e_a_iter = e_a, *e_b_iter = e_b;

    do {
      if (BM_vert_in_edge(e_a_iter, v_b)) {
        return e_a_iter;
      }
      if (BM_vert_in_edge(e_b_iter, v_a)) {
        return e_b_iter;
      }
    } while (((e_a_iter = bmesh_disk_edge_next(e_a_iter, v_a)) != e_a) &&
             ((e_b_iter = bmesh_disk_edge_next(e_b_iter, v_b)) != e_b));
  }

  return nullptr;
}
#endif

BMEdge *BM_edge_find_double(BMEdge *e)
{
  BMVert *v = e->v1;
  BMVert *v_other = e->v2;

  BMEdge *e_iter;

  e_iter = e;
  while ((e_iter = bmesh_disk_edge_next(e_iter, v)) != e) {
    if (UNLIKELY(BM_vert_in_edge(e_iter, v_other))) {
      return e_iter;
    }
  }

  return nullptr;
}















BMFace *BM_face_exists(BMVert *const *varr, int len)
{
  if (varr[0]->e) {
    BMEdge *e_iter, *e_first;
    e_iter = e_first = varr[0]->e;

    /* would normally use BM_LOOPS_OF_VERT, but this runs so often,
     * its faster to iterate on the data directly */
    do {
      if (e_iter->l) {
        BMLoop *l_iter_radial, *l_first_radial;
        l_iter_radial = l_first_radial = e_iter->l;

        do {
          if ((l_iter_radial->v == varr[0]) && (l_iter_radial->f->len == len)) {
            /* the fist 2 verts match, now check the remaining (len - 2) faces do too
             * winding isn't known, so check in both directions */
            int i_walk = 2;

            if (l_iter_radial->next->v == varr[1]) {
              BMLoop *l_walk = l_iter_radial->next->next;
              do {
                if (l_walk->v != varr[i_walk]) {
                  break;
                }
              } while ((void)(l_walk = l_walk->next), ++i_walk != len);
            }
            else if (l_iter_radial->prev->v == varr[1]) {
              BMLoop *l_walk = l_iter_radial->prev->prev;
              do {
                if (l_walk->v != varr[i_walk]) {
                  break;
                }
              } while ((void)(l_walk = l_walk->prev), ++i_walk != len);
            }

            if (i_walk == len) {
              return l_iter_radial->f;
            }
          }
        } while ((l_iter_radial = l_iter_radial->radial_next) != l_first_radial);
      }
    } while ((e_iter = BM_DISK_EDGE_NEXT(e_iter, varr[0])) != e_first);
  }

  return nullptr;
}

BMFace *BM_face_find_double(BMFace *f)
{
  BMLoop *l_first = BM_FACE_FIRST_LOOP(f);
  for (BMLoop *l_iter = l_first->radial_next; l_first != l_iter; l_iter = l_iter->radial_next) {
    if (l_iter->f->len == l_first->f->len) {
      if (l_iter->v == l_first->v) {
        BMLoop *l_a = l_first, *l_b = l_iter, *l_b_init = l_iter;
        do {
          if (l_a->e != l_b->e) {
            break;
          }
        } while (((void)(l_a = l_a->next), (l_b = l_b->next)) != l_b_init);
        if (l_b == l_b_init) {
          return l_iter->f;
        }
      }
      else {
        BMLoop *l_a = l_first, *l_b = l_iter, *l_b_init = l_iter;
        do {
          if (l_a->e != l_b->e) {
            break;
          }
        } while (((void)(l_a = l_a->prev), (l_b = l_b->next)) != l_b_init);
        if (l_b == l_b_init) {
          return l_iter->f;
        }
      }
    }
  }
  return nullptr;
}























































































































































































































































































































































bool BM_face_is_normal_valid(const BMFace *f)
{
  const float eps = 0.0001f;
  float no[3];

  BM_face_calc_normal(f, no);
  return len_squared_v3v3(no, f->no) < (eps * eps);
}

/**
 * Use to accumulate volume calculation for faces with consistent winding.
 *
 * Use double precision since this is prone to float precision error, see #73295.
 */

























































































































































































































































































































































































































































