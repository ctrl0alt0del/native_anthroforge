/* SPDX-FileCopyrightText: 2007 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bmesh
 *
 * Functions for interpolating data across the surface of a mesh.
 */

#include "MEM_guardedalloc.h"

#include "DNA_meshdata_types.h"

#include "BLI_alloca.h"
#include "BLI_linklist.h"
#include "BLI_math_geom.h"
#include "BLI_math_matrix.h"
#include "BLI_math_vector.h"
#include "BLI_memarena.h"
#include "BLI_task.h"

#include "BKE_attribute.h"
#include "BKE_attribute.hh"
#include "BKE_attribute_legacy_convert.hh"
#include "BKE_customdata.hh"
#include "BKE_multires.hh"

#include "bmesh.hh"
#include "intern/bmesh_private.hh"

using blender::StringRef;

/* edge and vertex share, currently there's no need to have different logic */
static void bm_data_interp_from_elem(CustomData *data_layer,
                                     const BMElem *ele_src_1,
                                     const BMElem *ele_src_2,
                                     BMElem *ele_dst,
                                     const float fac)
{
  if (ele_src_1->head.data && ele_src_2->head.data) {
    /* first see if we can avoid interpolation */
    if (fac <= 0.0f) {
      if (ele_src_1 == ele_dst) {
        /* do nothing */
      }
      else {
        CustomData_bmesh_copy_block(*data_layer, ele_src_1->head.data, &ele_dst->head.data);
      }
    }
    else if (fac >= 1.0f) {
      if (ele_src_2 == ele_dst) {
        /* do nothing */
      }
      else {
        CustomData_bmesh_copy_block(*data_layer, ele_src_2->head.data, &ele_dst->head.data);
      }
    }
    else {
      const void *src[2];
      float w[2];

      src[0] = ele_src_1->head.data;
      src[1] = ele_src_2->head.data;
      w[0] = 1.0f - fac;
      w[1] = fac;
      CustomData_bmesh_interp(data_layer, src, w, 2, ele_dst->head.data);
    }
  }
}

void BM_data_interp_from_verts(
    BMesh *bm, const BMVert *v_src_1, const BMVert *v_src_2, BMVert *v_dst, const float fac)
{
  bm_data_interp_from_elem(
      &bm->vdata, (const BMElem *)v_src_1, (const BMElem *)v_src_2, (BMElem *)v_dst, fac);
}

void BM_data_interp_from_edges(
    BMesh *bm, const BMEdge *e_src_1, const BMEdge *e_src_2, BMEdge *e_dst, const float fac)
{
  bm_data_interp_from_elem(
      &bm->edata, (const BMElem *)e_src_1, (const BMElem *)e_src_2, (BMElem *)e_dst, fac);
}

/**
 * \brief Data Vert Average
 *
 * Sets all the customdata (e.g. vert, loop) associated with a vert
 * to the average of the face regions surrounding it.
 */





void BM_data_interp_face_vert_edge(BMesh *bm,
                                   const BMVert *v_src_1,
                                   const BMVert * /*v_src_2*/,
                                   BMVert *v,
                                   BMEdge *e,
                                   const float fac)
{
  float w[2];
  BMLoop *l_v1 = nullptr, *l_v = nullptr, *l_v2 = nullptr;
  BMLoop *l_iter = nullptr;

  if (!e->l) {
    return;
  }

  w[1] = 1.0f - fac;
  w[0] = fac;

  l_iter = e->l;
  do {
    if (l_iter->v == v_src_1) {
      l_v1 = l_iter;
      l_v = l_v1->next;
      l_v2 = l_v->next;
    }
    else if (l_iter->v == v) {
      l_v1 = l_iter->next;
      l_v = l_iter;
      l_v2 = l_iter->prev;
    }

    if (!l_v1 || !l_v2) {
      return;
    }

    const void *src[2];
    src[0] = l_v1->head.data;
    src[1] = l_v2->head.data;

    CustomData_bmesh_interp(&bm->ldata, src, w, 2, l_v->head.data);
  } while ((l_iter = l_iter->radial_next) != e->l);
}


























































/**
 * \brief Multires Interpolation
 *
 * mdisps is a grid of displacements, ordered thus:
 * <pre>
 *      v1/center----v4/next -> x
 *          |           |
 *          |           |
 *       v2/prev------v3/cur
 *          |
 *          V
 *          y
 * </pre>
 */
