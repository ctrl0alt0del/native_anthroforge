"""Adopt one asynchronously created object without stealing a newer editing context."""


class CreationSelection:
    def __init__(self, controller):
        self.controller, self.pending = controller, None

    def signature(self):
        controller, session = self.controller, self.controller.session
        return (
            session,
            session.document.id,
            session.active_workspace,
            session.scheduler.epoch,
            tuple(controller.selection_view.selectedObjects),
            controller.authoring.editing,
        )

    def create(self, operation, arguments):
        context = self.signature()
        self.pending = None
        result = self.controller.run(operation, arguments)
        if isinstance(result, str) and result in self.controller.session.document.registry.authored:
            self.accept(result)
            return result
        registry = self.controller.session.scheduler.registry
        job = registry.by_id.get(result.get("job_id") if isinstance(result, dict) else result)
        target = created_target(result, job)
        if target:
            self.pending = context, target
            self.synchronize()
        return result

    def synchronize(self):
        if self.pending is None:
            return
        context, target = self.pending
        session = self.controller.session
        if context != self.signature():
            self.pending = None
        elif target in session.document.registry.records:
            if session.history.before is None:
                self.accept(target)
        elif not session.scheduler.registry.matching("output", (target,)):
            self.pending = None

    def accept(self, target):
        self.pending = None
        self.controller.authoring.setEditing(False)
        self.controller.selection_view.select(target)


def created_target(result, job):
    if job is None:
        return ""
    target = result.get("object_id", "") if isinstance(result, dict) else ""
    if target in job.outputs:
        return target
    return next(iter(job.outputs)) if len(job.outputs) == 1 else ""
