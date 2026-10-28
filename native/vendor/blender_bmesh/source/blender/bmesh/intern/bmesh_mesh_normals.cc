/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bmesh
 *
 * BM mesh normal calculation functions.
 *
 * \see mesh_normals.cc for the equivalent #Mesh functionality.
 */

#include "MEM_guardedalloc.h"

#include "DNA_scene_types.h"

#include "BLI_array.hh"
#include "BLI_bitmap.h"
#include "BLI_linklist_stack.h"
#include "BLI_listbase.h"
#include "BLI_math_base.hh"
#include "BLI_math_vector.h"
#include "BLI_task.h"
#include "BLI_task.hh"
#include "BLI_utildefines.h"
#include "BLI_vector.hh"

#include "BKE_customdata.hh"
#include "BKE_editmesh.hh"
#include "BKE_global.hh"
#include "BKE_mesh.hh"

#include "intern/bmesh_private.hh"

using blender::Array;
using blender::float3;
using blender::IndexRange;
using blender::MutableSpan;
using blender::Span;

/* Smooth angle to use when tagging edges is disabled entirely. */
#define EDGE_TAG_FROM_SPLIT_ANGLE_BYPASS -FLT_MAX

static void bm_edge_tag_from_smooth_and_set_sharp(Span<float3> fnos,
                                                  BMEdge *e,
                                                  const float split_angle_cos);
static void bm_edge_tag_from_smooth(Span<float3> fnos, BMEdge *e, const float split_angle_cos);

/* -------------------------------------------------------------------- */
/** \name Update Vertex & Face Normals
 * \{ */

/**
 * Helpers for #BM_mesh_normals_update and #BM_verts_calc_normal_vcos
 */

/* We use that existing internal API flag,
 * assuming no other tool using it would run concurrently to clnors editing. */
#define BM_LNORSPACE_UPDATE _FLAG_MF

struct BMVertsCalcNormalsWithCoordsData {
  /* Read-only data. */
  Span<float3> fnos;
  Span<float3> vcos;

  /* Write data. */
  MutableSpan<float3> vnos;
};

BLI_INLINE void bm_vert_calc_normals_accum_loop(const BMLoop *l_iter,
                                                const float e1diff[3],
                                                const float e2diff[3],
                                                const float f_no[3],
                                                float v_no[3])
{
  /* Calculate the dot product of the two edges that meet at the loop's vertex. */
  /* Edge vectors are calculated from `e->v1` to `e->v2`, so adjust the dot product if one but not
   * both loops actually runs from `e->v2` to `e->v1`. */
  float dotprod = dot_v3v3(e1diff, e2diff);
  if ((l_iter->prev->e->v1 == l_iter->prev->v) ^ (l_iter->e->v1 == l_iter->v)) {
    dotprod = -dotprod;
  }
  const float fac = blender::math::safe_acos_approx(-dotprod);
  /* Shouldn't happen as normalizing edge-vectors cause degenerate values to be zeroed out. */
  BLI_assert(!isnan(fac));
  madd_v3_v3fl(v_no, f_no, fac);
}

static void bm_vert_calc_normals_impl(BMVert *v)
{
  /* NOTE(@ideasman42): Regarding redundant unit-length edge-vector calculation:
   *
   * This functions calculates unit-length edge-vector for every loop edge
   * in practice this means 2x `sqrt` calls per face-corner connected to each vertex.
   *
   * Previously (2.9x and older), the edge vectors were calculated and stored for reuse.
   * However the overhead of did not perform well (~16% slower - single & multi-threaded)
   * when compared with calculating the values as they are needed.
   *
   * For simple grid topologies this function calculates the edge-vectors 4x times.
   * There is some room for improved performance by storing the edge-vectors for reuse locally
   * in this function, reducing the number of redundant `sqrtf` in half (2x instead of 4x).
   * so face loops that share an edge would not calculate it multiple times.
   * From my tests the performance improvements are so small they're difficult to measure,
   * the time saved removing `sqrtf` calls is lost on storing and looking up the information,
   * even in the case of small inline lookup tables.
   *
   * Further, local data structures would need to support cases where
   * stack memory isn't sufficient - adding additional complexity for corner-cases
   * (a vertex that has thousands of connected edges for example).
   * Unless there are important use-cases that benefit from edge-vector caching,
   * keep this simple and calculate ~4x as many edge-vectors.
   *
   * In conclusion, the cost of caching & looking up edge-vectors both globally or per-vertex
   * doesn't save enough time to make it worthwhile.
   */

  float *v_no = v->no;
  zero_v3(v_no);

  BMEdge *e_first = v->e;
  if (e_first != nullptr) {
    float e1diff[3], e2diff[3];
    BMEdge *e_iter = e_first;
    do {
      BMLoop *l_first = e_iter->l;
      if (l_first != nullptr) {
        sub_v3_v3v3(e2diff, e_iter->v1->co, e_iter->v2->co);
        normalize_v3(e2diff);

        BMLoop *l_iter = l_first;
        do {
          if (l_iter->v == v) {
            BMEdge *e_prev = l_iter->prev->e;
            sub_v3_v3v3(e1diff, e_prev->v1->co, e_prev->v2->co);
            normalize_v3(e1diff);

            bm_vert_calc_normals_accum_loop(l_iter, e1diff, e2diff, l_iter->f->no, v_no);
          }
        } while ((l_iter = l_iter->radial_next) != l_first);
      }
    } while ((e_iter = BM_DISK_EDGE_NEXT(e_iter, v)) != e_first);

    if (LIKELY(normalize_v3(v_no) != 0.0f)) {
      return;
    }
  }
  /* Fallback normal. */
  normalize_v3_v3(v_no, v->co);
}

