/* SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup intern_mem
 *
 * Guarded memory allocation, and boundary-write detection.
 */

#include <stdarg.h>
#include <stddef.h> /* offsetof */
#include <stdio.h>  /* printf */
#include <stdlib.h>
#include <string.h> /* memcpy */
#include <sys/types.h>

#include <pthread.h>

#include "MEM_guardedalloc.h"

/* Quiet warnings when dealing with allocated data written into the blend file.
 * This also rounds up and causes warnings which we don't consider bugs in practice. */
#ifdef WITH_MEM_VALGRIND
#  include "valgrind/memcheck.h"
#endif

/* to ensure strict conversions */
#include "../../source/blender/blenlib/BLI_strict_flags.h"

#include "atomic_ops.h"
#include "mallocn_intern.hh"
#include "mallocn_intern_function_pointers.hh"

using namespace mem_guarded::internal;

/* Only for debugging:
 * store original buffer's name when doing MEM_dupallocN
 * helpful to profile issues with non-freed "dup_alloc" buffers,
 * but this introduces some overhead to memory header and makes
 * things slower a bit, so better to keep disabled by default
 */
// #define DEBUG_MEMDUPLINAME

/* Only for debugging:
 * lets you count the allocations so as to find the allocator of unfreed memory
 * in situations where the leak is predictable */

// #define DEBUG_MEMCOUNTER

/* Only for debugging:
 * Defining DEBUG_BACKTRACE will display a back-trace from where memory block was allocated and
 * print this trace for all unfreed blocks. This will only work for ASAN enabled builds. This
 * option will be on by default for MSVC as it currently does not have LSAN which would normally
 * report these leaks, off by default on all other platforms because it would report the leaks
 * twice, once here, and once by LSAN.
 */
#if defined(_MSC_VER)
#  ifdef WITH_ASAN
#    define DEBUG_BACKTRACE
#  endif
#else
/* Un-comment to report back-traces with leaks, uses ASAN when enabled.
 * NOTE: The default linking options cause the stack traces only to include addresses.
 * Use `addr2line` to expand into file, line & function identifiers,
 * see: `tools/utils/addr2line_backtrace.py` convenience utility. */
// #  define DEBUG_BACKTRACE
#endif

#ifdef DEBUG_BACKTRACE
#  ifdef WITH_ASAN
/* Rely on address sanitizer. */
#  else
#    if defined(__linux__) || defined(__APPLE__)
#      define DEBUG_BACKTRACE_EXECINFO
#    else
#      error "DEBUG_BACKTRACE: not supported for this platform!"
#    endif
#  endif
#endif

#ifdef DEBUG_BACKTRACE_EXECINFO
#  define BACKTRACE_SIZE 100
#endif

#ifdef DEBUG_MEMCOUNTER
/* set this to the value that isn't being freed */
#  define DEBUG_MEMCOUNTER_ERROR_VAL 0
static int _mallocn_count = 0;

/* Break-point here. */




#endif

/* --------------------------------------------------------------------- */
/* Data definition                                                       */
/* --------------------------------------------------------------------- */
/* all memory chunks are put in linked lists */
typedef struct localLink {
  localLink *next, *prev;
} localLink;

typedef struct localListBase {
  void *first, *last;
} localListBase;

namespace {

/* NOTE(@hos): keep this struct aligned (e.g., IRIX/GCC). */
typedef struct MemHead {
  int tag1;
  size_t len;
  MemHead *next, *prev;
  const char *name;
  const char *nextname;
  int tag2;
  uint16_t flag;
  /* if non-zero aligned allocation was used and alignment is stored here. */
  short alignment;
#ifdef DEBUG_MEMCOUNTER
  int _count;
#endif

#ifdef DEBUG_MEMDUPLINAME
  int need_free_name, pad;
#endif

#ifdef DEBUG_BACKTRACE_EXECINFO
  void *backtrace[BACKTRACE_SIZE];
  int backtrace_size;
#endif

} MemHead;
static_assert(MEM_MIN_CPP_ALIGNMENT <= alignof(MemHead), "Bad alignment of MemHead");
static_assert(MEM_MIN_CPP_ALIGNMENT <= sizeof(MemHead), "Bad size of MemHead");

typedef MemHead MemHeadAligned;

}  // namespace

