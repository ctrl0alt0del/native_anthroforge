"""Comparison presentation reuses staged geometry and cached native picking."""

from PySide6.QtCore import Property, Slot

from anthroforge.native import inspection, scene, sections

from . import inspection_scene
from .skeleton_scene import SkeletonScene


class ReconstructionScene(SkeletonScene):
    def __init__(self, controller, parent):
        super().__init__(controller, parent)
        self.plane, self.contours, self.patch = None, [[], []], None
        self.triangles, self.outlines = set(), {}

    @Property("QVariantMap", notify=SkeletonScene.changed)
    def state(self):
        return dict(
            camera=self.camera,
            mode=self.mode,
            selection=self.selection,
            plane=self.plane,
            contours=self.contours,
            region=self.region_state(),
        )

    def region_state(self):
        return dict(
            active=self.patch is not None,
            count=len(self.triangles),
            side=self.patch,
            lines=[p for line in self.outlines.values() for p in line],
        )

    def refresh_annotations(self):
        self.marker_rows = []
        self.annotationsChanged.emit()

    def rows(self, index):
        rows, leases = [], []
        for layer in self.candidate[index].layers:
            metadata = self.metadata(layer, index)
            rows.extend(inspection_scene.chunks(metadata, layer.resource))
            if layer.resource is not None:
                leases.append(layer.resource)
        return rows, leases

    def metadata(self, layer, index):
        return dict(
            id=layer.identity,
            kind=layer.kind,
            matrix=layer.frame,
            trs=self.controller.session.engine.decompose(layer.frame),
            quaternion=scene.quaternion(self.controller.session.engine, layer.frame),
            color=layer.color,
            readonly=True,
            stage=self.candidate[index].stage,
        )

    def set_sections(self, report):
        self.plane = report.get("plane")
        self.contours = [
            [p for row in group for p in row["lines"]] for group in report.get("sections", [[], []])
        ]
        self.changed.emit()

    @Slot(int)
    def selectRegion(self, side):
        self.patch = side if side in (0, 1) else None
        self.triangles, self.outlines = set(), {}
        self.changed.emit()

    @Slot(int, "QVariantList", "QVariantList", float, result=str)
    def pick(self, index, origin, direction, radius):
        if self.patch is not None:
            return self.pick_region(index, origin, direction)
        if self.plane and self.picking[index]:
            rows, handles, matrices = self.picking[index]["MESH"]
            hits = sections.pick(
                self.controller.session.engine,
                handles,
                matrices,
                [self.plane] * len(rows),
                origin,
                direction,
            )
            return rows[int(hits[0][0])]["id"] if hits else ""
        return super().pick(index, origin, direction, radius)

    def pick_region(self, index, origin, direction):
        if index != self.patch or not self.candidate:
            return ""
        layers = self.candidate[index].layers
        if len(layers) != 1 or layers[0].kind != "MESH":
            return ""
        layer = layers[0]
        if not any(
            row["handle"] == layer.resource.handle for row in self.models[index].active_rows()
        ):
            return ""
        hits = self.region_hits(layer, origin, direction)
        if hits:
            self.toggle_triangle(layer, int(hits[0][2]))
        return layer.identity if hits else ""

    def region_hits(self, layer, origin, direction):
        return sections.pick(
            layer.resource.engine,
            [layer.resource.handle],
            [layer.frame],
            [self.plane or [0, 0, 0, 0]],
            origin,
            direction,
        )

    def toggle_triangle(self, layer, triangle):
        if triangle in self.triangles:
            self.triangles.remove(triangle)
            self.outlines.pop(triangle)
        else:
            self.triangles.add(triangle)
            self.outlines[triangle] = inspection.face_lines(layer.resource, layer.frame, triangle)
        self.changed.emit()

    def show_region(self, side, triangles):
        self.selectRegion(side)
        layer = self.candidate[side].layers[0]
        self.triangles = set(triangles)
        lines = inspection.faces_lines(layer.resource, layer.frame, triangles)
        self.outlines = {key: lines[i * 6 : (i + 1) * 6] for i, key in enumerate(triangles)}
        self.changed.emit()
