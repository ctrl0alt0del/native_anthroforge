"""Surface selectors project the shared role-aware choice service."""

from anthroforge.application import surface_options


def rows(controller):
    return surface_options.rows(controller.session)


def row(document, ref):
    return surface_options.row(document, ref)
