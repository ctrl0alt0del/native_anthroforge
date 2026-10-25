"""Incoming anatomical binding references, independent of transform parenting and routing."""

from .fibers import Fiber
from .points import Anchor
from .tissues import TissueVCP


def targets(item: object) -> frozenset[str]:
    if isinstance(item, Anchor):
        return frozenset((item.binding.reference.target,))
    if isinstance(item, Fiber):
        return frozenset(
            (
                *(s.reference.target for s in item.supports),
                *(b.target for b in item.bindings),
                *(ref.target for ref in item.support_policy.included),
            )
        )
    if isinstance(item, TissueVCP):
        return frozenset(c.reference.target for c in item.constraints if c.reference)
    return frozenset()
