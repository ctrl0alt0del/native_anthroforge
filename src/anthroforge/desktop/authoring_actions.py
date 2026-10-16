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
    session = editor.controller.session
    editor.drag_rows = selected_rows(editor)
    if any(ref["part"] in ("vertex", "base") for ref, _, _ in editor.drag_rows):
        raise ValueError(
            "Imported vertices are selectable for Hook membership, not direct editing."
        )
    editor.drag_mode = mode
    editor.drag_center = editor.transformData.get("trs", [0, 0, 0])[:3]
    editor.drag_control = selected_control_frame(editor)
    session.begin()


def selected_control_frame(editor):
    session = editor.controller.session
    if editor.state.get("is_control"):
        return control_frames.stable_frame(
            session, session.document.control(editor.controller.selection)
        )
    return None


def drag_transform(editor, axis, amount):
    session = editor.controller.session
    if session.history.before is None:
        return
    try:
        if editor.drag_control and (
            not editor.drag_rows or editor.drag_rows[0][0]["part"] == "control"
        ):
            return drag_control(editor, axis, amount)
        matrix = drag_matrix(editor, axis, amount)
        points = components.transformed(session.engine, [r[1] for r in editor.drag_rows], matrix)
        apply_points(editor, points)
        editor.controller.refresh()
    except ValueError as error:
        report_error(editor.controller, error)


def drag_control(editor, axis, amount):
    session = editor.controller.session
    world = construction.matrix(
        session.engine, drag_matrix(editor, axis, amount), editor.drag_control
    )
    control = session.document.control(editor.controller.selection)
    local = control_frames.authored_frame(session, control, world)
    values = session.engine.decompose(local)
    editor.controller.run(
        "control.transform", dict(control=editor.controller.selection, values=values)
    )


def drag_matrix(editor, axis, amount):
    engine = editor.controller.session.engine
    values = [0, 0, 0, 0, 0, 0, 1, 1, 1]
    index = axis + {"Move": 0, "Rotate": 3, "Scale": 6}[editor.drag_mode]
    values[index] = (
        max(0.01, 1 + amount)
        if editor.drag_mode == "Scale"
        else amount * (60 if editor.drag_mode == "Rotate" else 1)
    )
    pivot = engine.transform([*editor.drag_center, 0, 0, 0, 1, 1, 1])
    inverse = construction.matrix(engine, pivot, IDENTITY, relative=True)
    return construction.matrix(
        engine, construction.matrix(engine, pivot, engine.transform(values)), inverse
    )


def local_position(editor, reference, world):
    stage = "LATTICE" if reference["part"] == "lattice" else "CURVE"
    target = Target(reference["owner"], stage, reference.get("curve", ""))
    frame = deformer_operations.frame(editor.controller.session, target)
    inverse = construction.matrix(editor.controller.session.engine, frame, IDENTITY, relative=True)
    return components.transformed(editor.controller.session.engine, [world], inverse)[0].tolist()


def apply_points(editor, points):
    session, grouped = editor.controller.session, {}
    for (reference, _, _), world in zip(editor.drag_rows, points, strict=True):
        value = local_position(editor, reference, world)
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
