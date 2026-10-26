/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bmesh
 *
 * Functions to abstract looping over bmesh data structures.
 *
 * See: bmesh_iterators_inlin.c too, some functions are here for speed reasons.
 */

#include "MEM_guardedalloc.h"

#include "bmesh.hh"
#include "intern/bmesh_structure.hh"

const char bm_iter_itype_htype_map[BM_ITYPE_MAX] = {
    '\0',
    BM_VERT, /* BM_VERTS_OF_MESH */
    BM_EDGE, /* BM_EDGES_OF_MESH */
    BM_FACE, /* BM_FACES_OF_MESH */
    BM_EDGE, /* BM_EDGES_OF_VERT */
    BM_FACE, /* BM_FACES_OF_VERT */
    BM_LOOP, /* BM_LOOPS_OF_VERT */
    BM_VERT, /* BM_VERTS_OF_EDGE */
    BM_FACE, /* BM_FACES_OF_EDGE */
    BM_VERT, /* BM_VERTS_OF_FACE */
    BM_EDGE, /* BM_EDGES_OF_FACE */
    BM_LOOP, /* BM_LOOPS_OF_FACE */
    BM_LOOP, /* BM_LOOPS_OF_LOOP */
    BM_LOOP, /* BM_LOOPS_OF_EDGE */
};
















































































































































































































































































































/**
 * Notes on iterator implementation:
 *
 * Iterators keep track of the next element in a sequence.
 * When a step() callback is invoked the current value of 'next'
 * is stored to be returned later and the next variable is incremented.
 *
 * When the end of a sequence is reached, next should always equal nullptr
 *
 * The 'bmiter__' prefix is used because these are used in
 * bmesh_iterators_inine.c but should otherwise be seen as
 * private.
 */

/*
 * VERT OF MESH CALLBACKS
 */

/* see bug #36923 for why we need this,
 * allow adding but not removing, this isn't _totally_ safe since
 * you could add/remove within the same loop, but catches common cases
 */
#ifndef NDEBUG
#  define USE_IMMUTABLE_ASSERT
#endif

void bmiter__elem_of_mesh_begin(BMIter__elem_of_mesh *iter)
{
#ifdef USE_IMMUTABLE_ASSERT
  ((BMIter *)iter)->count = BLI_mempool_len(iter->pooliter.pool);
#endif
  BLI_mempool_iternew(iter->pooliter.pool, &iter->pooliter);
}

void *bmiter__elem_of_mesh_step(BMIter__elem_of_mesh *iter)
{
#ifdef USE_IMMUTABLE_ASSERT
  BLI_assert(((BMIter *)iter)->count <= BLI_mempool_len(iter->pooliter.pool));
#endif
  return BLI_mempool_iterstep(&iter->pooliter);
}

#ifdef USE_IMMUTABLE_ASSERT
#  undef USE_IMMUTABLE_ASSERT
#endif

/*
 * EDGE OF VERT CALLBACKS
 */

void bmiter__edge_of_vert_begin(BMIter__edge_of_vert *iter)
{
  if (iter->vdata->e) {
    iter->e_first = iter->vdata->e;
    iter->e_next = iter->vdata->e;
  }
  else {
    iter->e_first = nullptr;
    iter->e_next = nullptr;
  }
}

void *bmiter__edge_of_vert_step(BMIter__edge_of_vert *iter)
{
  BMEdge *e_curr = iter->e_next;

  if (iter->e_next) {
    iter->e_next = bmesh_disk_edge_next(iter->e_next, iter->vdata);
    if (iter->e_next == iter->e_first) {
      iter->e_next = nullptr;
    }
  }

  return e_curr;
}

/*
 * FACE OF VERT CALLBACKS
 */

void bmiter__face_of_vert_begin(BMIter__face_of_vert *iter)
{
  ((BMIter *)iter)->count = bmesh_disk_facevert_count(iter->vdata);
  if (((BMIter *)iter)->count) {
    iter->l_first = bmesh_disk_faceloop_find_first(iter->vdata->e, iter->vdata);
    iter->e_first = iter->l_first->e;
    iter->e_next = iter->e_first;
    iter->l_next = iter->l_first;
  }
  else {
    iter->l_first = iter->l_next = nullptr;
    iter->e_first = iter->e_next = nullptr;
  }
}
void *bmiter__face_of_vert_step(BMIter__face_of_vert *iter)
{
  BMLoop *l_curr = iter->l_next;

  if (((BMIter *)iter)->count && iter->l_next) {
    ((BMIter *)iter)->count--;
    iter->l_next = bmesh_radial_faceloop_find_next(iter->l_next, iter->vdata);
    if (iter->l_next == iter->l_first) {
      iter->e_next = bmesh_disk_faceedge_find_next(iter->e_next, iter->vdata);
      iter->l_first = bmesh_radial_faceloop_find_first(iter->e_next->l, iter->vdata);
      iter->l_next = iter->l_first;
    }
  }

  if (!((BMIter *)iter)->count) {
    iter->l_next = nullptr;
  }

  return l_curr ? l_curr->f : nullptr;
}

/*
 * LOOP OF VERT CALLBACKS
 */

