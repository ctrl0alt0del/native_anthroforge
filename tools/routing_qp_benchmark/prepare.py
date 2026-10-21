"""Generate a guarded experimental solve unit without changing the shipped native sources."""

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "build/routing-piqp/source"
NATIVE = ROOT / "native"
PATCHES = (
    (
        "struct AfV3SqpState {",
        "struct AfV3SqpState {\n    std::shared_ptr<afbench::Context> qp_lab;",
    ),
    ("static bool af_v3_sqp_candidate(", "static bool af_v3_sqp_candidate_current("),
    (
        "multipliers=af_v3_sqp_active_set(state,responses,active,state.candidate);\n"
        "    state.trust_boundary=af_v3_sqp_trust(state,state.candidate);return true;",
        "multipliers=af_v3_sqp_active_set(state,responses,active,state.candidate);\n"
        "    return true;",
    ),
    (
        "static double af_v3_sqp_spacing_energy(",
        '#include "candidate.hpp"\n\nstatic double af_v3_sqp_spacing_energy(',
    ),
)


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("Benchmark insertion point changed; review the solver before adapting it.")
    return text.replace(old, new)


def donor():
    name = "af_fiber_v3_native_sqp.hpp"
    metadata = json.loads((NATIVE / "migration/routing/sources.json").read_text())
    entry = next(row for row in metadata if row["file"] == name)
    path = NATIVE / "migration/routing" / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
    return path.read_text()


def instrument(text):
    for old, new in PATCHES:
        text = replace_once(text, old, new)
    return text


def copy_sources():
    (STAGE / "native/src").mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        NATIVE / "migration/routing", STAGE / "native/migration/routing", dirs_exist_ok=True
    )
    for name in ("routing_solve.cpp", "routing_internal.hpp", "routing_kernel.hpp"):
        shutil.copy2(NATIVE / "src" / name, STAGE / "native/src" / name)
    kernel = STAGE / "native/src/routing_kernel.hpp"
    kernel.write_text('#include "lab.hpp"\n' + kernel.read_text())
    solve = STAGE / "native/src/routing_solve.cpp"
    solve.write_text(solve.read_text() + '\n#include "exports.hpp"\n')


def main():
    copy_sources()
    path = STAGE / "native/migration/routing/af_fiber_v3_native_sqp.hpp"
    path.write_text(instrument(donor()))
    print(STAGE)


if __name__ == "__main__":
    main()
