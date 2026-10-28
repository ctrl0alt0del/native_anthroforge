/* SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bli
 * \brief Efficient memory allocation for many small chunks.
 * \section aboutmemarena Memory Arena
 *
 * Memory arena's are commonly used when the program
 * needs to quickly allocate lots of little bits of data,
 * which are all freed at the same moment.
 *
 * \note Memory can't be freed during the arenas lifetime.
 */

#include <cstdlib>
#include <cstring>

#include "MEM_guardedalloc.h"

#include "BLI_asan.h"
#include "BLI_memarena.h"
#include "BLI_utildefines.h"

#ifdef WITH_MEM_VALGRIND
#  include "valgrind/memcheck.h"
#else
#  define VALGRIND_CREATE_MEMPOOL(pool, rzB, is_zeroed) UNUSED_VARS(pool, rzB, is_zeroed)
#  define VALGRIND_DESTROY_MEMPOOL(pool) UNUSED_VARS(pool)
#  define VALGRIND_MEMPOOL_ALLOC(pool, addr, size) UNUSED_VARS(pool, addr, size)

#endif

#include "BLI_strict_flags.h" /* IWYU pragma: keep. Keep last. */

struct MemBuf {
  MemBuf *next;
  uchar data[0];
};

struct MemArena {
  uchar *curbuf;
  const char *name;
  MemBuf *bufs;

  size_t bufsize, cursize;
  size_t align;

  bool use_calloc;
};

static void memarena_buf_free_all(MemBuf *mb)
{
  while (mb != nullptr) {
    MemBuf *mb_next = mb->next;

    /* Unpoison memory because #MEM_freeN might overwrite it. */
    BLI_asan_unpoison(mb, uint(MEM_allocN_len(mb)));

    MEM_freeN(mb);
    mb = mb_next;
  }
}

MemArena *BLI_memarena_new(const size_t bufsize, const char *name)
{
  MemArena *ma = MEM_callocN<MemArena>("memarena");
  ma->bufsize = bufsize;
  ma->align = 8;
  ma->name = name;

  VALGRIND_CREATE_MEMPOOL(ma, 0, false);

  return ma;
}



















void BLI_memarena_free(MemArena *ma)
{
  memarena_buf_free_all(ma->bufs);

  VALGRIND_DESTROY_MEMPOOL(ma);

  MEM_freeN(ma);
}

/** Pad num up by \a amt (must be power of two). */
#define PADUP(num, amt) (((num) + ((amt) - 1)) & ~((amt) - 1))

/** Align alloc'ed memory (needed if `align > 8`). */
static void memarena_curbuf_align(MemArena *ma)
{
  uchar *tmp;

  tmp = (uchar *)PADUP(intptr_t(ma->curbuf), int(ma->align));
  ma->cursize -= size_t(tmp - ma->curbuf);
  ma->curbuf = tmp;
}

void *BLI_memarena_alloc(MemArena *ma, size_t size)
{
  void *ptr;

  /* Ensure proper alignment by rounding size up to multiple of 8. */
  size = PADUP(size, ma->align);

  if (UNLIKELY(size > ma->cursize)) {
    if (size > ma->bufsize - (ma->align - 1)) {
      ma->cursize = PADUP(size + 1, ma->align);
    }
    else {
      ma->cursize = ma->bufsize;
    }

    MemBuf *mb;
    if (ma->use_calloc) {
      mb = static_cast<MemBuf *>(MEM_callocN(sizeof(*mb) + ma->cursize, ma->name));
    }
    else {
      mb = static_cast<MemBuf *>(MEM_mallocN(sizeof(*mb) + ma->cursize, ma->name));
    }
    ma->curbuf = mb->data;
    mb->next = ma->bufs;
    ma->bufs = mb;

    BLI_asan_poison(ma->curbuf, ma->cursize);

    memarena_curbuf_align(ma);
  }

  ptr = ma->curbuf;
  ma->curbuf += size;
  ma->cursize -= size;

  VALGRIND_MEMPOOL_ALLOC(ma, ptr, size);

  BLI_asan_unpoison(ptr, size);

  return ptr;
}
























































void BLI_memarena_clear(MemArena *ma)
{
  if (ma->bufs) {
    if (ma->bufs->next) {
      memarena_buf_free_all(ma->bufs->next);
      ma->bufs->next = nullptr;
    }

    const uchar *curbuf_prev = ma->curbuf;
    ma->curbuf = ma->bufs->data;
    memarena_curbuf_align(ma);

    /* restore to original size */
    const size_t curbuf_used = size_t(curbuf_prev - ma->curbuf);
    ma->cursize += curbuf_used;

    if (ma->use_calloc) {
      memset(ma->curbuf, 0, curbuf_used);
    }
    BLI_asan_poison(ma->curbuf, ma->cursize);
  }

  VALGRIND_DESTROY_MEMPOOL(ma);
  VALGRIND_CREATE_MEMPOOL(ma, 0, false);
}
