/* SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bli
 *
 * A general (pointer -> pointer) chaining hash table
 * for 'Abstract Data Types' (known as an ADT Hash Table).
 */

#include <algorithm>
#include <climits>
#include <cstdarg>
#include <cstdlib>

#include "MEM_guardedalloc.h"

#include "BLI_math_base.h"
#include "BLI_mempool.h"
#include "BLI_sys_types.h" /* for intptr_t support */
#include "BLI_utildefines.h"

#define GHASH_INTERNAL_API
#include "BLI_ghash.h" /* own include */

#include "BLI_strict_flags.h" /* IWYU pragma: keep. Keep last. */

/* -------------------------------------------------------------------- */
/** \name Structs & Constants
 * \{ */

#define GHASH_USE_MODULO_BUCKETS

/**
 * Next prime after `2^n` (skipping 2 & 3).
 */
static const uint hashsizes[] = {
    5,       11,      17,      37,      67,       131,      257,      521,       1031,
    2053,    4099,    8209,    16411,   32771,    65537,    131101,   262147,    524309,
    1048583, 2097169, 4194319, 8388617, 16777259, 33554467, 67108879, 134217757, 268435459,
};

#ifdef GHASH_USE_MODULO_BUCKETS
#  define GHASH_MAX_SIZE 27
BLI_STATIC_ASSERT(ARRAY_SIZE(hashsizes) == GHASH_MAX_SIZE, "Invalid 'hashsizes' size");
#else
#  define GHASH_BUCKET_BIT_MIN 2
#  define GHASH_BUCKET_BIT_MAX 28 /* About 268M of buckets... */
#endif

/**
 * \note Max load #GHASH_LIMIT_GROW used to be 3. (pre 2.74).
 * Python uses 0.6666, tommyhashlib even goes down to 0.5.
 * Reducing our from 3 to 0.75 gives huge speedup
 * (about twice quicker pure GHash insertions/lookup,
 * about 25% - 30% quicker 'dynamic-topology' stroke drawing e.g.).
 * Min load #GHASH_LIMIT_SHRINK is a quarter of max load, to avoid resizing to quickly.
 */



/* WARNING! Keep in sync with ugly _gh_Entry in header!!! */
struct Entry {
  Entry *next;

  void *key;
};

struct GHashEntry {
  Entry e;

  void *val;
};

using GSetEntry = Entry;



struct GHash {
  GHashHashFP hashfp;
  GHashCmpFP cmpfp;

  Entry **buckets;
  BLI_mempool *entrypool;
  uint nbuckets;
  uint limit_grow, limit_shrink;
#ifdef GHASH_USE_MODULO_BUCKETS
  uint cursize, size_min;
#else
  uint bucket_mask, bucket_bit, bucket_bit_min;
#endif

  uint nentries;
  uint flag;
};

/** \} */

/* -------------------------------------------------------------------- */
/** \name Internal Utility API
 * \{ */





















/**
 * Get the full hash for a key.
 */





/**
 * Get the full hash for an entry.
 */





/**
 * Get the bucket-index for an already-computed full hash.
 */









/**
 * Find the index of next used bucket, starting from \a curr_bucket (\a gh is assumed non-empty).
 */






















/**
 * Expand buckets to the next size up or down.
 */

































































/**
 * Check if the number of items in the GHash is large enough to require more buckets,
 * or small enough to require less buckets, and resize \a gh accordingly.
 */





















































































/**
 * Clear and reset \a gh buckets, reserve again buckets for given number of entries.
 */























/**
 * Internal lookup function.
 * Takes hash and bucket_index arguments to avoid calling #ghash_keyhash and #ghash_bucket_index
 * multiple times.
 */














/**
 * Internal lookup function, returns previous entry of target one too.
 * Takes bucket_index argument to avoid calling #ghash_keyhash and #ghash_bucket_index
 * multiple times.
 * Useful when modifying buckets somehow (like removing an entry...).
 */


















/**
 * Internal lookup function. Only wraps #ghash_lookup_entry_ex
 */




























/**
 * Internal insert function.
 * Takes hash and bucket_index arguments to avoid calling #ghash_keyhash and #ghash_bucket_index
 * multiple times.
 */















/**
 * Insert function that takes a pre-allocated entry.
 */














/**
 * Insert function that doesn't set the value (use for GSet)
 */












































































/**
 * Remove the entry and return it, caller must free from gh->entrypool.
 */
































/**
 * Remove a random entry and return it (or nullptr if empty), caller must free from gh->entrypool.
 */





















/**
 * Run free callbacks for freeing entries.
 */





















/**
 * Copy the GHash.
 */




































/** \} */

/* -------------------------------------------------------------------- */
/** \name GHash Public API
 * \{ */













































































































































































































/** \} */

/* -------------------------------------------------------------------- */
/** \name GHash Iterator API
 * \{ */











































/** \} */

/* -------------------------------------------------------------------- */
/** \name GSet Public API
 * \{ */


















































































































/** \} */

/* -------------------------------------------------------------------- */
/** \name GSet Combined Key/Value Usage
 *
 * \note Not typical `set` use, only use when the pointer identity matters.
 * This can be useful when the key references data stored outside the GSet.
 * \{ */




















/** \} */

/* -------------------------------------------------------------------- */
/** \name Debugging & Introspection
 * \{ */

























































































































/** \} */
