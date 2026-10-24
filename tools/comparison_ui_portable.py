"""Compiled comparison adapters and controls, with a relocated offscreen test harness."""

import json
import sys
from pathlib import Path

from shortcut_inspection_portable import launch, prepare

HARNESS = """
    Timer {
        interval: 500; running: true
        onTriggered: {
            inspectorHeader.shortcuts=true;
            workspace.shortcutPanel.editing.select(SHORTCUT_ID);
            workspace.shortcutPanel.editing.inspectionView.activate(true);
            workspace.shortcutComparison.capture(SHORTCUT_ID);
            workspace.shortcutComparison.setMode("Before");
        }
    }
    Timer {
        interval: 1100; running: true
        onTriggered: {
            workspace.run("driver.value",{driver:SHORTCUT_ID,value:0.08});
            console.log("AF_EDIT_MODE="+workspace.shortcutComparison.state.mode);
            workspace.shortcutComparison.setMode("Overlay");
            workspace.shortcutComparison.compare();
        }
    }
    Timer {
        interval: 1800; running: true
        onTriggered: {
            console.log("AF_COMPARISON="+JSON.stringify(workspace.shortcutComparison.state));
        }
    }
"""


def run(distribution, project, output):
    output.mkdir(parents=True, exist_ok=True)
    executable = prepare(distribution, project, output, HARNESS)
    result = launch(executable, project, output)
    smoke = json.loads(result.stdout.strip())
    assert smoke["desktop_smoke"] and not smoke["warnings"], smoke
    assert "AF_EDIT_MODE=After" in result.stderr, result.stderr
    row = next(
        r.split("AF_COMPARISON=", 1)[1] for r in result.stderr.splitlines() if "AF_COMPARISON=" in r
    )
    state = json.loads(row)
    assert state["active"] and state["mode"] == "Overlay" and not state["error"], state
    (output / "comparison-ui.json").write_text(json.dumps(dict(passed=True, state=state), indent=2))


if __name__ == "__main__":
    run(*(Path(arg).resolve() for arg in sys.argv[1:4]))