static int compute_mdisp_quad(const BMLoop *l,
                              const float l_f_center[3],
                              float v1[3],
                              float v2[3],
                              float v3[3],
                              float v4[3],
                              float e1[3],
                              float e2[3])
{
  float n[3], p[3];

#ifndef NDEBUG
  {
    float cent[3];
    /* computer center */
    BM_face_calc_center_median(l->f, cent);
    BLI_assert(equals_v3v3(cent, l_f_center));
  }
#endif

  mid_v3_v3v3(p, l->prev->v->co, l->v->co);
  mid_v3_v3v3(n, l->next->v->co, l->v->co);

  copy_v3_v3(v1, l_f_center);
  copy_v3_v3(v2, p);
  copy_v3_v3(v3, l->v->co);
  copy_v3_v3(v4, n);

  sub_v3_v3v3(e1, v2, v1);
  sub_v3_v3v3(e2, v3, v4);

  return 1;
}

static bool quad_co(const float v1[3],
                    const float v2[3],
                    const float v3[3],
                    const float v4[3],
                    const float p[3],
                    const float n[3],
                    float r_uv[2])
{
  float projverts[5][3], n2[3];
  const float origin[2] = {0.0f, 0.0f};
  int i;

  /* project points into 2d along normal */
  copy_v3_v3(projverts[0], v1);
  copy_v3_v3(projverts[1], v2);
  copy_v3_v3(projverts[2], v3);
  copy_v3_v3(projverts[3], v4);
  copy_v3_v3(projverts[4], p);

  normal_quad_v3(n2, projverts[0], projverts[1], projverts[2], projverts[3]);

  if (dot_v3v3(n, n2) < -FLT_EPSILON) {
    return false;
  }

  /* rotate */
  poly_rotate_plane(n, projverts, 5);

  /* subtract origin */
  for (i = 0; i < 4; i++) {
    sub_v2_v2(projverts[i], projverts[4]);
  }

  if (!isect_point_quad_v2(origin, projverts[0], projverts[1], projverts[2], projverts[3])) {
    return false;
  }

  resolve_quad_uv_v2(r_uv, origin, projverts[0], projverts[3], projverts[2], projverts[1]);

  return true;
}

static void mdisp_axis_from_quad(const float v1[3],
                                 const float v2[3],
                                 float /*v3*/[3],
                                 const float v4[3],
                                 float r_axis_x[3],
                                 float r_axis_y[3])
{
  sub_v3_v3v3(r_axis_x, v4, v1);
  sub_v3_v3v3(r_axis_y, v2, v1);

  normalize_v3(r_axis_x);
  normalize_v3(r_axis_y);
}

/**
 * \param l_src: is loop whose internal displacement.
 * \param l_dst: is loop to project onto.
 * \param p: The point being projected.
 * \param r_axis_x, r_axis_y: The location in loop's #CD_MDISPS grid of point `p`.
 */
static bool mdisp_in_mdispquad(BMLoop *l_src,
                               BMLoop *l_dst,
                               const float l_dst_f_center[3],
                               const float p[3],
                               int res,
                               float r_axis_x[3],
                               float r_axis_y[3],
                               float r_uv[2])
{
  float v1[3], v2[3], c[3], v3[3], v4[3], e1[3], e2[3];
  float eps = FLT_EPSILON * 4000;

  if (is_zero_v3(l_src->v->no)) {
    BM_vert_normal_update_all(l_src->v);
  }
  if (is_zero_v3(l_dst->v->no)) {
    BM_vert_normal_update_all(l_dst->v);
  }

  compute_mdisp_quad(l_dst, l_dst_f_center, v1, v2, v3, v4, e1, e2);

  /* expand quad a bit */
  mid_v3_v3v3v3v3(c, v1, v2, v3, v4);

  sub_v3_v3(v1, c);
  sub_v3_v3(v2, c);
  sub_v3_v3(v3, c);
  sub_v3_v3(v4, c);
  mul_v3_fl(v1, 1.0f + eps);
  mul_v3_fl(v2, 1.0f + eps);
  mul_v3_fl(v3, 1.0f + eps);
  mul_v3_fl(v4, 1.0f + eps);
  add_v3_v3(v1, c);
  add_v3_v3(v2, c);
  add_v3_v3(v3, c);
  add_v3_v3(v4, c);

  if (!quad_co(v1, v2, v3, v4, p, l_src->v->no, r_uv)) {
    return false;
  }

  mul_v2_fl(r_uv, float(res - 1));

  mdisp_axis_from_quad(v1, v2, v3, v4, r_axis_x, r_axis_y);

  return true;
}

