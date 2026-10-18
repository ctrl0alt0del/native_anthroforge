"""Transient curve insertion and snapping; authored edits use shared commands."""

from time import perf_counter

from PySide6.QtCore import Property, QObject, Signal, Slot

from anthroforge.native import curve_queries, scene

from . import authoring_state, curve_context


class CurveInteraction(QObject):
    changed = Signal()

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.preview, self.snap = {}, {}
        self.offset = 0.0
        self.query = None
        self.context = None

    @Property("QVariantMap", notify=changed)
    def state(self):
        return dict(preview=self.preview, snap=self.snap, offset=self.offset)

    def rebuild(self):
        editor, controller = self.editor, self.editor.controller
        entity, curves = curve_context.owner(editor), curve_context.curves(editor)
        enabled = editor.editing and editor.category == "CURVE" and curves
        self.query = make_query(controller.session, entity, curves) if enabled else None
        self.context = authoring_state.cache_key(editor)
        self.clearPreview()

    @Slot()
    def clearPreview(self):
        if self.preview:
            self.preview = {}
            self.changed.emit()

    @Slot()
    def clearSnap(self):
        if self.snap or self.offset:
            self.snap = {}
            self.offset = 0.0
            self.changed.emit()

    @Slot(float)
    def adjustOffset(self, amount):
        self.offset += amount
        self.changed.emit()

    @Slot()
    def resetOffset(self):
        if self.offset:
            self.offset = 0.0
            self.changed.emit()

    @Slot("QVariantList", "QVariantList")
    def updatePreview(self, origin, direction):
        editor = self.editor
        eligible = self.query and editor.visible and editor.controller.selectedData.get("pickable")
        if not eligible or editor.controller.session.history.before is not None:
            return self.clearPreview()
        started = perf_counter()
        preview = self.query.closest(origin, direction)
        editor.controller.session.scheduler.metrics.observe(
            "curve_projection", perf_counter() - started
        )
        self.preview = preview if 1e-4 < preview.get("parameter", 0) < 1 - 1e-4 else {}
        self.changed.emit()

    @Slot(result=bool)
    def insert(self):
        if not self.preview or self.context != authoring_state.cache_key(self.editor):
            return False
        controller, preview = self.editor.controller, self.preview.copy()
        try:
            point = insert_point(controller, preview)
            controller.refresh()
            self.select_inserted(preview["curve"], point)
            return True
        except ValueError as error:
            controller.message = str(error)
            controller.notify()
            return False

    def select_inserted(self, curve, point):
        ref = dict(
            owner=self.editor.controller.selection, curve=curve, point=point, part="position"
        )
        self.editor.selectComponent(authoring_state.component_key(ref), False)

    @Slot("QVariantList", "QVariantList", float, bool, result="QVariantMap")
    def pressPoint(self, origin, direction, radius, extend):
        editor = self.editor
        if not editor.visible or not editor.controller.selectedData.get("pickable"):
            return {}
        index = editor._point_index.pick(origin, direction, radius)
        ref = editor.rows[index][0] if 0 <= index < len(editor.rows) else {}
        if not ref.get("curve"):
            return {}
        key = authoring_state.component_key(ref)
        if not extend and key not in editor.selection:
            editor.selectComponent(key, False)
        editor.drag_anchor = key
        return dict(key=key, position=editor.rows[index][1])

    @Slot(bool)
    def beginPointDrag(self, extend):
        editor = self.editor
        if editor.drag_anchor not in editor.selection:
            editor.selectComponent(editor.drag_anchor, extend)

    @Slot(bool)
    def clickPoint(self, extend):
        if extend:
            self.editor.selectComponent(self.editor.drag_anchor, True)

    @Slot("QVariantList", "QVariantList", "QVariantList", bool, result="QVariantList")
    def movement(self, origin, direction, values, enabled):
        editor = self.editor
        if not enabled:
            self.resetOffset()
        anchor = snap_anchor(editor) if enabled else None
        self.snap = surface_hit(editor.controller, origin, direction) if anchor else {}
        self.snap = offset_hit(self.snap, self.offset)
        self.changed.emit()
        if not self.snap:
            return values
        return [
            *(value - base for value, base in zip(self.snap["point"], anchor, strict=True)),
            *values[3:],
        ]


def snap_anchor(editor):
    rows = [(ref, world) for ref, world, _ in editor.drag_rows if ref["part"] == "position"]
    preferred = getattr(editor, "drag_anchor", "")
    return next(
        (world for ref, world in rows if authoring_state.component_key(ref) == preferred),
        rows[0][1] if rows else None,
    )


def surface_hit(controller, origin, direction):

    started = perf_counter()
    hits = scene.pick(
        controller.session.engine,
        controller.snap_handles,
        controller.snap_matrices,
        origin,
        direction,
    )
    controller.session.scheduler.metrics.observe("surface_snap", perf_counter() - started)
    hit = next((h for h in hits if controller.snap_ids[int(h[0])] != controller.selection), None)
    return surface_record(controller, hit) if hit is not None else {}


def surface_record(controller, hit):
    from .scene_state import hit_record

    index = int(hit[0])
    normal = scene.surface_normal(
        controller.session.engine,
        int(controller.snap_handles[index]),
        controller.snap_matrices[index],
        int(hit[3]),
    )
    return dict(hit_record(controller.snap_ids, hit), normal=normal)


def offset_hit(hit, offset):
    if not hit:
        return {}
    position = [p + offset * n for p, n in zip(hit["point"], hit["normal"], strict=True)]
    return dict(hit, surface=hit["point"], point=position)


def make_query(session, entity, curves):
    return curve_queries.CurveQuery(session.engine, curves, curve_context.frame(session, entity))


def insert_point(controller, preview):
    args = {key: preview[key] for key in ("curve", "segment", "parameter")}
    operation = (
        "curve.subdivide" if controller.selectedData.get("is_construction") else "curve.split"
    )
    if operation == "curve.split":
        args["entity"] = controller.selection
    return controller.session.command(operation, **args)
