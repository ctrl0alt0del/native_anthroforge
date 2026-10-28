"""Preserve world placement while explicitly mapping ordinary transform relationships."""

from dataclasses import replace
from typing import Any

from anthroforge.core import graph_records
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.entities import SCP
from anthroforge.native.construction import matrix

from . import assembly_graph, curve_sources
from .object_frames import Frames


class Placement:
    def __init__(self, engine: Any, source: Any, destination: Any, choices: Any) -> None:
        self.engine, self.source, self.destination = engine, source, destination
        self.before, self.after = Frames(engine, source), Frames(engine, destination)
        self.choices = choices

    def apply(self, original: Any, changed: Any) -> Any:
        for ref, decision, target in self.choices.replacements.get(original.id, ()):
            if ref.relationship != "parent":
                continue
            parent = "" if decision.get("action") == "detach" else target
            container = assembly_graph.at(original, ref.path[:-1])
            if isinstance(container, CurveUse):
                changed = self.use(original, changed, ref, parent, container)
            elif not isinstance(original, SCP) and ref.path in (("parent",), ("follow",)):
                changed = replace(changed, matrix=self.local(original.id, parent))
        return changed

    def local(self, source: str, parent: str) -> tuple[float, ...]:
        return matrix(
            self.engine, self.after.world(parent), self.before.world(source), relative=True
        )

    def use(self, original: Any, changed: Any, ref: Any, parent: str, before: CurveUse) -> Any:
        container = assembly_graph.at(changed, ref.path[:-1])
        bound = matrix(
            self.engine, self.after.world(parent), self.before.world(before.curve), relative=True
        )
        local = curve_sources.use_frame(self.engine, self.source, before)
        updated = replace(container, reference_frame=parent, bind_matrix=bound, matrix=local)
        return graph_records.replace_at(changed, ref.path[:-1], updated)


def frame_reads(document: Any, targets: set[str]) -> set[str]:
    result, pending = set(), list(targets)
    while pending:
        key = pending.pop()
        if not key or key in result:
            continue
        item = document.object(key)
        result.add(key)
        if not isinstance(item, SCP):
            pending.append(getattr(item, "parent", "") or getattr(item, "follow", ""))
    return result