/* #MemHead::flag. */
enum MemHeadFlag {
  /**
   * This block of memory has been allocated from CPP `new` (e.g. #MEM_new, or some
   * guardedalloc-overloaded `new` operator). It mainly checks that #MEM_freeN is not directly
   * called on it (#MEM_delete or some guardedalloc-overloaded `delete` operator should always be
   * used instead).
   */
  MEMHEAD_FLAG_FROM_CPP_NEW = 1 << 1,
};

typedef struct MemTail {
  int tag3, pad;
} MemTail;

#ifdef DEBUG_BACKTRACE_EXECINFO
#  include <execinfo.h>
#endif

/* --------------------------------------------------------------------- */
/* local functions                                                       */
/* --------------------------------------------------------------------- */

static void addtail(volatile localListBase *listbase, void *vlink);
static void remlink(volatile localListBase *listbase, void *vlink);
static void rem_memblock(MemHead *memh);
static void MemorY_ErroR(const char *block, const char *error);
static const char *check_memlist(const MemHead *memh);

/* --------------------------------------------------------------------- */
/* locally used defines                                                  */
/* --------------------------------------------------------------------- */

/* NOTE: this is endianness-sensitive. */
#define MAKE_ID(a, b, c, d) (int(d) << 24 | int(c) << 16 | (b) << 8 | (a))

#define MEMTAG1 MAKE_ID('M', 'E', 'M', 'O')
#define MEMTAG2 MAKE_ID('R', 'Y', 'B', 'L')
#define MEMTAG3 MAKE_ID('O', 'C', 'K', '!')
#define MEMFREE MAKE_ID('F', 'R', 'E', 'E')

#define MEMNEXT(x) ((MemHead *)(((char *)x) - offsetof(MemHead, next)))

/* --------------------------------------------------------------------- */
/* vars                                                                  */
/* --------------------------------------------------------------------- */

static uint totblock = 0;
static size_t mem_in_use = 0, peak_mem = 0;

static volatile localListBase _membase;
static volatile localListBase *membase = &_membase;
static void (*error_callback)(const char *) = nullptr;

static bool malloc_debug_memset = false;

#ifdef malloc
#  undef malloc
#endif

#ifdef calloc
#  undef calloc
#endif

#ifdef free
#  undef free
#endif

/* --------------------------------------------------------------------- */
/* implementation                                                        */
/* --------------------------------------------------------------------- */

#ifdef __GNUC__
__attribute__((format(printf, 1, 0)))
#endif
static void
print_error(const char *message, va_list str_format_args)
{
  char buf[512];
  vsnprintf(buf, sizeof(buf), message, str_format_args);
  buf[sizeof(buf) - 1] = '\0';

  if (error_callback) {
    error_callback(buf);
  }
  else {
    fputs(buf, stderr);
  }
}

#ifdef __GNUC__
__attribute__((format(printf, 1, 2)))
#endif
static void
print_error(const char *message, ...)
{
  va_list str_format_args;
  va_start(str_format_args, message);
  print_error(message, str_format_args);
  va_end(str_format_args);
}

#ifdef __GNUC__
__attribute__((format(printf, 2, 3)))
#endif
static void
report_error_on_address(const void *vmemh, const char *message, ...)
{
  va_list str_format_args;

  va_start(str_format_args, message);
  print_error(message, str_format_args);
  va_end(str_format_args);

  if (vmemh == nullptr) {
    MEM_trigger_error_on_memory_block(nullptr, 0);
    return;
  }

  const MemHead *memh = static_cast<const MemHead *>(vmemh);
  memh--;
  size_t len = memh->len;

  const void *address = memh;
  size_t size = len + sizeof(*memh) + sizeof(MemTail);
  if (UNLIKELY(memh->alignment > 0)) {
    const MemHeadAligned *memh_aligned = memh;
    address = MEMHEAD_REAL_PTR(memh_aligned);
    size = len + sizeof(*memh_aligned) + MEMHEAD_ALIGN_PADDING(memh_aligned->alignment) +
           sizeof(MemTail);
  }
  MEM_trigger_error_on_memory_block(address, size);
}