void bmiter__loop_of_vert_begin(BMIter__loop_of_vert *iter)
{
  ((BMIter *)iter)->count = bmesh_disk_facevert_count(iter->vdata);
  if (((BMIter *)iter)->count) {
    iter->l_first = bmesh_disk_faceloop_find_first(iter->vdata->e, iter->vdata);
    iter->e_first = iter->l_first->e;
    iter->e_next = iter->e_first;
    iter->l_next = iter->l_first;
  }
  else {
    iter->l_first = iter->l_next = nullptr;
    iter->e_first = iter->e_next = nullptr;
  }
}
void *bmiter__loop_of_vert_step(BMIter__loop_of_vert *iter)
{
  BMLoop *l_curr = iter->l_next;

  if (((BMIter *)iter)->count) {
    ((BMIter *)iter)->count--;
    iter->l_next = bmesh_radial_faceloop_find_next(iter->l_next, iter->vdata);
    if (iter->l_next == iter->l_first) {
      iter->e_next = bmesh_disk_faceedge_find_next(iter->e_next, iter->vdata);
      iter->l_first = bmesh_radial_faceloop_find_first(iter->e_next->l, iter->vdata);
      iter->l_next = iter->l_first;
    }
  }

  if (!((BMIter *)iter)->count) {
    iter->l_next = nullptr;
  }

  /* nullptr on finish */
  return l_curr;
}

/*
 * LOOP OF EDGE CALLBACKS
 */

void bmiter__loop_of_edge_begin(BMIter__loop_of_edge *iter)
{
  iter->l_first = iter->l_next = iter->edata->l;
}

void *bmiter__loop_of_edge_step(BMIter__loop_of_edge *iter)
{
  BMLoop *l_curr = iter->l_next;

  if (iter->l_next) {
    iter->l_next = iter->l_next->radial_next;
    if (iter->l_next == iter->l_first) {
      iter->l_next = nullptr;
    }
  }

  /* nullptr on finish */
  return l_curr;
}

/*
 * LOOP OF LOOP CALLBACKS
 */

void bmiter__loop_of_loop_begin(BMIter__loop_of_loop *iter)
{
  iter->l_first = iter->ldata;
  iter->l_next = iter->l_first->radial_next;

  if (iter->l_next == iter->l_first) {
    iter->l_next = nullptr;
  }
}

void *bmiter__loop_of_loop_step(BMIter__loop_of_loop *iter)
{
  BMLoop *l_curr = iter->l_next;

  if (iter->l_next) {
    iter->l_next = iter->l_next->radial_next;
    if (iter->l_next == iter->l_first) {
      iter->l_next = nullptr;
    }
  }

  /* nullptr on finish */
  return l_curr;
}

/*
 * FACE OF EDGE CALLBACKS
 */

void bmiter__face_of_edge_begin(BMIter__face_of_edge *iter)
{
  iter->l_first = iter->l_next = iter->edata->l;
}

void *bmiter__face_of_edge_step(BMIter__face_of_edge *iter)
{
  BMLoop *current = iter->l_next;

  if (iter->l_next) {
    iter->l_next = iter->l_next->radial_next;
    if (iter->l_next == iter->l_first) {
      iter->l_next = nullptr;
    }
  }

  return current ? current->f : nullptr;
}

/*
 * VERTS OF EDGE CALLBACKS
 */

void bmiter__vert_of_edge_begin(BMIter__vert_of_edge *iter)
{
  ((BMIter *)iter)->count = 0;
}

void *bmiter__vert_of_edge_step(BMIter__vert_of_edge *iter)
{
  switch (((BMIter *)iter)->count++) {
    case 0:
      return iter->edata->v1;
    case 1:
      return iter->edata->v2;
    default:
      return nullptr;
  }
}

/*
 * VERT OF FACE CALLBACKS
 */

void bmiter__vert_of_face_begin(BMIter__vert_of_face *iter)
{
  iter->l_first = iter->l_next = BM_FACE_FIRST_LOOP(iter->pdata);
}

void *bmiter__vert_of_face_step(BMIter__vert_of_face *iter)
{
  BMLoop *l_curr = iter->l_next;

  if (iter->l_next) {
    iter->l_next = iter->l_next->next;
    if (iter->l_next == iter->l_first) {
      iter->l_next = nullptr;
    }
  }

  return l_curr ? l_curr->v : nullptr;
}

/*
 * EDGE OF FACE CALLBACKS
 */

void bmiter__edge_of_face_begin(BMIter__edge_of_face *iter)
{
  iter->l_first = iter->l_next = BM_FACE_FIRST_LOOP(iter->pdata);
}

void *bmiter__edge_of_face_step(BMIter__edge_of_face *iter)
{
  BMLoop *l_curr = iter->l_next;

  if (iter->l_next) {
    iter->l_next = iter->l_next->next;
    if (iter->l_next == iter->l_first) {
      iter->l_next = nullptr;
    }
  }

  return l_curr ? l_curr->e : nullptr;
}

/*
 * LOOP OF FACE CALLBACKS
 */

void bmiter__loop_of_face_begin(BMIter__loop_of_face *iter)
{
  iter->l_first = iter->l_next = BM_FACE_FIRST_LOOP(iter->pdata);
}

void *bmiter__loop_of_face_step(BMIter__loop_of_face *iter)
{
  BMLoop *l_curr = iter->l_next;

  if (iter->l_next) {
    iter->l_next = iter->l_next->next;
    if (iter->l_next == iter->l_first) {
      iter->l_next = nullptr;
    }
  }

  return l_curr;
}
