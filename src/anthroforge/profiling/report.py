"""Atomic portable JSON bundles; streaming export never copies the whole trace."""

import json
import os
import platform
import tempfile
from pathlib import Path
from time import perf_counter_ns, process_time_ns, thread_time_ns
from zipfile import ZIP_DEFLATED, ZipFile

from anthroforge import __version__

from .identity import build_identity
from .summary import Summary


def default_directory():
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
    return base / "AnthroForge" / "Profiles"


def environment():
    return dict(
        application_version=__version__,
        python=platform.python_version(),
        os=platform.system(),
        os_release=platform.release(),
        architecture=platform.machine(),
        cpu=platform.processor(),
        logical_cpus=os.cpu_count(),
        build=build_identity(),
    )


def write_json(archive, name, value):
    archive.writestr(name, json.dumps(value, indent=2, allow_nan=False).encode())


def write_trace(archive, buffer):
    summary = Summary()
    with archive.open("trace.json", "w") as stream:
        stream.write(b'{"traceEvents":[')
        for index, event in enumerate(buffer.events()):
            summary.observe(event)
            payload = json.dumps(event, separators=(",", ":"), allow_nan=False).encode()
            stream.write((b"," if index else b"") + payload)
        stream.write(b'],"displayTimeUnit":"ms"}')
    return summary.report()


def write_bundle(path, buffer, manifest):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=".afprofile-", dir=path.parent)
    os.close(handle)
    try:
        export_contents(temporary, buffer, manifest)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def export_contents(path, buffer, manifest):
    start, cpu, process = perf_counter_ns(), thread_time_ns(), process_time_ns()
    with ZipFile(path, "w", ZIP_DEFLATED, compresslevel=1) as archive:
        summary = write_trace(archive, buffer)
        manifest["export"] = export_costs(start, cpu, process)
        summary["profiler"] = manifest["profiler"]
        write_json(archive, "summary.json", summary)
        write_json(archive, "manifest.json", manifest)


def export_costs(start, cpu, process):
    return dict(
        wall_ns=perf_counter_ns() - start,
        thread_cpu_ns=thread_time_ns() - cpu,
        process_cpu_ns=process_time_ns() - process,
        scope="trace serialization and compression, excludes final ZIP close",
        process_cpu_scope="whole process during export; includes concurrent application work",
    )