static void bm_vert_calc_normals_cb(void * /*userdata*/,
                                    MempoolIterData *mp_v,
                                    const TaskParallelTLS *__restrict /*tls*/)
{
  BMVert *v = (BMVert *)mp_v;
  bm_vert_calc_normals_impl(v);
}

static void bm_vert_calc_normals_with_coords(BMVert *v, BMVertsCalcNormalsWithCoordsData *data)
{
  /* See #bm_vert_calc_normals_impl note on performance. */
  float *v_no = data->vnos[BM_elem_index_get(v)];
  zero_v3(v_no);

  /* Loop over edges. */
  BMEdge *e_first = v->e;
  if (e_first != nullptr) {
    float e1diff[3], e2diff[3];
    BMEdge *e_iter = e_first;
    do {
      BMLoop *l_first = e_iter->l;
      if (l_first != nullptr) {
        sub_v3_v3v3(e2diff,
                    data->vcos[BM_elem_index_get(e_iter->v1)],
                    data->vcos[BM_elem_index_get(e_iter->v2)]);
        normalize_v3(e2diff);

        BMLoop *l_iter = l_first;
        do {
          if (l_iter->v == v) {
            BMEdge *e_prev = l_iter->prev->e;
            sub_v3_v3v3(e1diff,
                        data->vcos[BM_elem_index_get(e_prev->v1)],
                        data->vcos[BM_elem_index_get(e_prev->v2)]);
            normalize_v3(e1diff);

            bm_vert_calc_normals_accum_loop(
                l_iter, e1diff, e2diff, data->fnos[BM_elem_index_get(l_iter->f)], v_no);
          }
        } while ((l_iter = l_iter->radial_next) != l_first);
      }
    } while ((e_iter = BM_DISK_EDGE_NEXT(e_iter, v)) != e_first);

    if (LIKELY(normalize_v3(v_no) != 0.0f)) {
      return;
    }
  }
  /* Fallback normal. */
  normalize_v3_v3(v_no, data->vcos[BM_elem_index_get(v)]);
}

static void bm_vert_calc_normals_with_coords_cb(void *userdata,
                                                MempoolIterData *mp_v,
                                                const TaskParallelTLS *__restrict /*tls*/)
{
  BMVertsCalcNormalsWithCoordsData *data = static_cast<BMVertsCalcNormalsWithCoordsData *>(
      userdata);
  BMVert *v = (BMVert *)mp_v;
  bm_vert_calc_normals_with_coords(v, data);
}

static void bm_mesh_verts_calc_normals(BMesh *bm,
                                       const Span<float3> fnos,
                                       const Span<float3> vcos,
                                       MutableSpan<float3> vnos)
{
  BM_mesh_elem_index_ensure(bm, BM_FACE | ((!vnos.is_empty() || !vcos.is_empty()) ? BM_VERT : 0));

  TaskParallelSettings settings;
  BLI_parallel_mempool_settings_defaults(&settings);
  settings.use_threading = bm->totvert >= BM_THREAD_LIMIT;

  if (vcos.is_empty()) {
    BM_iter_parallel(bm, BM_VERTS_OF_MESH, bm_vert_calc_normals_cb, nullptr, &settings);
  }
  else {
    BLI_assert(!fnos.is_empty() || !vnos.is_empty());
    BMVertsCalcNormalsWithCoordsData data{};
    data.fnos = fnos;
    data.vcos = vcos;
    data.vnos = vnos;
    BM_iter_parallel(bm, BM_VERTS_OF_MESH, bm_vert_calc_normals_with_coords_cb, &data, &settings);
  }
}

