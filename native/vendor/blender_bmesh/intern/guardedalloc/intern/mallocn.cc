/* SPDX-FileCopyrightText: 2002-2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup intern_mem
 *
 * Guarded memory allocation, and boundary-write detection.
 */

#include "MEM_guardedalloc.h"

/* To ensure strict conversions. */
#include "../../source/blender/blenlib/BLI_strict_flags.h"

#include <cassert>

#include "mallocn_intern.hh"

#include "mallocn_intern_function_pointers.hh"

using namespace mem_guarded::internal;

#ifdef WITH_MEM_JEMALLOC
/**
 * If JEMALLOC is used, it reads this global variable and enables background
 * threads to purge dirty pages. Otherwise we release memory too slowly or not
 * at all if the thread that did the allocation stays inactive.
 */
const char *malloc_conf =
    "background_thread:true,dirty_decay_ms:4000,thp:always,metadata_thp:always";
#endif

/* NOTE: Keep in sync with MEM_use_lockfree_allocator(). */

size_t (*MEM_allocN_len)(const void *vmemh) = MEM_lockfree_allocN_len;
void (*mem_guarded::internal::mem_freeN_ex)(void *vmemh,
                                            AllocationType allocation_type) = MEM_lockfree_freeN;
void *(*mem_guarded::internal::mem_dupallocN)(const void *vmemh) = MEM_lockfree_dupallocN;
void *(*MEM_reallocN_id)(void *vmemh, size_t len, const char *str) = MEM_lockfree_reallocN_id;
void *(*MEM_recallocN_id)(void *vmemh, size_t len, const char *str) = MEM_lockfree_recallocN_id;
void *(*mem_guarded::internal::mem_callocN)(size_t len, const char *str) = MEM_lockfree_callocN;
void *(*mem_guarded::internal::mem_calloc_arrayN)(size_t len,
                                                  size_t size,
                                                  const char *str) = MEM_lockfree_calloc_arrayN;
void *(*mem_guarded::internal::mem_mallocN)(size_t len, const char *str) = MEM_lockfree_mallocN;
void *(*mem_guarded::internal::mem_malloc_arrayN)(size_t len,
                                                  size_t size,
                                                  const char *str) = MEM_lockfree_malloc_arrayN;
void *(*mem_guarded::internal::mem_mallocN_aligned_ex)(size_t len,
                                                       size_t alignment,
                                                       const char *str,
                                                       AllocationType allocation_type) =
    MEM_lockfree_mallocN_aligned;
void *(*MEM_malloc_arrayN_aligned)(size_t len,
                                   size_t size,
                                   size_t alignment,
                                   const char *str) = MEM_lockfree_malloc_arrayN_aligned;
void *(*MEM_calloc_arrayN_aligned)(size_t len,
                                   size_t size,
                                   size_t alignment,
                                   const char *str) = MEM_lockfree_calloc_arrayN_aligned;
void (*MEM_printmemlist_pydict)(void) = MEM_lockfree_printmemlist_pydict;
void (*MEM_printmemlist)(void) = MEM_lockfree_printmemlist;
void (*MEM_callbackmemlist)(void (*func)(void *)) = MEM_lockfree_callbackmemlist;
void (*MEM_printmemlist_stats)(void) = MEM_lockfree_printmemlist_stats;
void (*MEM_set_error_callback)(void (*func)(const char *)) = MEM_lockfree_set_error_callback;
bool (*MEM_consistency_check)(void) = MEM_lockfree_consistency_check;
void (*MEM_set_memory_debug)(void) = MEM_lockfree_set_memory_debug;
size_t (*MEM_get_memory_in_use)(void) = MEM_lockfree_get_memory_in_use;
uint (*MEM_get_memory_blocks_in_use)(void) = MEM_lockfree_get_memory_blocks_in_use;
void (*MEM_reset_peak_memory)(void) = MEM_lockfree_reset_peak_memory;
size_t (*MEM_get_peak_memory)(void) = MEM_lockfree_get_peak_memory;

void (*mem_clearmemlist)(void) = mem_lockfree_clearmemlist;

#ifndef NDEBUG
const char *(*MEM_name_ptr)(void *vmemh) = MEM_lockfree_name_ptr;
void (*MEM_name_ptr_set)(void *vmemh, const char *str) = MEM_lockfree_name_ptr_set;
#endif

void *aligned_malloc(size_t size, size_t alignment)
{
  /* #posix_memalign requires alignment to be a multiple of `sizeof(void *)`. */
  assert(alignment >= ALIGNED_MALLOC_MINIMUM_ALIGNMENT);

#ifdef _WIN32
  return _aligned_malloc(size, alignment);
#elif defined(__APPLE__) || defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__)
  void *result;

  if (posix_memalign(&result, alignment, size)) {
    /* non-zero means allocation error
     * either no allocation or bad alignment value
     */
    return NULL;
  }
  return result;
#else /* This is for Linux. */
  return memalign(alignment, size);
#endif
}

void aligned_free(void *ptr)
{
#ifdef _WIN32
  _aligned_free(ptr);
#else
  free(ptr);
#endif
}

void MEM_freeN(void *vmemh)
{
  mem_freeN_ex(vmemh, AllocationType::ALLOC_FREE);
}

void *MEM_callocN(size_t len, const char *str)
{
  return mem_callocN(len, str);
}

void *MEM_calloc_arrayN(size_t len, size_t size, const char *str)
{
  return mem_calloc_arrayN(len, size, str);
}

void *MEM_mallocN(size_t len, const char *str)
{
  return mem_mallocN(len, str);
}

void *MEM_malloc_arrayN(size_t len, size_t size, const char *str)
{
  return mem_malloc_arrayN(len, size, str);
}

void *MEM_mallocN_aligned(size_t len, size_t alignment, const char *str)
{
  return mem_mallocN_aligned_ex(len, alignment, str, AllocationType::ALLOC_FREE);
}






/**
 * Perform assert checks on allocator type change.
 *
 * Helps catching issues (in debug build) caused by an unintended allocator type change when there
 * are allocation happened.
 */





















































































