"""Serializable context for the isolated drag investigation."""

import json
import os
import platform
import subprocess
from datetime import UTC, datetime

import PySide6

JOB_FIELDS = (
    "id",
    "key",
    "kind",
    "state",
    "origin",
    "epoch",
    "created",
    "started",
    "finished",
    "cancel_requested",
    "obsolete",
    "execution",
    "prepare_ms",
    "compute_ms",
    "publish_ms",
)


def metadata(args):
    options = ("events", "repeats", "interval", "mode", "intervention", "height", "spans")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    return dict(
        recorded_utc=datetime.now(UTC).isoformat(),
        source_commit=commit,
        python=platform.python_version(),
        qt=PySide6.__version__,
        platform=platform.platform(),
        options={name: getattr(args, name) for name in options},
        environment={name: os.getenv(name) for name in ("QSG_RENDER_LOOP", "QSG_RHI_BACKEND")},
        clock="perf_counter seconds; durations explicitly suffixed ms or s",
        frames="GUI receipt of frameSwapped; not GPU/present timestamps",
        profiling="central wall spans if enabled; no sampling; app metrics remain enabled",
    )


def job_records(jobs):
    return [{field: getattr(job, field) for field in JOB_FIELDS} for job in jobs]


def save_recording(args, results, warnings=None):
    data = dict(
        schema_version=1,
        metadata=args.metadata,
        results=results,
        complete=warnings is not None,
        warnings=warnings or [],
    )
    temporary = args.output.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temporary.replace(args.output)
