/* SPDX-FileCopyrightText: 2001-2002 NaN Holding BV. All rights reserved.
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bli
 *
 * Routines for working with single linked lists of 'links' - pointers to other data.
 *
 * For double linked lists see `BLI_listbase.h`.
 */

#include <cstdlib>

#include "MEM_guardedalloc.h"

#include "BLI_assert.h"
#include "BLI_linklist.h"
#include "BLI_memarena.h"
#include "BLI_mempool.h"

#include "BLI_strict_flags.h" /* IWYU pragma: keep. Keep last. */



































































































































void BLI_linklist_prepend_nlink(LinkNode **listp, void *ptr, LinkNode *nlink)
{
  nlink->link = ptr;
  nlink->next = *listp;
  *listp = nlink;
}

void BLI_linklist_prepend(LinkNode **listp, void *ptr)
{
  LinkNode *nlink = MEM_mallocN<LinkNode>(__func__);
  BLI_linklist_prepend_nlink(listp, ptr, nlink);
}







void BLI_linklist_prepend_pool(LinkNode **listp, void *ptr, BLI_mempool *mempool)
{
  LinkNode *nlink = BLI_mempool_alloc<LinkNode>(mempool);
  BLI_linklist_prepend_nlink(listp, ptr, nlink);
}
















































void *BLI_linklist_pop_pool(LinkNode **listp, BLI_mempool *mempool)
{
  /* intentionally no nullptr check */
  void *link = (*listp)->link;
  LinkNode *next = (*listp)->next;

  BLI_mempool_free(mempool, (*listp));

  *listp = next;
  return link;
}


















void BLI_linklist_free(LinkNode *list, LinkNodeFreeFP freefunc)
{
  while (list) {
    LinkNode *next = list->next;

    if (freefunc) {
      freefunc(list->link);
    }
    MEM_freeN(list);

    list = next;
  }
}


































/* -------------------------------------------------------------------- */
/* Sort */
#define SORT_IMPL_LINKTYPE LinkNode
#define SORT_IMPL_LINKTYPE_DATA link

/* regular call */
#define SORT_IMPL_FUNC linklist_sort_fn
#include "list_sort_impl.h"
#undef SORT_IMPL_FUNC

/* re-entrant call */
#define SORT_IMPL_USE_THUNK
#define SORT_IMPL_FUNC linklist_sort_fn_r
#include "list_sort_impl.h"
#undef SORT_IMPL_FUNC
#undef SORT_IMPL_USE_THUNK

#undef SORT_IMPL_LINKTYPE
#undef SORT_IMPL_LINKTYPE_DATA


