static pthread_mutex_t thread_lock = PTHREAD_MUTEX_INITIALIZER;

static void mem_lock_thread()
{
  pthread_mutex_lock(&thread_lock);
}

static void mem_unlock_thread()
{
  pthread_mutex_unlock(&thread_lock);
}

























































































































































































#ifdef DEBUG_BACKTRACE_EXECINFO

















#endif /* DEBUG_BACKTRACE_EXECINFO */








































































































































































































































































/* Memory statistics print */
typedef struct MemPrintBlock {
  const char *name;
  uintptr_t len;
  int items;
} MemPrintBlock;































































































































static const char mem_printmemlist_pydict_script[] =
    "mb_userinfo = {}\n"
    "totmem = 0\n"
    "for mb_item in membase:\n"
    "    mb_item_user_size = mb_userinfo.setdefault(mb_item['name'], [0,0])\n"
    "    mb_item_user_size[0] += 1 # Add a user\n"
    "    mb_item_user_size[1] += mb_item['len'] # Increment the size\n"
    "    totmem += mb_item['len']\n"
    "print('(membase) items:', len(membase), '| unique-names:',\n"
    "      len(mb_userinfo), '| total-mem:', totmem)\n"
    "mb_userinfo_sort = list(mb_userinfo.items())\n"
    "for sort_name, sort_func in (('size', lambda a: -a[1][1]),\n"
    "                             ('users', lambda a: -a[1][0]),\n"
    "                             ('name', lambda a: a[0])):\n"
    "    print('\\nSorting by:', sort_name)\n"
    "    mb_userinfo_sort.sort(key = sort_func)\n"
    "    for item in mb_userinfo_sort:\n"
    "        print('name:%%s, users:%%i, len:%%i' %%\n"
    "              (item[0], item[1][0], item[1][1]))\n";

/* Prints in python syntax for easy */




















































































#if 0




























#endif






























































































/* --------------------------------------------------------------------- */
/* local functions                                                       */
/* --------------------------------------------------------------------- */

static void addtail(volatile localListBase *listbase, void *vlink)
{
  localLink *link = static_cast<localLink *>(vlink);

  /* for a generic API error checks here is fine but
   * the limited use here they will never be nullptr */
#if 0
  if (link == nullptr) {
    return;
  }
  if (listbase == nullptr) {
    return;
  }
#endif

  link->next = nullptr;
  link->prev = static_cast<localLink *>(listbase->last);

  if (listbase->last) {
    ((localLink *)listbase->last)->next = link;
  }
  if (listbase->first == nullptr) {
    listbase->first = link;
  }
  listbase->last = link;
}

static void remlink(volatile localListBase *listbase, void *vlink)
{
  localLink *link = static_cast<localLink *>(vlink);

  /* for a generic API error checks here is fine but
   * the limited use here they will never be nullptr */
#if 0
  if (link == nullptr) {
    return;
  }
  if (listbase == nullptr) {
    return;
  }
#endif

  if (link->next) {
    link->next->prev = link->prev;
  }
  if (link->prev) {
    link->prev->next = link->next;
  }

  if (listbase->last == link) {
    listbase->last = link->prev;
  }
  if (listbase->first == link) {
    listbase->first = link->next;
  }
}

