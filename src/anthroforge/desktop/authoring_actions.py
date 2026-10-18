"""Small construction interaction workflows built from application commands."""

from anthroforge.application import control_frames, deformer_operations
from anthroforge.core.construction import Target
from anthroforge.core.entities import IDENTITY
from anthroforge.native import components, construction

from . import authoring_state


def selected_rows(editor):
    return [row for row in editor.rows if authoring_state.component_key(row[0]) in editor.selection]


def add_deformer(editor, kind):
    controller = editor.controller
    if not controller.selection:
        return
    controller.run("begin", {})
    try:
        control = create_control(editor, kind)
        bind_selection(editor, control, kind)
        controller.run("commit", {})
        controller.select(control)
    except Exception as error:
        controller.run("cancel", {})
        report_error(controller, error)


def create_control(editor, kind):
    session, parent = editor.controller.session, editor.parent_scp()
    options = dict(kind=kind, entity=parent, name=kind.title())
    rows = selected_rows(editor)
    if kind == "HOOK" and rows:
        center = authoring_state.selection_center(editor, [row[1] for row in rows])
        inverse = construction.matrix(
            session.engine, session.document.entity(parent).matrix, IDENTITY, relative=True
        )
        local = session.engine.world_point(inverse, center)
        options["values"] = [*local, 0, 0, 0, 1, 1, 1]
    return session.command("control.create", **options)


def report_error(controller, error):
    controller.message = str(error)
    controller.notify()


def bind_selection(editor, control, kind):
    session, selected = editor.controller.session, editor.controller.selection
    rows = selected_rows(editor)
    if kind == "HOOK" and rows:
        groups = binding_groups(rows)
        for (stage, component), indices in groups.items():
            target = dict(
                owner=selected,
                stage=stage,
                component=component,
            )
            session.command("deformer.add", control=control, target=target, indices=indices)
    else:
        stage = "LATTICE" if editor.state.get("kind") == "LATTICE" else "GEOMETRY"
        session.command("deformer.add", control=control, target=dict(owner=selected, stage=stage))


def binding_groups(rows):
    groups = {}
    for reference, _, _ in rows:
        key = reference_target(reference)
        groups.setdefault(key, []).append(reference["index"])
    return groups


def reference_target(reference):
    if reference.get("curve"):
        return "CURVE", reference["curve"]
    if reference.get("piece"):
        return "BASE", reference["piece"]
    return ("LATTICE" if reference["part"] == "lattice" else "GEOMETRY"), ""


def binding_members(editor, binding, assign):
    session = editor.controller.session
    target = deformer_operations.locate(session, binding).target
    rows = [r for r in editor.rows if reference_target(r[0]) == (target.stage, target.component)]
    if assign:
        selected = [
            r[0]["index"] for r in rows if authoring_state.component_key(r[0]) in editor.selection
        ]
        editor.controller.run("deformer.update", dict(binding=binding, indices=selected))
    else:
        indices = member_indices(session, binding, rows)
        editor.selection = [
            authoring_state.component_key(r[0]) for r in rows if r[0]["index"] in indices
        ]
        editor.notify()


def member_indices(session, binding, rows):
    current = deformer_operations.locate(session, binding)
    return (
        session.command("deformer.members", binding=binding)
        if current.restrict
        else [r[0]["index"] for r in rows]
    )


def selected_weights(editor, binding, value):
    current = next(b for b in editor.state["deformers"] if b["id"] == binding)
    target = current["target"]
    rows = [
        r for r in editor.rows if reference_target(r[0]) == (target["stage"], target["component"])
    ]
    selected = {
        r[0]["index"] for r in rows if authoring_state.component_key(r[0]) in editor.selection
    }
    if not selected:
        raise ValueError("Select target points or vertices before assigning their weight.")
    weights = current["weights"] or [1.0] * len(rows)
    weights = [value if index in selected else old for index, old in enumerate(weights)]
    editor.controller.run("deformer.update", dict(binding=binding, weights=weights))


