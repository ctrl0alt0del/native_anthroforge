"""Three-way authored reconciliation; changed accepted values never lose silently."""

from dataclasses import replace
from typing import Any

from anthroforge.core import snapshot_definitions
from anthroforge.core.skeleton_update import Finding

from .skeleton_graph import identity

GROUPS = (
    "entities",
    "objects",
    "controls",
    "junctions",
    "shortcuts",
    "driving_shortcuts",
    "mirror_rules",
    "shared_mirror_targets",
)


def record_ids(document: Any) -> set[str]:
    return {identity(row) for group in GROUPS for row in getattr(document, group)}


def scope(record: Any, baseline: Any, current: Any) -> set[str]:
    if current.editing_scope is not None:
        return relationship_scope(set(current.editing_scope.editable), baseline, current)
    owned = set(record.editable) | set(dict(record.construction_map).values())
    for group in GROUPS:
        previous = {identity(v) for v in getattr(baseline, group)}
        owned.update(identity(v) for v in getattr(current, group) if identity(v) not in previous)
    return owned


def relationship_scope(owned: set[str], *documents: Any) -> set[str]:
    result = set(owned)
    for document in documents:
        result.update(identity(r) for r in document.mirror_rules if r.target in owned)
        result.update(identity(r) for r in document.shared_mirror_targets if r.source in owned)
    return result


def merge(record: Any, baseline: Any, current: Any, accepted: Any, choices: Any) -> Any:
    findings: list[Finding] = []
    owned, changes = scope(record, baseline, current), {}
    for group in GROUPS:
        before, proposed, live = (getattr(d, group) for d in (baseline, current, accepted))
        changes[group] = reconcile(before, proposed, live, owned, choices, findings)
    changes["formula_results"] = retained_results(current, accepted, changes["driving_shortcuts"])
    try:
        return replace(accepted, **changes), findings
    except ValueError as error:
        findings.append(Finding("structure", "", str(error), blocking=True))
        return accepted, findings


def reconcile(
    before: Any, proposed: Any, live: Any, owned: Any, choices: Any, findings: Any
) -> Any:
    old, new, present = ({identity(v): v for v in rows} for rows in (before, proposed, live))
    result = dict(present)
    for key in owned & (old.keys() | new.keys()):
        chosen = choose(key, old.get(key), new.get(key), present.get(key), choices, findings)
        if chosen is None:
            result.pop(key, None)
        else:
            result[key] = chosen
    return tuple(result.values())


def equal(before: Any, after: Any) -> bool:
    return before is after or (
        before is not None and after is not None and snapshot_definitions.same(before, after)
    )


def choose(key: str, before: Any, proposed: Any, live: Any, choices: Any, findings: Any) -> Any:
    if equal(before, proposed):
        return live
    if not equal(before, live) and not equal(proposed, live):
        decision = choices.get(key)
        if decision == "ACCEPTED":
            return live
        if decision != "VARIANT":
            findings.append(conflict(key))
            return live
    return proposed


def conflict(key: str) -> Finding:
    return Finding(
        "conflict:" + key,
        key,
        "Accepted anatomy also changed. Choose Accepted or Variant.",
        blocking=True,
        kind="conflict",
    )


def retained_results(current: Any, accepted: Any, drivers: Any) -> tuple[Any, ...]:
    formulas = {f.id for d in drivers for f in d.formulas}
    results = {r.formula: r for r in accepted.formula_results if r.formula in formulas}
    results.update(
        {
            r.formula: r
            for r in current.formula_results
            if r.formula in formulas and r.formula not in results
        }
    )
    return tuple(results.values())


def refreshed(record: Any, baseline: Any, current: Any, accepted: Any) -> Any:
    owned = scope(record, baseline, current)
    changes = {}
    for group in GROUPS:
        rows = {identity(v): v for v in getattr(accepted, group) if identity(v) not in owned}
        rows.update({identity(v): v for v in getattr(current, group) if identity(v) in owned})
        changes[group] = tuple(rows.values())
    changes["editing_scope"] = refreshed_scope(current, accepted, owned)
    changes["formula_results"] = retained_results(current, accepted, changes["driving_shortcuts"])
    return replace(current, **changes)


def refreshed_scope(current: Any, accepted: Any, owned: Any) -> Any:
    from anthroforge.core.reconstruction import EditingScope

    return EditingScope(frozenset(owned), frozenset(record_ids(accepted)) - owned)
