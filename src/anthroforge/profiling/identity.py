"""Build provenance without network access; packaged identities are pinned at staging."""

import json
import subprocess
from pathlib import Path


def build_identity():
    packaged = Path(__file__).resolve().parents[1] / "_runtime" / "build.json"
    if packaged.is_file():
        return json.loads(packaged.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[3]
    try:
        revision = git(root, "rev-parse", "HEAD").strip()
        dirty = bool(git(root, "status", "--porcelain", "--untracked-files=no").strip())
        return dict(revision=revision, tracked_changes=dirty, packaged=False)
    except (OSError, subprocess.SubprocessError):
        return dict(revision="unavailable", packaged=False)


def git(root, *arguments):
    return subprocess.check_output(
        ["git", *arguments],
        cwd=root,
        text=True,
        stderr=subprocess.DEVNULL,
        timeout=2,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
