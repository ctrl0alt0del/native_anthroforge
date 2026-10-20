"""Exact semantic root allocation for >6 children and at most two outer boundaries."""

from collections import Counter, deque
from typing import Any


def allocate(options: Any) -> Any:
    assigned = matching(options)
    if assigned is None:
        return None
    counts = Counter(slot[0] for slot in assigned.values())
    for boundary, count in counts.items():
        if count == 1:
            return repair_singleton(options, assigned, boundary)
    return assigned


def matching(options: Any) -> Any:
    owners: dict[Any, str] = {}
    assigned: dict[str, Any] = {}
    for child in options:
        if not augment(options, owners, assigned, child):
            return None
    return assigned


def augment(options: Any, owners: Any, assigned: Any, child: str) -> bool:
    pending, previous = deque([child]), {}
    while pending:
        current = pending.popleft()
        for slot in options[current]:
            if slot in previous:
                continue
            previous[slot] = current
            if slot not in owners:
                install(owners, assigned, previous, slot)
                return True
            pending.append(owners[slot])
    return False


def install(owners: Any, assigned: Any, previous: Any, slot: Any) -> None:
    while slot is not None:
        child = previous[slot]
        old = assigned.get(child)
        assigned[child], owners[slot] = slot, child
        slot = old


def repair_singleton(options: Any, assigned: Any, boundary: str) -> Any:
    used = set(assigned.values())
    for child, slots in options.items():
        for slot in slots:
            if slot[0] == boundary and slot not in used:
                return {**assigned, child: slot}
    # One root slot cannot support a branch. All children must use the other boundary.
    reduced = {
        key: [slot for slot in slots if slot[0] != boundary] for key, slots in options.items()
    }
    return matching(reduced)
