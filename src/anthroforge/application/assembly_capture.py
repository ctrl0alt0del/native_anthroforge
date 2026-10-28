"""Batch rebind adapter: missing unchanged supports use retained evidence only for preparation."""

from dataclasses import replace
from typing import Any

from anthroforge.core.assembly import declaration
from anthroforge.core.surface_references import CapturedSurface
from anthroforge.native import attachment_fields
from anthroforge.native import surface_queries as native

from . import assembly_evidence, fiber_edit_evaluation, fiber_supports, surface_queries


class Capture:
    def __init__(self, service: Any) -> None:
        self.service = service

    def __call__(
        self, engine: Any, item: Any, resources: Any, document: Any, geometry: Any, cancel: int
    ) -> Any:
        request = fiber_edit_evaluation.capture_request(
            item, geometry.path, geometry.records, geometry.world
        )
        parents = fiber_supports.resolve_parents(
            engine, document, resources, item.edit.candidates, request, cancel
        )
        targets = fiber_supports.selected_targets(
            item.edit.candidates, parents, item.support_policy
        )
        request = replace(request, parents=[targets.index(p) for p in parents])
        return self.capture(engine, document, resources, targets, request, cancel)

    def capture(
        self, engine: Any, document: Any, resources: Any, targets: Any, request: Any, cancel: int
    ) -> Any:
        providers = [self.provider(ref) for ref in targets]
        queries = tuple(self.query(document, resources, p, cancel) for p in providers)
        inputs = surface_queries.Inputs(queries, tuple(p.frame for p in providers))
        field = attachment_fields.capture(engine, inputs, request, cancel)
        return field, tuple(CapturedSurface(p.reference, p.asset_id) for p in providers)

    def provider(self, reference: Any) -> Any:
        retained = assembly_evidence.retained_provider(
            self.service.document, self.service.resources, reference
        )
        return retained or self.service.destination_provider(reference)

    def query(self, document: Any, resources: Any, provider: Any, cancel: int) -> Any:
        missing = declaration(document.registry.records, provider.reference.target)
        if missing is None:
            return surface_queries.prepare(
                document, resources.meshes, provider, native.Mode.CONFIRMED, cancel
            )
        base = resources.meshes[missing.surface_base].mesh if missing.surface_base else None
        return native.prepare(provider.resource.mesh, base, native.Mode.CONFIRMED, cancel)
