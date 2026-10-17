"""Collect compact, machine-readable qualification evidence without copying trace payloads."""

import argparse
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from anthroforge.profiling.identity import build_identity


def read(path):
    return json.loads(path.read_text())


def gui_trials(folder):
    result = []
    for path in sorted(folder.glob("*.json")):
        item = read(path)
        if "trials" in item:
            result.append(gui_case(path, item))
    return result


def gui_case(path, item):
    return dict(
        file=path.name,
        mode=item["mode"],
        interaction=item["interaction"],
        activity_open=item["activity_open"],
        system_load=item["system_load"],
        trials=[compact_trial(t) for t in item["trials"]],
    )


def compact_trial(trial):
    fields = (
        "snapping",
        "snap_hits",
        "events",
        "handler_ms",
        "frame_ms",
        "job_compute_ms",
        "process_cpu_s",
    )
    return {key: trial[key] for key in fields}


def capture(path):
    with ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        events = json.loads(archive.read("trace.json"))["traceEvents"]
    return dict(
        file=str(path),
        complete=manifest["complete"],
        storage=manifest["storage"],
        losses=manifest["losses"],
        build=manifest["environment"]["build"],
        **capture_events(events),
    )


def capture_events(events):
    native = Counter(e["name"] for e in events if e.get("cat") == "native")
    models = Counter(e["name"] for e in events if "model" in e.get("cat", ""))
    curve_models = sum(
        "model" in e.get("cat", "") and e.get("args", {}).get("object") == "curveChoice"
        for e in events
    )
    return dict(
        native_calls=dict(native),
        model_events=dict(models),
        curve_choice_model_events=curve_models,
    )


def measurements(folder):
    return dict(
        document_and_history=read(folder / "stage4/scaling.json"),
        geometry=read(folder / "stage3/comparison.json"),
        soak=read(folder / "stage4/soak.json"),
        large_geometry={
            name: read(folder / f"large-{name}.json") for name in ("baseline", "candidate")
        },
        gui=gui_trials(folder / "final-comparison"),
    )


def profiles(folder):
    paths = sorted((folder / "final-comparison").glob("*.afprofile.zip"))
    paths += [folder / "stage3/geometry.afprofile.zip", folder / "stage4/soak.afprofile.zip"]
    return [capture(path) for path in paths]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = dict(
        schema=1,
        collected_from=build_identity(),
        baseline="d810557795c2af002da0d86cfa7797317f9af4c4",
        measurements=measurements(args.folder),
        captures=profiles(args.folder),
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