def start_transform(editor, mode):
    editor.drag_mode = mode
    capture_transform(editor)
    editor.controller.session.begin()


def capture_transform(editor):
    editor.drag_rows = transform_rows(editor)
    if any(ref["part"] in ("vertex", "base") for ref, _, _ in editor.drag_rows):
        raise ValueError(
            "Imported vertices are selectable for Hook membership, not direct editing."
        )
    editor.drag_center = editor.transformData.get("trs", [0, 0, 0])[:3]
    editor.drag_control = selected_control_frame(editor)


def transform_rows(editor):
    selected = selected_rows(editor)
    if editor.drag_mode == "Move":
        return selected
    points = {
        (r["owner"], r.get("curve"), r.get("point"))
        for r, _, _ in selected
        if r["part"] == "position"
    }
    return [
        row
        for row in editor.rows
        if authoring_state.component_key(row[0]) in editor.selection
        or (row[0]["owner"], row[0].get("curve"), row[0].get("point")) in points
    ]


def selected_control_frame(editor):
    session = editor.controller.session
    if editor.state.get("is_control"):
        return control_frames.stable_frame(
            session, session.document.control(editor.controller.selection)
        )
    return None


def drag_transform(editor, axis, amount):
    from .transform_delta import axis_values

    transform_delta(editor, axis_values(editor.drag_mode, axis, amount))


def transform_delta(editor, values):
    session = editor.controller.session
    if session.history.before is None:
        return
    try:
        apply_delta(editor, values)
        editor.controller.refresh()
    except ValueError as error:
        report_error(editor.controller, error)


def apply_delta(editor, values):
    from .transform_delta import matrix

    if editor.drag_control and (
        not editor.drag_rows or editor.drag_rows[0][0]["part"] == "control"
    ):
        return drag_control(editor, values)
    engine = editor.controller.session.engine
    delta = matrix(engine, editor.drag_center, values)
    points = components.transformed(engine, [r[1] for r in editor.drag_rows], delta)
    apply_points(editor, points)


def drag_control(editor, delta):
    from .transform_delta import object_values

    session = editor.controller.session
    initial = session.engine.decompose(editor.drag_control)
    world = session.engine.transform(object_values(session.engine, initial, delta))
    control = session.document.control(editor.controller.selection)
    local = control_frames.authored_frame(session, control, world)
    values = session.engine.decompose(local)
    editor.controller.run("control.transform", dict(control=control.id, values=values))


def point_target(reference):
    stage = "LATTICE" if reference["part"] == "lattice" else "CURVE"
    return Target(reference["owner"], stage, reference.get("curve", ""))


def local_positions(editor, points):
    session, groups = editor.controller.session, {}
    if len(points) != len(editor.drag_rows):
        raise ValueError("Transform points must match the selected components.")
    for index, (reference, _, _) in enumerate(editor.drag_rows):
        groups.setdefault(point_target(reference), []).append(index)
    result = [None] * len(points)
    for target, indices in groups.items():
        frame = deformer_operations.frame(session, target)
        inverse = construction.matrix(session.engine, frame, IDENTITY, relative=True)
        local = components.transformed(session.engine, [points[i] for i in indices], inverse)
        for index, value in zip(indices, local.tolist(), strict=True):
            result[index] = value
    return result


def apply_points(editor, points):
    session, grouped = editor.controller.session, {}
    local = local_positions(editor, points)
    for (reference, _, _), value in zip(editor.drag_rows, local, strict=True):
        if reference["part"] == "lattice":
            update_lattice_point(session, reference, value)
        else:
            key = (reference["owner"], reference["curve"], reference["point"])
            grouped.setdefault(key, {})[reference["part"]] = value
    for (entity, curve, point), options in grouped.items():
        session.command("point.update", entity=entity, curve=curve, point=point, **options)


def update_lattice_point(session, reference, value):
    session.command(
        "lattice.point", control=reference["owner"], index=reference["index"], position=value
    )
