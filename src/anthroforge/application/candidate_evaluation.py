"""Owned evaluation state shared by reviewed graph updates; never a second Session/pool."""

from dataclasses import dataclass, field, replace
from typing import Any

from anthroforge.core.entities import SCP
from anthroforge.core.results import Port
from anthroforge.core.skeleton_update import Finding


@dataclass
class EvaluationContext:
    engine: Any
    document: Any
    resources: Any
    preferences: Any
    cancel: Any
    profiler: Any
    baseline: Any
    prepared: set[Port] = field(default_factory=set)
    findings: list[Finding] = field(default_factory=list)
    fixed_poses: frozenset[str] = frozenset()

    @property
    def assets(self) -> Any:
        return self.resources.meshes

    def install(self, item: Any) -> None:
        group = "entities" if isinstance(item, SCP) else "objects"
        if item.id in self.document.index.controls:
            group = "controls"
        self.document = replace(
            self.document,
            **{
                group: tuple(
                    item if old.id == item.id else old for old in getattr(self.document, group)
                )
            },
        )

    def check_cancelled(self) -> None:
        if self.cancel.is_set():
            raise InterruptedError("Skeleton update cancelled.")

    def call(self, port: Port, function: Any) -> Any:
        self.check_cancelled()
        return self.profiler.call(
            "skeleton_update",
            port.output,
            function,
            self,
            port,
            _metadata=dict(target=port.owner, candidate=True),
        )
