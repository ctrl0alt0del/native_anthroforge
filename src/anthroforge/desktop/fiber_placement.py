"""Provisional surface-click points; the shared operation owns confirmed binding and solving."""

from .curve_interaction import surface_hit
from .image_tools import context_owner


class FiberPlacement:
    def __init__(self, tool):
        self.tool, self.points = tool, []

    def pointer(self, ray, press):
        hit = surface_hit(self.tool.controller, ray[:3], ray[3:6], exclude_current=False)
        self.tool.hover = hit.get("point", [])
        if press and hit:
            self.points.append(dict(position=list(hit["point"]), target=hit["id"]))
            self.tool.pointsAdded.emit([hit["point"]])

    def finish(self):
        if len(self.points) < 2:
            self.tool.require_more_points()
            return
        result = self.tool.controller.run(
            "fiber.place", dict(points=self.points, owner=context_owner(self.tool.controller))
        )
        if result:
            jobs = self.tool.controller.session.scheduler.jobs
            self.tool.created.extend(next(job.outputs for job in jobs if job.id == result))
            self.tool.cancel()

    def pop(self):
        if self.points:
            self.points.pop()
        self.tool.resetPreview.emit()
        self.tool.pointsAdded.emit([row["position"] for row in self.points])
        self.tool.changed.emit()
