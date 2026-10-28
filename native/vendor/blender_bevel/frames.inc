// SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
// SPDX-License-Identifier: GPL-2.0-or-later
// Unmodified Blender 5.0.1 minimum-twist frame functions; see sources.json.
static void bevel_list_calc_bisect(BevList *bl)
{
  BevPoint *bevp2, *bevp1, *bevp0;
  int nr;
  const bool is_cyclic = bl->poly != -1;

  if (is_cyclic) {
    bevp2 = bl->bevpoints;
    bevp1 = bevp2 + (bl->nr - 1);
    bevp0 = bevp1 - 1;
    nr = bl->nr;
  }
  else {
    /* If spline is not cyclic, direction of first and
     * last bevel points matches direction of CV handle.
     *
     * This is getting calculated earlier when we know
     * CV's handles and here we might simply skip evaluation
     * of direction for this guys.
     */

    bevp0 = bl->bevpoints;
    bevp1 = bevp0 + 1;
    bevp2 = bevp1 + 1;

    nr = bl->nr - 2;
  }

  while (nr--) {
    /* totally simple */
    bisect_v3_v3v3v3(bevp1->dir, bevp0->vec, bevp1->vec, bevp2->vec);

    bevp0 = bevp1;
    bevp1 = bevp2;
    bevp2++;
  }

  /* In the unlikely situation that handles define a zeroed direction,
   * calculate it from the adjacent points, see #80742.
   *
   * Only do this as a fallback since we typically want the end-point directions
   * to be exactly aligned with the handles at the end-point, see #83117. */
  if (is_cyclic == false) {
    bevp0 = &bl->bevpoints[0];
    bevp1 = &bl->bevpoints[1];
    if (UNLIKELY(is_zero_v3(bevp0->dir))) {
      sub_v3_v3v3(bevp0->dir, bevp1->vec, bevp0->vec);
      if (normalize_v3(bevp0->dir) == 0.0f) {
        copy_v3_v3(bevp0->dir, bevp1->dir);
      }
    }

    bevp0 = &bl->bevpoints[bl->nr - 2];
    bevp1 = &bl->bevpoints[bl->nr - 1];
    if (UNLIKELY(is_zero_v3(bevp1->dir))) {
      sub_v3_v3v3(bevp1->dir, bevp1->vec, bevp0->vec);
      if (normalize_v3(bevp1->dir) == 0.0f) {
        copy_v3_v3(bevp1->dir, bevp0->dir);
      }
    }
  }
}

static void minimum_twist_between_two_points(BevPoint *bevp_curr, const BevPoint *bevp_prev)
{
  float angle = angle_normalized_v3v3(bevp_prev->dir, bevp_curr->dir);

  if (angle > 0.0f) { /* otherwise we can keep as is */
    float q[4];
    float cross_tmp[3];
    cross_v3_v3v3(cross_tmp, bevp_prev->dir, bevp_curr->dir);
    axis_angle_to_quat(q, cross_tmp, angle);
    mul_qt_qtqt(bevp_curr->quat, q, bevp_prev->quat);
  }
  else {
    copy_qt_qt(bevp_curr->quat, bevp_prev->quat);
  }
}