static void rem_memblock(MemHead *memh)
{
  mem_lock_thread();
  remlink(membase, &memh->next);
  if (memh->prev) {
    if (memh->next) {
      MEMNEXT(memh->prev)->nextname = MEMNEXT(memh->next)->name;
    }
    else {
      MEMNEXT(memh->prev)->nextname = nullptr;
    }
  }
  mem_unlock_thread();

  atomic_sub_and_fetch_u(&totblock, 1);
  atomic_sub_and_fetch_z(&mem_in_use, memh->len);

#ifdef DEBUG_MEMDUPLINAME
  if (memh->need_free_name) {
    free((char *)memh->name);
  }
#endif

  if (UNLIKELY(malloc_debug_memset && memh->len)) {
    memset(memh + 1, 255, memh->len);
  }
  if (LIKELY(memh->alignment == 0)) {
    free(memh);
  }
  else {
    aligned_free(MEMHEAD_REAL_PTR(memh));
  }
}

static void MemorY_ErroR(const char *block, const char *error)
{
  print_error("Memoryblock %s: %s\n", block, error);

#ifdef WITH_ASSERT_ABORT
  abort();
#endif
}

static const char *check_memlist(const MemHead *memh)
{
  MemHead *forw, *back, *forwok, *backok;
  const char *name;

  forw = static_cast<MemHead *>(membase->first);
  if (forw) {
    forw = MEMNEXT(forw);
  }
  forwok = nullptr;
  while (forw) {
    if (forw->tag1 != MEMTAG1 || forw->tag2 != MEMTAG2) {
      break;
    }
    forwok = forw;
    if (forw->next) {
      forw = MEMNEXT(forw->next);
    }
    else {
      forw = nullptr;
    }
  }

  back = (MemHead *)membase->last;
  if (back) {
    back = MEMNEXT(back);
  }
  backok = nullptr;
  while (back) {
    if (back->tag1 != MEMTAG1 || back->tag2 != MEMTAG2) {
      break;
    }
    backok = back;
    if (back->prev) {
      back = MEMNEXT(back->prev);
    }
    else {
      back = nullptr;
    }
  }

  if (forw != back) {
    return ("MORE THAN 1 MEMORYBLOCK CORRUPT");
  }

  if (forw == nullptr && back == nullptr) {
    /* no wrong headers found then but in search of memblock */

    forw = static_cast<MemHead *>(membase->first);
    if (forw) {
      forw = MEMNEXT(forw);
    }
    forwok = nullptr;
    while (forw) {
      if (forw == memh) {
        break;
      }
      if (forw->tag1 != MEMTAG1 || forw->tag2 != MEMTAG2) {
        break;
      }
      forwok = forw;
      if (forw->next) {
        forw = MEMNEXT(forw->next);
      }
      else {
        forw = nullptr;
      }
    }
    if (forw == nullptr) {
      return nullptr;
    }

    back = (MemHead *)membase->last;
    if (back) {
      back = MEMNEXT(back);
    }
    backok = nullptr;
    while (back) {
      if (back == memh) {
        break;
      }
      if (back->tag1 != MEMTAG1 || back->tag2 != MEMTAG2) {
        break;
      }
      backok = back;
      if (back->prev) {
        back = MEMNEXT(back->prev);
      }
      else {
        back = nullptr;
      }
    }
  }

  if (forwok) {
    name = forwok->nextname;
  }
  else {
    name = "No name found";
  }

  if (forw == memh) {
    /* to be sure but this block is removed from the list */
    if (forwok) {
      if (backok) {
        forwok->next = (MemHead *)&backok->next;
        backok->prev = (MemHead *)&forwok->next;
        forwok->nextname = backok->name;
      }
      else {
        forwok->next = nullptr;
        membase->last = (localLink *)&forwok->next;
      }
    }
    else {
      if (backok) {
        backok->prev = nullptr;
        membase->first = &backok->next;
      }
      else {
        membase->first = membase->last = nullptr;
      }
    }
  }
  else {
    MemorY_ErroR(name, "Additional error in header");
    return ("Additional error in header");
  }

  return name;
}









































#ifndef NDEBUG
























#endif /* !NDEBUG */