static float bm_loop_flip_equotion(float mat[2][2],
                                   float b[2],
                                   const float target_axis_x[3],
                                   const float target_axis_y[3],
                                   const float coord[3],
                                   int i,
                                   int j)
{
  mat[0][0] = target_axis_x[i];
  mat[0][1] = target_axis_y[i];
  mat[1][0] = target_axis_x[j];
  mat[1][1] = target_axis_y[j];
  b[0] = coord[i];
  b[1] = coord[j];

  return cross_v2v2(mat[0], mat[1]);
}

static void bm_loop_flip_disp(const float source_axis_x[3],
                              const float source_axis_y[3],
                              const float target_axis_x[3],
                              const float target_axis_y[3],
                              float disp[3])
{
  float vx[3], vy[3], coord[3];
  float n[3], vec[3];
  float b[2], mat[2][2], d;

  mul_v3_v3fl(vx, source_axis_x, disp[0]);
  mul_v3_v3fl(vy, source_axis_y, disp[1]);
  add_v3_v3v3(coord, vx, vy);

  /* project displacement from source grid plane onto target grid plane */
  cross_v3_v3v3(n, target_axis_x, target_axis_y);
  project_v3_v3v3(vec, coord, n);
  sub_v3_v3v3(coord, coord, vec);

  d = bm_loop_flip_equotion(mat, b, target_axis_x, target_axis_y, coord, 0, 1);

  if (fabsf(d) < 1e-4f) {
    d = bm_loop_flip_equotion(mat, b, target_axis_x, target_axis_y, coord, 0, 2);
    if (fabsf(d) < 1e-4f) {
      d = bm_loop_flip_equotion(mat, b, target_axis_x, target_axis_y, coord, 1, 2);
    }
  }

  disp[0] = (b[0] * mat[1][1] - mat[0][1] * b[1]) / d;
  disp[1] = (mat[0][0] * b[1] - b[0] * mat[1][0]) / d;
}

struct BMLoopInterpMultiresData {
  BMLoop *l_dst;
  BMLoop *l_src_first;
  int cd_loop_mdisp_offset;

  MDisps *md_dst;
  const float *f_src_center;

  float *axis_x, *axis_y;
  float *v1, *v4;
  float *e1, *e2;

  int res;
  float d;
};

static void loop_interp_multires_cb(void *__restrict userdata,
                                    const int ix,
                                    const TaskParallelTLS *__restrict /*tls*/)
{
  BMLoopInterpMultiresData *data = static_cast<BMLoopInterpMultiresData *>(userdata);

  BMLoop *l_first = data->l_src_first;
  BMLoop *l_dst = data->l_dst;
  const int cd_loop_mdisp_offset = data->cd_loop_mdisp_offset;

  MDisps *md_dst = data->md_dst;
  const float *f_src_center = data->f_src_center;

  float *axis_x = data->axis_x;
  float *axis_y = data->axis_y;

  float *v1 = data->v1;
  float *v4 = data->v4;
  float *e1 = data->e1;
  float *e2 = data->e2;

  const int res = data->res;
  const float d = data->d;

  float x = d * ix, y;
  int iy;
  for (y = 0.0f, iy = 0; iy < res; y += d, iy++) {
    BMLoop *l_iter = l_first;
    float co1[3], co2[3], co[3];

    madd_v3_v3v3fl(co1, v1, e1, y);
    madd_v3_v3v3fl(co2, v4, e2, y);
    interp_v3_v3v3(co, co1, co2, x);

    do {
      MDisps *md_src;
      float src_axis_x[3], src_axis_y[3];
      float uv[2];

      md_src = static_cast<MDisps *>(BM_ELEM_CD_GET_VOID_P(l_iter, cd_loop_mdisp_offset));

      if (mdisp_in_mdispquad(l_dst, l_iter, f_src_center, co, res, src_axis_x, src_axis_y, uv)) {
        old_mdisps_bilinear(md_dst->disps[iy * res + ix], md_src->disps, res, uv[0], uv[1]);
        bm_loop_flip_disp(src_axis_x, src_axis_y, axis_x, axis_y, md_dst->disps[iy * res + ix]);

        break;
      }
    } while ((l_iter = l_iter->next) != l_first);
  }
}