static void bm_face_calc_normals_cb(void * /*userdata*/,
                                    MempoolIterData *mp_f,
                                    const TaskParallelTLS *__restrict /*tls*/)
{
  BMFace *f = (BMFace *)mp_f;

  BM_face_calc_normal(f, f->no);
}

void BM_mesh_normals_update_ex(BMesh *bm, const BMeshNormalsUpdate_Params *params)
{
  if (params->face_normals) {
    /* Calculate all face normals. */
    TaskParallelSettings settings;
    BLI_parallel_mempool_settings_defaults(&settings);
    settings.use_threading = bm->totedge >= BM_THREAD_LIMIT;

    BM_iter_parallel(bm, BM_FACES_OF_MESH, bm_face_calc_normals_cb, nullptr, &settings);
  }

  /* Add weighted face normals to vertices, and normalize vert normals. */
  bm_mesh_verts_calc_normals(bm, {}, {}, {});
}

void BM_mesh_normals_update(BMesh *bm)
{
  BMeshNormalsUpdate_Params params{};
  params.face_normals = true;
  BM_mesh_normals_update_ex(bm, &params);
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Update Vertex & Face Normals (Partial Updates)
 * \{ */




































/** \} */

/* -------------------------------------------------------------------- */
/** \name Update Vertex & Face Normals (Custom Coords)
 * \{ */










/** \} */

/* -------------------------------------------------------------------- */
/** \name Tagging Utility Functions
 * \{ */




































/**
 * Helpers for #BM_mesh_loop_normals_update and #BM_loops_calc_normal_vcos
 */











































/** \} */

/* -------------------------------------------------------------------- */
/** \name Loop Normals Calculation API
 * \{ */

































/**
 * Called for all faces loops.
 *
 * - All loops must have #BM_ELEM_TAG cleared.
 * - Loop indices must be valid.
 *
 * \note When custom normals are present, the order of loops can be important.
 * Loops with lower indices must be passed before loops with higher indices (for each vertex).
 * This is needed since the first loop sets the reference point for the custom normal offsets.
 *
 * \return The number of loops that were handled (for early exit when all have been handled).
 */



















































































































































































































































































































/**
 * We only tag edges that are *really* smooth when the following conditions are met:
 * - The angle between both its polygons normals is below split_angle value.
 * - The edge is tagged as smooth.
 * - The faces of the edge are tagged as smooth.
 * - The faces of the edge have compatible (non-flipped) topological normal (winding),
 *   i.e. both loops on the same edge do not share the same vertex.
 */
BLI_INLINE bool bm_edge_is_smooth_no_angle_test(const BMEdge *e,
                                                const BMLoop *l_a,
                                                const BMLoop *l_b)
{
  BLI_assert(l_a->radial_next == l_b);
  return (
      /* The face is manifold. */
      (l_b->radial_next == l_a) &&
      /* Faces have winding that faces the same way. */
      (l_a->v != l_b->v) &&
      /* The edge is smooth. */
      BM_elem_flag_test(e, BM_ELEM_SMOOTH) &&
      /* Both faces are smooth. */
      BM_elem_flag_test(l_a->f, BM_ELEM_SMOOTH) && BM_elem_flag_test(l_b->f, BM_ELEM_SMOOTH));
}

static void bm_edge_tag_from_smooth(const Span<float3> fnos,
                                    BMEdge *e,
                                    const float split_angle_cos)
{
  BLI_assert(e->l != nullptr);
  BMLoop *l_a = e->l, *l_b = l_a->radial_next;
  bool is_smooth = false;
  if (bm_edge_is_smooth_no_angle_test(e, l_a, l_b)) {
    if (split_angle_cos != -1.0f) {
      const float dot = fnos.is_empty() ? dot_v3v3(l_a->f->no, l_b->f->no) :
                                          dot_v3v3(fnos[BM_elem_index_get(l_a->f)],
                                                   fnos[BM_elem_index_get(l_b->f)]);
      if (dot >= split_angle_cos) {
        is_smooth = true;
      }
    }
    else {
      is_smooth = true;
    }
  }

  /* Perform `BM_elem_flag_set(e, BM_ELEM_TAG, is_smooth)`
   * NOTE: This will be set by multiple threads however it will be set to the same value. */

  /* No need for atomics here as this is a single byte. */
  char *hflag_p = &e->head.hflag;
  if (is_smooth) {
    *hflag_p = *hflag_p | BM_ELEM_TAG;
  }
  else {
    *hflag_p = *hflag_p & ~BM_ELEM_TAG;
  }
}

/**
 * A version of #bm_edge_tag_from_smooth that sets sharp edges
 * when they would be considered smooth but exceed the split angle .
 *
 * \note This doesn't have the same atomic requirement as #bm_edge_tag_from_smooth
 * since it isn't run from multiple threads at once.
 */
static void bm_edge_tag_from_smooth_and_set_sharp(const Span<float3> fnos,
                                                  BMEdge *e,
                                                  const float split_angle_cos)
{
  BLI_assert(e->l != nullptr);
  BMLoop *l_a = e->l, *l_b = l_a->radial_next;
  bool is_smooth = false;
  if (bm_edge_is_smooth_no_angle_test(e, l_a, l_b)) {
    if (split_angle_cos != -1.0f) {
      const float dot = fnos.is_empty() ? dot_v3v3(l_a->f->no, l_b->f->no) :
                                          dot_v3v3(fnos[BM_elem_index_get(l_a->f)],
                                                   fnos[BM_elem_index_get(l_b->f)]);
      if (dot >= split_angle_cos) {
        is_smooth = true;
      }
      else {
        /* Note that we do not care about the other sharp-edge cases
         * (sharp face, non-manifold edge, etc.),
         * only tag edge as sharp when it is due to angle threshold. */
        BM_elem_flag_disable(e, BM_ELEM_SMOOTH);
      }
    }
    else {
      is_smooth = true;
    }
  }

  BM_elem_flag_set(e, BM_ELEM_TAG, is_smooth);
}

/**
 * Operate on all vertices loops.
 * operating on vertices this is needed for multi-threading
 * so there is a guarantee that each thread has isolated loops.
 */






















































































































/**
 * A simplified version of #bm_mesh_loops_calc_normals_for_vert_with_clnors
 * that can operate on loops in any order.
 */






































































/**
 * BMesh version of bke::mesh::normals_calc_corners() in `mesh_evaluate.cc`
 * Will use first clnors_data array, and fallback to cd_loop_clnors_offset
 * (use nullptr and -1 to not use clnors).
 *
 * \note This sets #BM_ELEM_TAG which is used in tool code (e.g. #84426).
 * we could add a low-level API flag for this, see #BM_ELEM_API_FLAG_ENABLE and friends.
 */





























































































struct BMLoopsCalcNormalsWithCoordsData {
  /* Read-only data. */
  Span<float3> vcos;
  Span<float3> fnos;
  BMesh *bm;
  const short (*clnors_data)[2];
  int cd_loop_clnors_offset;
  bool do_rebuild;
  float split_angle_cos;

  /* Output. */
  MutableSpan<float3> r_lnos;
  MLoopNorSpaceArray *r_lnors_spacearr;
};

struct BMLoopsCalcNormalsWithCoords_TLS {
  blender::Vector<blender::float3, 16> *edge_vectors;

  /** Copied from #BMLoopsCalcNormalsWithCoordsData.r_lnors_spacearr when it's not nullptr. */
  MLoopNorSpaceArray *lnors_spacearr;
  MLoopNorSpaceArray lnors_spacearr_buf;
};




































































































































































































/* This threshold is a bit touchy (usual float precision issue), this value seems OK. */
#define LNOR_SPACE_TRIGO_THRESHOLD (1.0f - 1e-4f)

/**
 * Check each current smooth fan (one lnor space per smooth fan!), and if all its
 * matching custom lnors are not (enough) equal, add sharp edges as needed.
 */




























































































/**
 * Assign custom normal data from given normal vectors, averaging normals
 * from one smooth fan as necessary.
 */

















































































/**
 * Compute internal representation of given custom normals (as an array of float[2] or data layer).
 *
 * It also makes sure the mesh matches those custom normals, by marking new sharp edges to split
 * the smooth fans when loop normals for the same vertex are different, or averaging the normals
 * instead, depending on the do_split_fans parameter.
 */






















































































































































/** \} */

/* -------------------------------------------------------------------- */
/** \name Loop Normal Space API
 * \{ */



























































































































































/**
 * Make sure the corner fan (tangent space) style custom normals exist on the BMesh. If free vector
 * custom normals exist, they'll be converted. This is often necessary for BMesh editing tools that
 * don't (yet) support free normals.
 */




































































/** \} */

/* -------------------------------------------------------------------- */
/** \name Loop Normal Edit Data Array API
 *
 * Utilities for creating/freeing #BMLoopNorEditDataArray.
 * \{ */

/**
 * Auxiliary function only used by rebuild to detect if any spaces were not marked as invalid.
 * Reports error if any of the lnor spaces change after rebuilding, meaning that all the possible
 * lnor spaces to be rebuilt were not correctly marked.
 */
#ifndef NDEBUG








































#endif















































































































































/* Mark the individual clnors to be edited, if multiple selection methods are used. */










































































































































































/** \} */

/* -------------------------------------------------------------------- */
/** \name Custom Normals / Vector Layer Conversion
 * \{ */





































































/** \} */
