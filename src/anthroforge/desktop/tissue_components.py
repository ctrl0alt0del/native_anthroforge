"""Tissue parameter controls share component selection without exposing derived vertex edits."""


def projected(item):
    return dict(id=item.id, name=item.name, kind="TISSUE", source=item.source)


def edit(editor, part, side):
    editor.controller.viewport_view.cancelViewportTools()
    editor.tissue_context = (part, side)
    editor.category, editor.editing, editor.selection = "TISSUE_CONTROL", True, []
    editor.refresh()
    if editor.componentRows:
        editor.selectComponent(editor.componentRows[0]["key"], False)
