/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bli
 */

#include <cstdlib> /* abort() */
#include <cstring>

#include "BLI_utildefines.h"
#include "MEM_guardedalloc.h"

#include "BLI_stack.h" /* own include */

#include "BLI_strict_flags.h" /* IWYU pragma: keep. Keep last. */

#define USE_TOTELEM

#define CHUNK_EMPTY size_t(-1)
/* target chunks size: 64kb */
#define CHUNK_SIZE_DEFAULT (1 << 16)
/* ensure we get at least this many elems per chunk */
#define CHUNK_ELEM_MIN 32

struct StackChunk {
  StackChunk *next;
  char data[0];
};

struct BLI_Stack {
  StackChunk *chunk_curr; /* currently active chunk */
  StackChunk *chunk_free; /* free chunks */
  size_t chunk_index;     /* index into 'chunk_curr' */
  size_t chunk_elem_max;  /* number of elements per chunk */
  size_t elem_size;
#ifdef USE_TOTELEM
  size_t elem_num;
#endif
};






/**
 * \return number of elements per chunk, optimized for slop-space.
 */














































































































































































































