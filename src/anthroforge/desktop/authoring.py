"""Focused Qt adapter for construction commands and component selection."""

import numpy as np
from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.profiling.spans import measured

from . import authoring_picking
from . import authoring_state as state
from .property_projection import PropertyProjection


class Authoring(QObject):
    changed = Signal()
    hoverChanged = Signal()
    geometryChanged = Signal()

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.editing, self.selection, self.rows = False, [], []
        self._cache_key, self._points = None, np.empty((0, 3))
        self.drag_rows = []
        self._lines, self.hover_index = [], -1
        self._curve_lines, self.hover_curve = {}, ""
        self.category = "CURVE"
        from .curve_interaction import CurveInteraction

        self.interaction = CurveInteraction(self)
        self._state, self._point_rows, self._component_rows = PropertyProjection(self), [], []
        self._component_lookup = {}
        self._layers, self._highlights = {}, {}

    @Property(QObject, constant=True)
    def state(self):
        return self._state

    @Property(QObject, constant=True)
    def curveInteraction(self):
        return self.interaction

    @Property("QVariantMap", notify=geometryChanged)
    def visualLayers(self):
        return self._layers

    @Property("QVariantMap", notify=hoverChanged)
    def highlights(self):
        return self._highlights

    @Property("QVariantList", notify=geometryChanged)
    def points(self):
        return self._point_rows

    @Property("QVariantList", notify=changed)
    def selectedPoints(self):
        return [
            self._component_lookup[key]["world"]
            for key in self.selection
            if key in self._component_lookup
        ]

    @Property("QVariantList", notify=geometryChanged)
    def lines(self):
        return self._lines

    @Property("QVariantList", notify=hoverChanged)
    def hoveredPoints(self):
        return [self.rows[self.hover_index][1]] if 0 <= self.hover_index < len(self.rows) else []

    @Property("QVariantList", notify=hoverChanged)
    def hoveredLines(self):
        return self._curve_lines.get(self.hover_curve, [])

    @Property("QVariantList", notify=geometryChanged)
    def componentRows(self):
        return self._component_rows

    @Property("QVariantMap", notify=changed)
    def selectedComponent(self):
        return self._component_lookup.get(self.selection[0], {}) if self.selection else {}

    @measured("ui", lambda owner: owner.controller.session.profiler)
    def notify(self):
        self.refresh_highlights()
        self._state.synchronize(state.data(self))
        self.changed.emit()

    def refresh_highlights(self):
        from .authoring_visuals import highlights

        self._highlights = highlights(self)
        self.hoverChanged.emit()

    @Property(bool, notify=changed)
    def active(self):
        return self.editing or bool(self.state.get("is_control"))

    @Property(bool, notify=changed)
    def visible(self):
        return bool(
            self.active
            and self.controller.selectedData.get("visible")
            and self.controller.session.workspace.handles
        )

    @Property("QVariantMap", notify=changed)
    def transformData(self):
        selected = self.selectedPoints
        if not self.active or self.state.get("kind") == "HOOK":
            return self.controller.selectedData.as_dict()
        if not selected:
            return self.controller.selectedData.as_dict() if self.state.get("is_control") else {}
        center = state.selection_center(self, selected)
        readonly = self.controller.selectedData.get("readonly", False) or state.imported_selection(
            self
        )
        return dict(
            id="components", trs=[*center, 0, 0, 0, 1, 1, 1], readonly=readonly, transformable=True
        )

    @measured("ui", lambda owner: owner.controller.session.profiler)
    def refresh(self):
        key = state.cache_key(self)
        if key == self._cache_key:
            self.notify()
            return
        self._cache_key = key
        try:
            authoring_picking.prepare(self)
        except ValueError as error:
            self.rows, self._lines = [], []
            self.controller.message = str(error)
        self.selection = state.retained_selection(self)
        self.publish_geometry()
        self.notify()

    def publish_geometry(self):
        from .authoring_visuals import layers

        self.interaction.rebuild()
        self._layers = layers(self)
        self._point_rows = self._points.tolist()
        self._component_rows = [
            dict(ref, key=state.component_key(ref), world=world, local=list(local))
            for ref, world, local in self.rows
        ]
        self._component_lookup = {row["key"]: row for row in self._component_rows}
        self.geometryChanged.emit()

    @Slot(bool)
    def setEditing(self, enabled):
        self.editing = enabled
        self.selection = []
        self.refresh()

    @Slot(str)
    def setCategory(self, category):
        self.category, self.selection = category, []
        self.refresh()

    @Slot(str, bool)
    def members(self, binding, assign):
        from .authoring_actions import binding_members

        binding_members(self, binding, assign)

    @Slot(str, float)
    def weights(self, binding, value):
        from .authoring_actions import selected_weights

        try:
            selected_weights(self, binding, value)
        except ValueError as error:
            self.controller.message = str(error)
            self.controller.notify()

    @Slot(str, str)
    def create(self, kind, shape):
        from .construction_creation import create

        create(self, kind, shape)

    def create_arguments(self, kind, shape):
        args = dict(
            kind=kind,
            shape=shape,
            parent=self.parent_scp(),
            name="Loft" if kind == "LOFT" else shape.title(),
        )
        return args

    def parent_scp(self):
        document = self.controller.session.document
        if not document.entities:
            return ""
        selected = self.state
        return (
            selected.get("follow")
            or (selected.get("id") if selected.get("id") in document.index.entities else "")
            or document.entities[0].id
        )

    @Slot(str, bool)
    def selectComponent(self, key, extend=False):
        if not extend:
            self.selection = []
        if key in self.selection:
            self.selection.remove(key)
        elif key:
            self.selection.append(key)
        self.notify()

    @Slot(str, str)
    def focusCurvePoint(self, curve, point):
        row = next(
            (
                r
                for r in self._component_rows
                if r.get("curve") == curve
                and r.get("point") == point
                and r.get("part") == "position"
            ),
            None,
        )
        if row is not None:
            self.selectComponent(row["key"], False)

    @Slot("QVariantList", "QVariantList", float, int, bool, bool, result=bool)
    def pick(self, origin, direction, radius, depth, select, extend):
        if (
            not self.visible
            or not self.controller.selectedData.get("pickable")
            or not len(self.rows)
        ):
            return False
        return authoring_picking.pick(self, origin, direction, radius, depth, select, extend)

    def update_hover(self, index, curve=""):
        if (index, curve) != (self.hover_index, self.hover_curve):
            self.hover_index, self.hover_curve = index, curve
            self.refresh_highlights()

    @Slot(str)
    def addDeformer(self, kind):
        from .authoring_actions import add_deformer

        add_deformer(self, kind)

    @Slot(str, "QVariantMap")
    def edit(self, operation, arguments):
        from .curve_context import command

        command(self, operation, arguments)

    @Slot(str, str, result="QVariantMap")
    def junctionOptions(self, curve, point):
        from .junction_tools import choices

        return choices(self.controller, curve, point)

    @Slot(str, str, "QVariant")
    def setting(self, operation, key, value):
        selected = self.controller.selection
        field = "control" if self.state.get("is_control") else "entity"
        self.controller.run(operation, {field: selected, key: value})
