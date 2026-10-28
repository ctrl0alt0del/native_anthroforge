/* SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bli
 *
 * Manipulations on double-linked list (#ListBase structs).
 *
 * For single linked lists see `BLI_linklist.h`.
 */

#include <cstdlib>
#include <cstring>

#include "MEM_guardedalloc.h"

#include "DNA_listBase.h"

#include "BLI_assert.h"
#include "BLI_listbase.h"

#include "BLI_strict_flags.h" /* IWYU pragma: keep. Keep last. */

void BLI_movelisttolist(ListBase *dst, ListBase *src)
{
  if (src->first == nullptr) {
    return;
  }

  if (dst->first == nullptr) {
    dst->first = src->first;
    dst->last = src->last;
  }
  else {
    ((Link *)dst->last)->next = static_cast<Link *>(src->first);
    ((Link *)src->first)->prev = static_cast<Link *>(dst->last);
    dst->last = src->last;
  }
  src->first = src->last = nullptr;
}





































































void BLI_addtail(ListBase *listbase, void *vlink)
{
  Link *link = static_cast<Link *>(vlink);

  if (link == nullptr) {
    return;
  }

  link->next = nullptr;
  link->prev = static_cast<Link *>(listbase->last);

  if (listbase->last) {
    ((Link *)listbase->last)->next = link;
  }
  if (listbase->first == nullptr) {
    listbase->first = link;
  }
  listbase->last = link;
}

void BLI_remlink(ListBase *listbase, void *vlink)
{
  Link *link = static_cast<Link *>(vlink);

  if (link == nullptr) {
    return;
  }

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





















































































































void BLI_freelinkN(ListBase *listbase, void *vlink)
{
  Link *link = static_cast<Link *>(vlink);

  if (link == nullptr) {
    return;
  }

  BLI_remlink(listbase, link);
  MEM_freeN(link);
}

/**
 * Assigns all #Link.prev pointers from #Link.next
 */











#define SORT_IMPL_LINKTYPE Link

/* regular call */
#define SORT_IMPL_FUNC listbase_sort_fn
#include "list_sort_impl.h"
#undef SORT_IMPL_FUNC

/* re-entrant call */
#define SORT_IMPL_USE_THUNK
#define SORT_IMPL_FUNC listbase_sort_fn_r
#include "list_sort_impl.h"
#undef SORT_IMPL_FUNC
#undef SORT_IMPL_USE_THUNK

#undef SORT_IMPL_LINKTYPE


























































































































































































void BLI_freelistN(ListBase *listbase)
{
  Link *link, *next;

  link = static_cast<Link *>(listbase->first);
  while (link) {
    next = link->next;
    MEM_freeN(link);
    link = next;
  }

  BLI_listbase_clear(listbase);
}






























































































































































































void *BLI_findptr(const ListBase *listbase, const void *ptr, const int offset)
{
  LISTBASE_FOREACH (Link *, link, listbase) {
    /* Exact copy of #BLI_findstring(), except for this line. */
    const void *ptr_iter = *((const void **)(((const char *)link) + offset));
    if (ptr == ptr_iter) {
      return link;
    }
  }
  return nullptr;
}

































































































































































































































