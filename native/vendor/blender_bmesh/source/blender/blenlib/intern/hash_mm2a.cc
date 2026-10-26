/* SPDX-FileCopyrightText: 2014 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bli
 *
 *  Functions to compute Murmur2A hash key.
 *
 * A very fast hash generating int32 result, with few collisions and good repartition.
 *
 * See also:
 * reference implementation:
 * - https://smhasher.googlecode.com/svn-history/r130/trunk/MurmurHash2.cpp
 * - http://programmers.stackexchange.com/questions/49550
 *
 * \warning Do not store that hash in files or such, it is not endian-agnostic,
 * so you should only use it for temporary data.
 */

#include "BLI_compiler_attrs.h"

#include "BLI_hash_mm2a.hh" /* own include */

/* Helpers. */
#define MM2A_M 0x5bd1e995







































































































