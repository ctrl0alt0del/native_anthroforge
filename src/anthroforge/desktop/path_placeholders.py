"""Invalid Parametric previews are display leases, never accepted document resources."""

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.parametric import ParametricSettings
from anthroforge.native.parametric import evaluate


class PathPlaceholders:
    def __init__(self):
        self.path = None

    def rows(self, controller):
        from .mirror_scene import presented

        missing = missing_paths(controller)
        if missing and self.path is None:
            self.path = straight_line(controller.session.engine)
        if not missing:
            self.path = None
            return []
        candidates = [*missing, *placeholder_mirrors(controller, missing)]
        return [
            placeholder(row, self.path.handle) for row in candidates if presented(controller, row)
        ]

    def resources(self):
        return (self.path,) if self.path is not None else ()


def placeholder_mirrors(controller, missing):
    sources = {row["id"] for row in missing}
    return [row for row in controller.mirror_records.values() if row["mirror_source"] in sources]


def missing_paths(controller):
    return [
        row
        for row in controller.construction.records.values()
        if row.get("engine") == "PARAMETRIC" and not row["asset"]
    ]


def straight_line(engine):
    curve = Curve((CurvePoint(), CurvePoint()), engine_settings=ParametricSettings(resolution=2))
    return evaluate(engine, curve, 0)[0]


def placeholder(row, handle):
    return dict(
        row,
        handle=handle,
        geometry_asset="placeholder:" + row["id"],
        key="placeholder:" + row["id"],
        chunk=0,
        pickable=False,
        placeholder=True,
        readonly=row["readonly"],
    )
