"""Field selection is presentation; weight assignment uses the shared operation policy."""


def edit(editor, name):
    editor.controller.cancelViewportTools()
    editor.tissue_context = (name, "")
    editor.category, editor.editing, editor.selection = "TISSUE_FIELD", True, []
    editor.refresh()


def assign(editor, value):
    chosen = [
        r for r in editor.componentRows if r["key"] in editor.selection and r["part"] == "field"
    ]
    if not chosen:
        return
    editor.controller.run("tissue.field.assign", assignment(chosen, value))


def assignment(chosen, value):
    first = chosen[0]
    return dict(
        target=first["owner"],
        name=first["field"],
        topology=first["topology"],
        indices=[r["index"] for r in chosen],
        value=value,
    )
