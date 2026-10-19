"""Pin actual addon prepared inflation, welded seams and Hermite connector results."""

import hashlib
import importlib
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
from capture_branch_reference import paths
from capture_tissue_reference import legacy_spec

from anthroforge.core.tissue_settings import TissueInflation


def material(assembly, module):
    main = assembly.main
    grids = [np.arange(main.size // 3).reshape(main.shape[:2])]
    count = main.size // 3
    for branch in assembly.branches:
        mapping, additional = module._branch_map(main, branch.grid, branch, count)
        grids.append(mapping.reshape(branch.grid.shape[:2]))
        count += len(additional)
    records = [v for g in grids for v in (*g.shape, 0, 0, g.size, *g.ravel().tolist())]
    axes = [*np.linspace(0, 1, len(main)), *assembly.along]
    for branch in assembly.branches:
        axes.extend([*branch.across, *branch.along])
    return records, axes


def case(boundary, flip, control, fullness):
    module = importlib.import_module("core.vcp.branched_surface")
    inflate = importlib.import_module("core.vcp.prepared_inflation")
    spec_type = importlib.import_module("core.vcp.muscle_numeric").MuscleNumericSpec
    main, children = paths(boundary, True)
    branch = module.BranchInput("branch", boundary, (1, 2), tuple(children), 0.3, fullness)
    assembly = module.prepare_assembly(main, (branch,), flip)
    settings = settings_for(control)
    specs = tuple(spec_type(**vars(legacy_spec(s, False))) for s in settings)
    front, sides = inflate.inflate_assembly(assembly, specs)
    base, faces = module.assemble(assembly)
    output, _ = module.assemble(assembly, front, sides)
    return record(module, assembly, settings, base, faces, output, control, fullness)


def settings_for(control):
    first = TissueInflation(amount=0.07, boundary_band=3, length_taper=0.3)
    second = replace(first, amount=0.11)
    if control:
        second = replace(
            second,
            mode="CTRL_POINT",
            control=(0.4, -0.2, 0.2),
            direction_depth=0.2,
            falloff_radius=0.8,
        )
    return first, second


def record(module, assembly, settings, base, faces, output, control, fullness):
    records, axes = material(assembly, module)
    return dict(
        name=f"side{assembly.branches[0].connection.boundary}_flip{assembly.flip}_control{control}_full{fullness}",
        settings=[asdict(s) for s in settings],
        points=base.tolist(),
        faces=faces.tolist(),
        material=records,
        axes=axes,
        connectors=[0.25, 0, 0.3, fullness],
        output=output.tolist(),
    )


def main(addon, output):
    sys.path.insert(0, str(addon))
    names = ("branched_surface", "prepared_inflation", "branch_connector")
    sources = {
        name: hashlib.sha256((addon / f"core/vcp/{name}.py").read_bytes()).hexdigest()
        for name in names
    }
    rows = [
        case(side, flip, control, full)
        for side in (0, -1)
        for flip in (False, True)
        for control, full in ((False, 0), (True, 0.025))
    ]
    output.write_text(json.dumps(dict(sources=sources, cases=rows), allow_nan=False) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
