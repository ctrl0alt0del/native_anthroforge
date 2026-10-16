"""Measure complete edit/publication work; soft goals are reported, not assumed."""

from time import perf_counter

from primitive_acceptance import screenshot, settle
from PySide6.QtTest import QTest

from anthroforge.core.metrics import Metrics


def setup(controller):
    controller.authoring.create("LOFT", "")
    settle(controller)
    entity = controller.selection
    controller.run("primitive.update", dict(entity=entity, samples=512, strips=64))
    controller.run("thickness.update", dict(entity=entity, thickness=0.02))
    settle(controller)
    controller.authoring.addDeformer("LATTICE")
    settle(controller)
    cage = controller.selection
    controller.run("lattice.resize", dict(control=cage, resolution=[10, 10, 10]))
    settle(controller)
    return entity, cage


def displayed(controller, entity):
    return next(
        row["handle"] for row in controller.render_model.active_rows() if row["id"] == entity
    )


def watch_replacement(controller, entity, old):
    seen = []
    for _ in range(600):
        QTest.qWait(5)
        visible = [r for r in controller.render_model.rows if r["active"] and r["id"] == entity]
        assert visible and len({r["handle"] for r in visible}) == 1
        if controller.render_model.pending:
            assert displayed(controller, entity) == old
            seen.append(True)
        if not controller.session.scheduler.blocked and not controller.render_model.pending:
            QTest.qWait(100)
            return bool(seen)
    raise AssertionError("Large geometry replacement did not finish.")


def edit_and_measure(controller, entity, cage):
    metrics = controller.session.scheduler.metrics
    old = displayed(controller, entity)
    controller.last_frame = perf_counter()
    started = perf_counter()
    controller.run("lattice.point", dict(control=cage, index=999, position=[0.5, 0.5, 1.2]))
    metrics.observe("edit_command", perf_counter() - started)
    staged = watch_replacement(controller, entity, old)
    assert displayed(controller, entity) != old
    return staged


def drag_and_cancel(controller, cage):
    for step in range(18):
        started = perf_counter()
        controller.run(
            "lattice.point", dict(control=cage, index=999, position=[0.5, 0.5, 0.7 + step * 0.02])
        )
        controller.session.scheduler.metrics.observe("edit_command", perf_counter() - started)
        QTest.qWait(12)
    settle(controller)
    assert any(j.obsolete for j in controller.session.scheduler.jobs)


def component_picking(controller):
    for step in range(120):
        started = perf_counter()
        controller.authoring.pick([step / 120 - 0.5, 0, 2], [0, 0, -1], 0.01, 0, False, False)
        controller.session.scheduler.metrics.observe("component_picking", perf_counter() - started)


def verify(controller, window):
    window.resize(1500, 950)
    entity, cage = setup(controller)
    controller.session.scheduler.metrics = Metrics()
    controller.performance_job_start = len(controller.session.scheduler.jobs)
    retained = edit_and_measure(controller, entity, cage)
    drag_and_cancel(controller, cage)
    component_picking(controller)
    screenshot(window, "large-publication")
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors
    return report(controller, entity, retained)


def report(controller, entity, retained):
    computation_metrics(controller)
    mesh = controller.session.assets[controller.session.document.entity(entity).asset].mesh
    return dict(
        vertices=mesh.counts[0],
        triangles=mesh.counts[3],
        chunks=mesh.counts[4],
        cage_points=1000,
        retained_during_staging=retained,
        metrics=controller.session.scheduler.metrics.report(),
    )


def computation_metrics(controller):
    for job in controller.session.scheduler.jobs[controller.performance_job_start :]:
        if job.kind == "construction" and job.compute_ms:
            name = "compute_accepted" if job.state == "succeeded" else "compute_superseded"
            controller.session.scheduler.metrics.observe(name, job.compute_ms / 1000)
