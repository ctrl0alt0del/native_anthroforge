"""Point presentation and native batched picking share the same projected world coordinates."""

from dataclasses import asdict

import numpy as np

from anthroforge.application import point_evaluation
from anthroforge.core.points import Anchor, Point
from anthroforge.native import components


def metadata(session, item):
    if not isinstance(item, Point):
        return {}
    location = point_evaluation.position(session.engine, session.document, item)
    return dict(
        point_position=item.position,
        world_position=location,
        binding=asdict(item.binding) if isinstance(item, Anchor) else None,
        color="#f3b45e" if isinstance(item, Anchor) else "#8fdb83",
    )


class PointScene:
    def __init__(self, controller):
        self.controller, self.rows = controller, []
        self.positions = np.empty((0, 3))

    def synchronize(self, records):
        desired = [r for r in records.values() if r.get("world_position") and r["pickable"]]
        if self.rows != desired:
            self.rows = desired
            self.positions = np.ascontiguousarray([r["world_position"] for r in desired])

    def hits(self, origin, direction, radius):
        if not self.rows:
            return []
        hits = components.hits(
            self.controller.session.engine, self.positions, origin, direction, radius
        )
        return [self.hit(int(i), d) for i, d in hits]

    def hit(self, index, distance):
        return dict(
            id=self.rows[index]["id"],
            distance=distance,
            point=self.positions[index].tolist(),
            face=-1,
            triangle=-1,
            vertex=-1,
        )