void BM_loop_interp_multires_ex(BMesh * /*bm*/,
                                BMLoop *l_dst,
                                const BMFace *f_src,
                                const float f_dst_center[3],
                                const float f_src_center[3],
                                const int cd_loop_mdisp_offset)
{
  MDisps *md_dst;
  float v1[3], v2[3], v3[3], v4[3] = {0.0f, 0.0f, 0.0f}, e1[3], e2[3];
  float axis_x[3], axis_y[3];

  /* ignore 2-edged faces */
  if (UNLIKELY(l_dst->f->len < 3)) {
    return;
  }

  md_dst = static_cast<MDisps *>(BM_ELEM_CD_GET_VOID_P(l_dst, cd_loop_mdisp_offset));
  compute_mdisp_quad(l_dst, f_dst_center, v1, v2, v3, v4, e1, e2);

  /* if no disps data allocate a new grid, the size of the first grid in f_src. */
  if (!md_dst->totdisp) {
    const MDisps *md_src = static_cast<const MDisps *>(
        BM_ELEM_CD_GET_VOID_P(BM_FACE_FIRST_LOOP(f_src), cd_loop_mdisp_offset));

    md_dst->totdisp = md_src->totdisp;
    md_dst->level = md_src->level;
    if (md_dst->totdisp) {
      md_dst->disps = static_cast<float (*)[3]>(
          MEM_callocN(sizeof(float[3]) * md_dst->totdisp, __func__));
    }
    else {
      return;
    }
  }

  mdisp_axis_from_quad(v1, v2, v3, v4, axis_x, axis_y);

  const int res = int(sqrt(md_dst->totdisp));
  BMLoopInterpMultiresData data = {};
  data.l_dst = l_dst;
  data.l_src_first = BM_FACE_FIRST_LOOP(f_src);
  data.cd_loop_mdisp_offset = cd_loop_mdisp_offset;
  data.md_dst = md_dst;
  data.f_src_center = f_src_center;
  data.axis_x = axis_x;
  data.axis_y = axis_y;
  data.v1 = v1;
  data.v4 = v4;
  data.e1 = e1;
  data.e2 = e2;
  data.res = res;
  data.d = 1.0f / float(res - 1);

  TaskParallelSettings settings;
  BLI_parallel_range_settings_defaults(&settings);
  settings.use_threading = (res > 5);
  BLI_task_parallel_range(0, res, &data, loop_interp_multires_cb, &settings);
}
















void BM_face_interp_multires_ex(BMesh *bm,
                                BMFace *f_dst,
                                const BMFace *f_src,
                                const float f_dst_center[3],
                                const float f_src_center[3],
                                const int cd_loop_mdisp_offset)
{
  BMLoop *l_iter, *l_first;
  l_iter = l_first = BM_FACE_FIRST_LOOP(f_dst);
  do {
    BM_loop_interp_multires_ex(
        bm, l_iter, f_src, f_dst_center, f_src_center, cd_loop_mdisp_offset);
  } while ((l_iter = l_iter->next) != l_first);
}
















