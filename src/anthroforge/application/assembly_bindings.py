"""Verified material correspondence or explicit current-shape rebinding at import boundaries."""

import zipfile
from dataclasses import replace
from typing import Any

from anthroforge.core import anatomical_surfaces
from anthroforge.core.entities import SCP
from anthroforge.core.results import geometry_asset
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.native import attachments, topology

from . import assembly_graph, replacement_bindings, resource_storage, surface_providers


class Bindings:
    def __init__(self, preparation: Any, document: Any) -> None:
        self.p, self.document = preparation, document
        self.resources = preparation.available.snapshot()
        for kind in self.resources.__dataclass_fields__:
            getattr(self.resources, kind).update(getattr(preparation.resources, kind))
        self.cancel = getattr(preparation.cancel, "handle", 0)
        self.source_meshes = dict(preparation.loaded.meshes)
        self.evidence: list[dict[str, Any]] = []
        self.changed: set[str] = set()

    def assess(self) -> None:
        for row in self.p.mapping.rows:
            if row["action"] == "map" and row["relationship"] == "support":
                self.support(row)
        self.roots()

    def support(self, row: Any) -> None:
        choice = self.p.mapping.choices.get(
            row["key"], self.p.mapping.choices.get(row["source"], {})
        )
        choice = choice if isinstance(choice, dict) else dict(target=choice)
        role = row["role"] or "SCP_GEOMETRY"
        previous = SurfaceReference(row["source"], role)
        current = SurfaceReference(row["target"], role, choice.get("instance", ""))
        same = self.equivalent(previous, current)
        captured = self.captured_owners(row)
        if captured and not same and not choice.get("rebind", False):
            self.require_rebind(row["key"])
        elif captured and choice.get("rebind", False):
            for owner in captured:
                self.rebind(owner, current.target)

    def require_rebind(self, key: str) -> None:
        self.p.mapping.findings.append(
            dict(
                reference=key,
                blocking=True,
                message=(
                    "Material correspondence differs. "
                    "Choose Rebind to review new attachment locations."
                ),
            )
        )

    def captured_owners(self, row: Any) -> set[str]:
        result = set()
        for owner, replacements in self.p.mapping.replacements.items():
            for ref, _, _target in replacements:
                if (ref.target, ref.role, ref.relationship) != (
                    row["source"],
                    row["role"],
                    "support",
                ):
                    continue
                item = self.p.source.document.registry.records.get(owner)
                if item is not None and captured_path(item, ref.path):
                    result.add(self.p.ids[owner])
        return result

    def equivalent(self, before: Any, after: Any) -> bool:
        source = self.source_provider(before)
        target = surface_providers.snapshot(
            self.p.engine, self.document, self.resources.meshes, after
        )
        return topology.same_content(source.resource.mesh, target.resource.mesh, self.cancel)

    def source_provider(self, reference: SurfaceReference) -> Any:
        document = self.p.source.document
        item = document.object(reference.target)
        key = (
            geometry_asset(item)
            if isinstance(item, SCP)
            else anatomical_surfaces.result(item, reference.role).asset
        )
        if key not in self.source_meshes:
            with zipfile.ZipFile(self.p.source.path) as archive:
                metadata = self.p.source.metadata["assets"][key]
                self.source_meshes[key] = resource_storage.read_mesh(
                    archive, key, metadata, self.p.engine
                )
        return surface_providers.snapshot(self.p.engine, document, self.source_meshes, reference)

    def rebind(self, owner: str, target: str) -> None:
        if owner in self.changed:
            return
        before = self.document.object(owner)
        after = replacement_bindings.rebound(
            self.p.engine, self.document, self.document, self.resources, before, target, self.cancel
        )
        self.install(after)
        self.record_evidence(before, after, target)
        self.changed.add(owner)

    def record_evidence(self, before: Any, after: Any, target: str) -> None:
        self.evidence.append(
            dict(
                owner=before.id,
                target=target,
                action="rebind",
                before=locations(before),
                after=locations(after),
            )
        )

    def install(self, item: Any) -> None:
        group = "entities" if isinstance(item, SCP) else "objects"
        self.p.values[group] = tuple(item if v.id == item.id else v for v in self.p.values[group])
        records = tuple(item if v.id == item.id else v for v in getattr(self.document, group))
        self.document = replace(self.document, **{group: records})

    def roots(self) -> None:
        for key in assembly_graph.roots(self.p.selection):
            item = self.document.entity(self.p.ids[key])
            if not item.parent:
                continue
            self.root(key, item)

    def root(self, original: str, item: SCP) -> None:
        source = self.p.source.document.entity(original)
        parent = self.document.entity(item.parent)
        if source.parent and source.attachment.binding:
            if self.root_equivalent(source, parent):
                self.install(retained_root(source, item, self.p.ids, self.p.assets))
                return
            if not self.p.options.get("rebind_roots", False):
                self.require_rebind("destination_parent")
                return
        meshes = {k: a.mesh for k, a in self.resources.meshes.items()}
        changed = attachments.capture(self.p.engine, item, parent, meshes, self.cancel)
        self.install(changed)
        self.record_evidence(item, changed, parent.id)

    def root_equivalent(self, source: SCP, parent: SCP) -> bool:
        previous = self.p.source.document.entity(source.parent)
        if previous.matrix != parent.matrix or previous.geometry_offset != parent.geometry_offset:
            return False
        if source.attachment.parent_mode == "OBJECT_ORIGIN":
            return True
        return self.equivalent(SurfaceReference(source.parent), SurfaceReference(parent.id))

    def retain(self) -> None:
        for kind in self.resources.__dataclass_fields__:
            previous = getattr(self.p.available, kind)
            copied = getattr(self.p.resources, kind)
            copied.update(
                {k: v for k, v in getattr(self.resources, kind).items() if k not in previous}
            )


def captured_path(item: Any, path: Any) -> bool:
    for size in range(1, len(path)):
        container = assembly_graph.at(item, path[:size])
        if getattr(container, "material_asset", "") or getattr(container, "attachment_asset", ""):
            return True
    return False


def retained_root(source: SCP, item: SCP, ids: Any, assets: Any) -> SCP:
    from anthroforge.core.graph_records import rewritten

    return replace(
        item,
        attachment=rewritten(source.attachment, ids, assets),
        capture_parent_matrix=source.capture_parent_matrix,
        capture_parent_offset=source.capture_parent_offset,
    )


def locations(item: Any) -> list[dict[str, Any]]:
    if hasattr(item, "bindings"):
        return [
            dict(
                point=b.point,
                target=b.target,
                binding=list(b.attachment.binding) if b.attachment else [],
            )
            for b in item.bindings
        ]
    if hasattr(item, "binding"):
        return [dict(position=list(item.resolved_position), target=item.binding.reference.target)]
    return []


def assess(preparation: Any, candidate: Any) -> tuple[dict[str, Any], ...]:
    service = Bindings(preparation, candidate.merge(preparation.destination))
    service.assess()
    service.retain()
    return tuple(service.evidence)
