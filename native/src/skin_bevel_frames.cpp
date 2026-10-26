// SPDX-License-Identifier: GPL-2.0-or-later
#include "skin_bevel.hpp"
#include "BLI_math_vector.h"
#include "BLI_math_rotation.h"
#include "BLI_utildefines.h"
namespace af::skin {
using BevPoint=BevelPoint;
struct BevList { BevPoint* bevpoints; int nr,poly; };
#include "../vendor/blender_bevel/frames.inc"
void bevel_frames(BevelPoints& points,bool closed) {
    BevList list{points.data(),int(points.size()),closed?0:-1};
    if(list.nr==2) make_bevel_list_segment_3D(&list);
    else make_bevel_list_3D_minimum_twist(&list);
}
}
