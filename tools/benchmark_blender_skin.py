"""Run the same fixed-input benchmark inside the addon's actual Blender worker runtime."""

import importlib
import sys
from pathlib import Path

import bpy


def main():
    addon, metrics, *arguments = sys.argv[sys.argv.index("--") + 1 :]
    sys.path.insert(0, addon)
    importlib.import_module("adapters.draft_skin.vendor").ensure_worker_dependencies()
    sys.path.append(metrics)  # psutil's Windows ABI3 extension; numerical packages stay pinned.
    sys.path.insert(0, str(Path(__file__).parent))
    benchmark = importlib.import_module("skin_optimization_benchmark")
    sys.argv = [__file__, *arguments, "--addon", addon]
    print("Blender worker runtime:", bpy.app.version_string, sys.version, flush=True)
    benchmark.main()


if __name__ == "__main__":
    main()
