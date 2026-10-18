"""Pin production-addon warm remapping and solve outputs for moved/resampled anchors."""

import importlib
import json
import sys
from dataclasses import replace
from pathlib import Path

from capture_routing_reference import fixtures, request, source_hashes


def warm_request(case, count):
    original = request(case["points"], closed=case["closed"], samples=case["samples"])
    moved = [list(point) for point in case["points"]]
    moved[1][0] += 0.6
    changed = request(moved, closed=case["closed"], samples=count)
    module = importlib.import_module("core.vcp.v3.warm")
    pins = (module._cyclic_pin_indices if case["closed"] else module._pin_indices)(
        original.anchors, case["samples"]
    )
    state = module._warm_state(
        case["result"], pins, original.anchors, "fixture", "fixture", case["closed"]
    )
    seed = module._remap(state, count, changed.anchors)
    return replace(changed, warm_seed=tuple(map(tuple, seed)))


def case_result(case, count):
    value = warm_request(case, count)
    result = importlib.import_module("core.vcp.v3.production").solve_v3(value).result
    return dict(
        name=case["name"] + "-" + str(count),
        original=case,
        points=[row.point for row in value.anchors],
        samples=count,
        warm_seed=value.warm_seed,
        result=result.points,
        validated=result.validated,
        termination=result.termination.value,
    )


def run(addon, output):
    sys.path.insert(0, str(addon))
    cases = [case_result(case, count) for case in fixtures()[:2] for count in (24, 32, 48)]
    payload = dict(sources=source_hashes(addon), cases=cases)
    output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps([dict(name=row["name"], validated=row["validated"]) for row in cases]))


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]))
