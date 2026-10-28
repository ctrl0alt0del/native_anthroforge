/* SPDX-FileCopyrightText: 2020-2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup intern_mem
 */

#include <any>
#include <cstdio> /* Needed for `printf` on WIN32/APPLE. */
#include <cstdlib>
#include <mutex>
#include <vector>

#include "MEM_guardedalloc.h"
#include "mallocn_intern.hh"

bool leak_detector_has_run = false;
char free_after_leak_detection_message[] =
    "Freeing memory after the leak detector has run. This can happen when using "
    "static variables in C++ that are defined outside of functions. To fix this "
    "error, use the 'construct on first use' idiom.";

namespace {

bool fail_on_memleak = false;

class MemLeakPrinter {
 public:
  ~MemLeakPrinter()
  {
    leak_detector_has_run = true;
    const uint leaked_blocks = MEM_get_memory_blocks_in_use();
    if (leaked_blocks == 0) {
      return;
    }
    const size_t mem_in_use = MEM_get_memory_in_use();
    printf("Error: Not freed memory blocks: %u, total unfreed memory %f MB\n",
           leaked_blocks,
           double(mem_in_use) / 1024 / 1024);
    MEM_printmemlist();

    /* In guarded implementation, the fact that all allocated memory blocks are stored in the
     * static `membase` listbase is enough for LSAN to not detect them as leaks. Clearing it solves
     * that issue. */
    mem_clearmemlist();

    if (fail_on_memleak) {
      /* There are many other ways to change the exit code to failure here:
       * - Make the destructor `noexcept(false)` and throw an exception.
       * - Call exit(EXIT_FAILURE).
       * - Call terminate().
       */
      abort();
    }
  }
};
}  // namespace



































