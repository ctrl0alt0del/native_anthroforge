"""Read-only skin eligibility shared by desktop consumers and application operations."""

import json
from dataclasses import asdict, dataclass
from typing import Any

from anthroforge.core import skin_sources


@dataclass(frozen=True)
class Eligibility:
    available: bool
    reason: str = ""
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class Status:
    document_revision: int
    skin_revision: int
    reference: str
    final_revision: int
    operations: dict[str, Eligibility]


def allowed(reason: str, warnings: tuple[str, ...] = ()) -> Eligibility:
    return Eligibility(not reason, reason, warnings if not reason else ())


def assess(document: Any, resources: Any) -> Status:
    skin = document.skin
    actions = creation(document, resources) | operational(document, resources)
    return Status(document.revision, skin.revision, skin.reference, skin.final.revision, actions)


def creation(document: Any, resources: Any) -> dict[str, Eligibility]:
    skin = document.skin
    build = "" if skin_sources.contributors(document) else "Add SCP or tissue geometry first."
    topology = "" if skin.envelope.asset in resources.meshes else "Build a skin envelope first."
    reference = (
        ""
        if (skin.pending_topology.asset or skin.topology.asset) in resources.meshes
        else "Build skin topology first."
    )
    return dict(
        build=allowed(build),
        envelope=allowed(build),
        topology=allowed(topology),
        reference=allowed(reference),
    )


def operational(document: Any, resources: Any) -> dict[str, Eligibility]:
    skin = document.skin
    update = reference_reason(document, resources)
    warning = (
        ("Using accepted skin; construction settings have not been rebuilt.",)
        if skin.construction_stale
        else ()
    )
    fit = update or (skin.final.error if skin.final.status in ("failed", "invalid") else "")
    export = "" if skin.final.asset in resources.meshes else "Build final skin before exporting."
    return dict(
        update=allowed(update, warning),
        fit=allowed(fit, warning),
        export=allowed(export, export_warnings(skin)),
    )


def reference_reason(document: Any, resources: Any) -> str:
    try:
        return reference_compatibility(document, resources)
    except (KeyError, ValueError, TypeError):
        return "Skin reference data is incomplete or incompatible; rebuild the reference."


def reference_compatibility(document: Any, resources: Any) -> str:
    skin = document.skin
    reference = resources.skin.get(skin.reference)
    if reference is None or skin.final.asset not in resources.meshes:
        return "Build skin with a deformation reference first."
    if set(skin.reference_sources) - resources.meshes.keys():
        return "Retained anatomical material is missing; rebuild the skin reference."
    metadata = json.loads(reference.metadata)
    previous = tuple((r["owner"], r["kind"], r["instance"]) for r in metadata["sources"])
    current = tuple((r.owner, r.kind, r.instance) for r in skin_sources.contributors(document))
    if previous != current:
        return "Skin contributors changed; rebuild the skin reference."
    if resources.meshes[skin.final.asset].mesh.counts[0] != len(reference.arrays["vertex_ids"]):
        return "Skin vertex identities changed; rebuild the skin reference."
    return source_failures(document, resources, metadata)


def source_failures(document: Any, resources: Any, metadata: Any) -> str:
    for row in metadata["sources"]:
        item = document.object(row["owner"])
        result = source_result(item, row["kind"], metadata["tissue_surface"])
        if result.status in ("failed", "invalid", "cancelled") or result.error:
            return str(item.name + ": " + (result.error or "The required surface is unavailable."))
        current = resources.meshes.get(result.asset or getattr(item, "asset", ""))
        if current is None:
            return str(item.name) + ": evaluate the required surface first."
    return ""


def source_result(item: Any, kind: str, policy: str) -> Any:
    if kind != "TISSUE":
        return item.result
    return item.rest_result if policy == "INFLATED_REST" else item.final_result


def export_warnings(skin: Any) -> tuple[str, ...]:
    if skin.construction_stale or skin.final.status != "ready" or skin.final.pending:
        return ("Skin has pending changes or unapplied settings; choose an export policy.",)
    return ()


class SkinStatusProvider:
    def __init__(self, session: Any):
        self.session = session
        self.key: tuple[int, int] | None = None
        self.value: Status | None = None
        self.listeners: list[Any] = []

    def subscribe(self, callback: Any) -> Any:
        self.listeners.append(callback)
        return lambda: self.listeners.remove(callback)

    def changed(self) -> None:
        self.key = None
        for callback in tuple(self.listeners):
            callback()

    def snapshot(self) -> Status:
        document, resources = self.session.document, self.session.resources
        key = id(document), id(resources)
        if self.key != key or self.value is None:
            self.value = assess(document, resources)
            self.key = key
        return self.value

    def describe(self) -> dict[str, Any]:
        return asdict(self.snapshot())

    def require(self, operation: str) -> None:
        status = self.snapshot().operations[operation]
        if not status.available:
            raise ValueError(status.reason)
