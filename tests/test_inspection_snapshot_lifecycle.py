"""Export leases outlive API replacement and numerical scenes need no Qt runtime."""

import gc
import subprocess
import sys
from threading import Event
from weakref import ref

import numpy as np

from anthroforge.application import inspection_scene_bundle as bundle
from anthroforge.application import inspection_snapshot_export as exporting
from anthroforge.application import inspection_snapshots as snapshots
from tests.test_inspection_snapshots import capture
from tests.test_surface_preview import loops, preview


def test_export_holds_lease_until_job_retirement(session, tmp_path):
    _, key = capture(session)
    frozen = snapshots.selected(session, key)
    held = ref(frozen)
    job = export_job(tmp_path, frozen)
    del frozen
    session.command("inspection.release", snapshot=key)
    assert held() is not None
    session.command("curve.conversion.cancel")
    session.scheduler.submit(job)
    session.wait()
    assert job.state == "succeeded", job.error
    gc.collect()
    assert held() is None


def export_job(root, frozen):
    view = exporting.view_settings(frozen, {})
    return exporting.make_job(root / "out.zip", frozen, False, view)


def test_scene_roundtrip_preserves_every_canonical_buffer(session, tmp_path):
    token = preview(session, curves=loops(session))
    result = session.command("inspection.capture", kind="surface", token=token)
    frozen = snapshots.selected(session, result["snapshot"])
    bundle.write(tmp_path, frozen, exporting.view_settings(frozen, None), Event())
    metadata, restored = bundle.read(tmp_path, session.engine)
    assert metadata["snapshot"] == frozen.identity
    for old, new in zip(frozen.layers, restored, strict=True):
        assert old.identity == new.identity and old.frame == new.frame
        for name in snapshots.metadata(old)["buffers"]:
            np.testing.assert_array_equal(snapshots.array(old, name), snapshots.array(new, name))


def test_numerical_capture_export_process_does_not_import_qt(tmp_path):
    process = subprocess.run(
        [sys.executable, "-c", numerical_script(), str(tmp_path / "a.afinspection.zip")],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert process.returncode == 0, process.stderr


def numerical_script():
    return (
        "import sys; from pathlib import Path; "
        "from anthroforge.application.session import Session; "
        "from tests.test_inspection_snapshots import capture; "
        "s=Session(); key,snapshot=capture(s); "
        "s.command('inspection.export',snapshot=snapshot,images=False,wait=True,path=sys.argv[1]); "
        "s.close(); assert not any(k.startswith('PySide6') for k in sys.modules)"
    )


def test_driver_dependencies_are_valid_preview_reads_and_become_stale(session):
    from tests.test_curve_conversion import preview, source
    from tests.test_driving_formulas import driver

    target = source(session)
    key, _ = driver(session, target, "value", value=16, kind="INTEGER")
    session.wait()
    token = preview(session, target)
    result = session.command("inspection.capture", kind="curve_conversion", token=token)
    assert result["current"]
    session.command("driver.value", driver=key, value=20)
    session.wait()
    assert not session.command("inspection.capture.status", snapshot=result["snapshot"])["current"]


def test_profiler_attributes_snapshot_resources_after_preview_cancel(session):
    _, key = capture(session)
    value = snapshots.selected(session, key)
    resources = {layer.resource for layer in value.layers if layer.resource}
    session.command("curve.conversion.cancel")
    owners = session.profiler.resources.owners()
    assert resources <= owners["inspection_capture"]
    session.command("inspection.release", snapshot=key)
    assert not session.profiler.resources.owners()["inspection_capture"]