void BM_face_multires_bounds_smooth(BMesh *bm, BMFace *f)
{
  const int cd_loop_mdisp_offset = CustomData_get_offset(&bm->ldata, CD_MDISPS);
  BMLoop *l;
  BMIter liter;

  if (cd_loop_mdisp_offset == -1) {
    return;
  }

  BM_ITER_ELEM (l, &liter, f, BM_LOOPS_OF_FACE) {
    MDisps *mdp = static_cast<MDisps *>(BM_ELEM_CD_GET_VOID_P(l->prev, cd_loop_mdisp_offset));
    MDisps *mdl = static_cast<MDisps *>(BM_ELEM_CD_GET_VOID_P(l, cd_loop_mdisp_offset));
    MDisps *mdn = static_cast<MDisps *>(BM_ELEM_CD_GET_VOID_P(l->next, cd_loop_mdisp_offset));
    float co1[3];
    int sides;
    int y;

    /**
     * mdisps is a grid of displacements, ordered thus:
     * <pre>
     *                    v4/next
     *                      |
     *  |      v1/cent-----mid2 ---> x
     *  |         |         |
     *  |         |         |
     * v2/prev---mid1-----v3/cur
     *            |
     *            V
     *            y
     * </pre>
     */

    sides = int(sqrt(mdp->totdisp));
    for (y = 0; y < sides; y++) {
      mid_v3_v3v3(co1, mdn->disps[y * sides], mdl->disps[y]);

      copy_v3_v3(mdn->disps[y * sides], co1);
      copy_v3_v3(mdl->disps[y], co1);
    }
  }

  BM_ITER_ELEM (l, &liter, f, BM_LOOPS_OF_FACE) {
    MDisps *mdl1 = static_cast<MDisps *>(BM_ELEM_CD_GET_VOID_P(l, cd_loop_mdisp_offset));
    MDisps *mdl2;
    float co1[3], co2[3], co[3];
    int sides;
    int y;

    /**
     * mdisps is a grid of displacements, ordered thus:
     * <pre>
     *                    v4/next
     *                      |
     *  |      v1/cent-----mid2 ---> x
     *  |         |         |
     *  |         |         |
     * v2/prev---mid1-----v3/cur
     *            |
     *            V
     *            y
     * </pre>
     */

    if (l->radial_next == l) {
      continue;
    }

    if (l->radial_next->v == l->v) {
      mdl2 = static_cast<MDisps *>(BM_ELEM_CD_GET_VOID_P(l->radial_next, cd_loop_mdisp_offset));
    }
    else {
      mdl2 = static_cast<MDisps *>(
          BM_ELEM_CD_GET_VOID_P(l->radial_next->next, cd_loop_mdisp_offset));
    }

    sides = int(sqrt(mdl1->totdisp));
    for (y = 0; y < sides; y++) {
      int a1, a2, o1, o2;

      if (l->v != l->radial_next->v) {
        a1 = sides * y + sides - 2;
        a2 = (sides - 2) * sides + y;

        o1 = sides * y + sides - 1;
        o2 = (sides - 1) * sides + y;
      }
      else {
        a1 = sides * y + sides - 2;
        a2 = sides * y + sides - 2;
        o1 = sides * y + sides - 1;
        o2 = sides * y + sides - 1;
      }

      /* magic blending numbers, hardcoded! */
      add_v3_v3v3(co1, mdl1->disps[a1], mdl2->disps[a2]);
      mul_v3_fl(co1, 0.18);

      add_v3_v3v3(co2, mdl1->disps[o1], mdl2->disps[o2]);
      mul_v3_fl(co2, 0.32);

      add_v3_v3v3(co, co1, co2);

      copy_v3_v3(mdl1->disps[o1], co);
      copy_v3_v3(mdl2->disps[o2], co);
    }
  }
}





































































































































































































































































































































































































/* -------------------------------------------------------------------- */
/** \name Loop interpolation functions: BM_vert_loop_groups_data_layer_***
 *
 * Handling loop custom-data such as UVs, while keeping contiguous fans is rather tedious.
 * Especially when a verts loops can have multiple CustomData layers,
 * and each layer can have multiple (different) contiguous fans.
 * Said differently, a single vertices loops may span multiple UV islands.
 *
 * These functions snapshot vertices loops, storing each contiguous fan in its own group.
 * The caller can manipulate the loops, then re-combine the CustomData values.
 *
 * While these functions don't explicitly handle multiple layers at once,
 * the caller can simply store its own list.
 *
 * \note Currently they are averaged back together (weighted by loop angle)
 * but we could copy add other methods to re-combine CustomData-Loop-Fans.
 *
 * \{ */

struct LoopWalkCtx {
  /* same for all groups */
  int type;
  int cd_layer_offset;
  const float *loop_weights;
  MemArena *arena;

  /* --- Per loop fan vars --- */

  /* reference for this contiguous fan */
  const void *data_ref;
  int data_len;

  /* accumulate 'LoopGroupCD.weight' to make unit length */
  float weight_accum;

  /* both arrays the size of the 'BM_vert_face_count(v)'
   * each contiguous fan gets a slide of these arrays */
  void **data_array;
  int *data_index_array;
  float *weight_array;
};

/* Store vars to pass into 'CustomData_bmesh_interp' */
struct LoopGroupCD {
  /* direct customdata pointer array */
  void **data;
  /* weights (aligned with 'data') */
  float *data_weights;
  /* index-in-face */
  int *data_index;
  /* number of loops in the fan */
  int data_len;
};














/**
 * called recursively, keep stack-usage minimal.
 *
 * \note called for fan matching so we're pretty much safe not to break the stack
 */












































































































































































/** \} */
