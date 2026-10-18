"""Real gesture reports must explain input changes, base reuse and displayed ownership."""

import json
from pathlib import Path
from zipfile import ZipFile

import profiler_acceptance as acceptance
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete

from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime
from anthroforge.profiling import report

OUTPUT = Path("build/inspection-018/profiles").resolve()


def diagnostics(path):
    with ZipFile(path) as archive:
        summary = json.loads(archive.read("summary.json"))
        trace = json.loads(archive.read("trace.json"))["traceEvents"]
    evidence = summary["diagnostics"]
    assert evidence["invalidation_reasons"]["input_output_changed"]
    assert evidence["cache_events"]["hit:"]
    peak = evidence["geometry_memory"]["peak_observed_bytes"]
    assert all(peak[key] > 0 for key in ("document", "history", "viewport_displayed"))
    assert any(e["ph"] == "C" and e["name"] == "geometry_bytes" for e in trace)
    assert any(e["cat"] == "revision" for e in trace)
    return dict(path=path, diagnostics=evidence, frames=summary["frame_submission_intervals"])


def verify():
    results = json.loads((OUTPUT / "acceptance.json").read_text())
    evidence = [diagnostics(row["path"]) for row in results]
    (OUTPUT / "diagnostics.json").write_text(json.dumps(evidence, indent=2))
    print(json.dumps(dict(diagnostic_captures=len(evidence), complete=True)))


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    acceptance.OUTPUT = OUTPUT
    report.default_directory = lambda: OUTPUT
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            acceptance.run()
            verify()
        finally:
            delete(app)
