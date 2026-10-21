"""Worker-owned construction evaluation, including shared control frames and cages."""

from typing import Any

from anthroforge.core.construction import (
    Control,
    Curve,
    Deformer,
    Primitive,
    ResolvedPrimitive,
    cyclic,
)
from anthroforge.core.document import Document
from anthroforge.core.entities import IDENTITY, SCP
from anthroforge.core.primitive_sampling import count
from anthroforge.core.results import geometry_asset
from anthroforge.native import bodies, components, path_editing, paths, segment_chain, shrinkwrap
from anthroforge.native import construction as native
from anthroforge.native.mesh import GeometryEngine, Mesh, NativeCancellation
from anthroforge.native.scene import entity_frame
from anthroforge.native.topology import draft, finalize

from . import consumed_paths
from .membership import resolve
from .object_frames import Frames
from .path_assets import PathAsset


class Evaluation:
    def __init__(
        self,
        engine: GeometryEngine,
        document: Document,
        meshes: dict[str, Mesh],
        cancel: NativeCancellation,
        path_assets: dict[str, PathAsset] | None = None,
    ) -> None:
        self.engine, self.document, self.meshes, self.cancel = engine, document, meshes, cancel
        self.transforms = Frames(engine, document)
        self.cages: dict[str, Any] = {}
        self.paths = path_assets if path_assets is not None else {}

    def control_frame(self, control: Control) -> tuple[float, ...]:
        return self.transforms.world(control.id)

    def follow_frame(self, control: Control) -> tuple[float, ...]:
        frame = self.transforms.world(control.follow)
        return native.matrix(self.engine, frame, control.matrix)

    def cage(self, control: Control) -> Any:
        if control.id not in self.cages:
            points = native.lattice_points(self.engine, control)
            self.cages[control.id] = self.deform(
                points, control.deformers, "LATTICE", "", self.control_frame(control)
            )
        return self.cages[control.id]

    def deform(
        self,
        points: Any,
        bindings: tuple[Deformer, ...],
        stage: str,
        component: str,
        frame: tuple[float, ...],
    ) -> Any:
        for binding in bindings:
            if applies(binding, stage, component):
                points = self.apply_binding(points, binding, frame)
        return points

    def apply_binding(self, points: Any, binding: Deformer, frame: Any) -> Any:
        if binding.shrinkwrap:
            return self.wrap(points, binding, frame)
        control = self.document.control(binding.control)
        target = self.control_frame(control)
        if binding.kind == "HOOK":
            return native.hook(self.engine, points, binding, frame, target, self.cancel.handle)
        args = (self.engine, points, control, binding, frame, target, self.cancel.handle)
        return native.lattice(*args, cage_points=self.cage(control))

    def wrap(self, points: Any, binding: Deformer, frame: Any) -> Any:
        from .assets import Asset
        from .surface_providers import get

        assert binding.shrinkwrap is not None
        assets = {
            key: Asset(mesh, "generated", "", 1.0, False) for key, mesh in self.meshes.items()
        }
        provider = get(self.engine, self.document, assets, binding.shrinkwrap.surface)
        return shrinkwrap.deform(self.engine, points, binding, frame, provider, self.cancel.handle)

    def curve(self, entity: SCP, curve: Curve, definition: ResolvedPrimitive) -> Any:
        bindings = tuple(b for b in entity.deformers if applies(b, "CURVE", curve.id))
        asset = consumed_paths.accepted(self.document, self.paths, curve.id)
        path = self.deformed_path(entity, curve, bindings, asset.path) if bindings else asset.path
        assert isinstance(entity.primitive, Primitive)
        use = next(use for use in entity.primitive.curves if use.id == curve.id)
        return consumed_paths.samples(path, curve, definition, use.reverse, self.cancel.handle)

    def deformed_path(
        self, entity: SCP, curve: Curve, bindings: tuple[Deformer, ...], accepted: paths.Path
    ) -> paths.Path:
        records = native.resolved_curve(self.engine, curve)
        frame = native.matrix(self.engine, entity_frame(self.engine, entity), curve.matrix)
        # Blender indices within each Bézier triple: left handle, point, right handle.
        points = records[:, [3, 4, 5, 0, 1, 2, 6, 7, 8]].reshape((-1, 3))
        bindings = tuple(resolve(b, curve) for b in bindings)
        points = self.deform(points, bindings, "CURVE", curve.id, frame)
        packed = points.reshape((-1, 9))
        records[:, :9] = packed[:, [3, 4, 5, 0, 1, 2, 6, 7, 8]]
        records = native.resolved_curve(self.engine, curve, records)
        return path_editing.deform(accepted, curve, records, self.cancel.handle)

    def construct(self, entity: SCP) -> Mesh:
        definition = consumed_paths.definition(self.engine, self.document, entity, self.paths)
        if definition.kind == "IMPORTED":
            return draft(self.meshes[definition.source], self.cancel.handle)
        if definition.chain:
            return segment_chain.construct(self.engine, definition.chain, self.cancel.handle)
        samples = {curve.id: self.curve(entity, curve, definition) for curve in definition.curves}
        if definition.kind == "LOFT":
            return native.loft(
                self.engine, definition, list(samples.values()), self.cancel.handle, complete=False
            )
        return self.body(entity, definition, samples)

    def body(self, entity: SCP, definition: ResolvedPrimitive, samples: dict[str, Any]) -> Mesh:
        pieces = [
            self.body_piece(entity, definition, p, samples[p.curve]) for p in definition.pieces
        ]
        return (
            pieces[0]
            if len(pieces) == 1
            else native.joined(self.engine, pieces, self.cancel.handle)
        )

    def body_piece(
        self, entity: SCP, definition: ResolvedPrimitive, piece: Any, samples: Any
    ) -> Mesh:
        curve = next(c for c in definition.curves if c.id == piece.curve)
        closed = cyclic(curve, definition)
        samples_count = count(entity.primitive, piece.curve)
        base = bodies.draft_base(self.engine, piece, samples_count, closed, self.cancel.handle)
        frame = native.matrix(self.engine, entity_frame(self.engine, entity), curve.matrix)
        original = base.array(0)
        points = self.deform(original, entity.deformers, "BASE", piece.id, frame)
        if points is not original:
            base = native.deformed(base, points, self.cancel.handle)
        bent = bodies.bend(base, samples, piece, closed, self.cancel.handle)
        return self.transform_mesh(bent, curve.matrix)

    def transform_mesh(self, mesh: Mesh, matrix: tuple[float, ...]) -> Mesh:
        if matrix == IDENTITY:
            return mesh
        points = components.transformed(self.engine, mesh.array(0), matrix)
        return native.deformed(mesh, points, self.cancel.handle)

    def geometry(self, entity: SCP) -> Mesh:
        mesh = self.construct(entity)
        original = mesh.array(0)
        points = self.deform(
            original, entity.deformers, "GEOMETRY", "", entity_frame(self.engine, entity)
        )
        if points is not original:
            mesh = native.deformed(mesh, points, self.cancel.handle)
        if entity.thickness and entity.thickness.enabled:
            mesh = native.solidify(mesh, entity.thickness, self.cancel.handle)
        return finalize(mesh, self.meshes.get(geometry_asset(entity)), self.cancel.handle)


def applies(binding: Deformer, stage: str, component: str) -> bool:
    return (
        binding.enabled and binding.target.stage == stage and binding.target.component == component
    )