static void make_bevel_list_3D_minimum_twist(BevList *bl)
{
  BevPoint *bevp2, *bevp1, *bevp0; /* Standard for all make_bevel_list_3D_* functions. */
  int nr;
  float q[4];
  const bool is_cyclic = bl->poly != -1;
  /* NOTE(@ideasman42): For non-cyclic curves only initialize the first direction
   * (via `vec_to_quat`), necessary for symmetry, see #71137.
   * Otherwise initialize the first and second points before propagating rotation forward.
   * This is historical as changing this can cause significantly different output.
   * Specifically: `deform_modifiers` test: (`CurveMeshDeform`).
   *
   * While it would seem correct to only use the first point for non-cyclic curves as well
   * the end-points direction is initialized from the input handles (instead of the directions
   * between points), there is often a bigger difference in the first and second directions
   * than you'd otherwise expect. So using only the first direction breaks compatibility
   * enough it's best to leave it as-is. */
  const int nr_init = bl->nr - (is_cyclic ? 1 : 2);

  bevel_list_calc_bisect(bl);

  bevp2 = bl->bevpoints;
  bevp1 = bevp2 + (bl->nr - 1);
  bevp0 = bevp1 - 1;

  nr = bl->nr;
  while (nr--) {

    if (nr >= nr_init) {
      /* Initialize the rotation, otherwise propagate the previous rotation forward. */
      vec_to_quat(bevp1->quat, bevp1->dir, 5, 1);
    }
    else {
      minimum_twist_between_two_points(bevp1, bevp0);
    }

    bevp0 = bevp1;
    bevp1 = bevp2;
    bevp2++;
  }

  if (bl->poly != -1) { /* check for cyclic */

    /* Need to correct for the start/end points not matching
     * do this by calculating the tilt angle difference, then apply
     * the rotation gradually over the entire curve.
     *
     * Note that the split is between last and second last, rather than first/last as you'd expect.
     *
     * real order is like this
     * 0,1,2,3,4 --> 1,2,3,4,0
     *
     * This is why we compare last with second last.
     */
    float vec_1[3] = {0, 1, 0}, vec_2[3] = {0, 1, 0}, angle, ang_fac, cross_tmp[3];

    BevPoint *bevp_first;
    BevPoint *bevp_last;

    bevp_first = bl->bevpoints;
    bevp_first += bl->nr - 1;
    bevp_last = bevp_first;
    bevp_last--;

    /* Quaternions and vectors are normalized, should not need to re-normalize. */
    mul_qt_v3(bevp_first->quat, vec_1);
    mul_qt_v3(bevp_last->quat, vec_2);
    normalize_v3(vec_1);
    normalize_v3(vec_2);

    /* align the vector, can avoid this and it looks 98% OK but
     * better to align the angle quat roll's before comparing */
    {
      cross_v3_v3v3(cross_tmp, bevp_last->dir, bevp_first->dir);
      angle = angle_normalized_v3v3(bevp_first->dir, bevp_last->dir);
      axis_angle_to_quat(q, cross_tmp, angle);
      mul_qt_v3(q, vec_2);
    }

    angle = angle_normalized_v3v3(vec_1, vec_2);

    /* flip rotation if needs be */
    cross_v3_v3v3(cross_tmp, vec_1, vec_2);
    normalize_v3(cross_tmp);
    if (angle_normalized_v3v3(bevp_first->dir, cross_tmp) < DEG2RADF(90.0f)) {
      angle = -angle;
    }

    bevp2 = bl->bevpoints;
    bevp1 = bevp2 + (bl->nr - 1);
    bevp0 = bevp1 - 1;

    nr = bl->nr;
    while (nr--) {
      ang_fac = angle * (1.0f - (float(nr) / bl->nr)); /* also works */

      axis_angle_to_quat(q, bevp1->dir, ang_fac);
      mul_qt_qtqt(bevp1->quat, q, bevp1->quat);

      bevp0 = bevp1;
      bevp1 = bevp2;
      bevp2++;
    }
  }
  else {
    /* Need to correct quat for the first/last point,
     * this is so because previously it was only calculated
     * using its own direction, which might not correspond
     * the twist of neighbor point.
     */
    bevp1 = bl->bevpoints;
    bevp0 = bevp1 + 1;
    minimum_twist_between_two_points(bevp1, bevp0);

    bevp2 = bl->bevpoints;
    bevp1 = bevp2 + (bl->nr - 1);
    bevp0 = bevp1 - 1;
    minimum_twist_between_two_points(bevp1, bevp0);
  }
}

static void make_bevel_list_segment_3D(BevList *bl)
{
  float q[4];

  BevPoint *bevp2 = bl->bevpoints;
  BevPoint *bevp1 = bevp2 + 1;

  /* simple quat/dir */
  sub_v3_v3v3(bevp1->dir, bevp1->vec, bevp2->vec);
  normalize_v3(bevp1->dir);

  vec_to_quat(bevp1->quat, bevp1->dir, 5, 1);
  axis_angle_to_quat(q, bevp1->dir, bevp1->tilt);
  mul_qt_qtqt(bevp1->quat, q, bevp1->quat);
  normalize_qt(bevp1->quat);

  copy_v3_v3(bevp2->dir, bevp1->dir);
  vec_to_quat(bevp2->quat, bevp2->dir, 5, 1);
  axis_angle_to_quat(q, bevp2->dir, bevp2->tilt);
  mul_qt_qtqt(bevp2->quat, q, bevp2->quat);
  normalize_qt(bevp2->quat);
}
