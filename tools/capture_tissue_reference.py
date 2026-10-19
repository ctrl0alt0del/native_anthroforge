"""Capture numerical addon inflation outputs without Blender or foreground windows."""

import importlib
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from capture_routing_reference import source_hashes

from anthroforge.core.tissue_settings import SectionProfile, TissueInflation


def grid():
    return np.array(
        [
            [(j * 0.03, i * 0.02, 0.01 * np.sin(j * 0.4) * np.cos(i * 0.3)) for j in range(11)]
            for i in range(7)
        ]
    )


def legacy_spec(s, reverse):
    value = dict(
        target_count=11,
        densify=False,
        closed_u=False,
        close_across_fibers=False,
        topology_flip_normals=False,
        closed_v=False,
        flip_normals=reverse,
        initialize_control=not s.control,
        control_world=s.control or (0, 0, 0),
    )
    value.update(inflation_values(s))
    return SimpleNamespace(**value)


def inflation_values(s):
    return dict(
        inflation_mode=s.mode,
        inflation_enabled=s.enabled,
        inflation_falloff_type="SMOOTHSTEP" if s.falloff == "SMOOTH" else s.falloff,
        inflation_max_value=s.amount,
        inflation_falloff_radius=s.falloff_radius,
        inflation_direction_depth=s.direction_depth,
        inflation_boundary_strength=s.boundary_strength,
        inflation_boundary_band=s.boundary_band,
        inflation_boundary_power=s.boundary_power,
        inflation_length_taper_band=s.length_taper,
    )


def case(name, settings, reverse=False):
    native = importlib.import_module("core.vcp.muscle_envelope_native")
    points = grid()
    if settings.mode == "SECTION_PROFILE":
        settings, p = canonical(settings)
        result = native.section(points, p, -1 if reverse else 1)
    else:
        result = native.legacy(points, legacy_spec(settings, reverse))
    return dict(
        name=name,
        settings=asdict(settings),
        reverse=reverse,
        points=points.tolist(),
        output=result.tolist(),
    )


def canonical(settings):
    module = importlib.import_module("core.vcp.muscle_section_profile")
    p = module.canonical_profile(SimpleNamespace(**asdict(settings.profile), version=1))
    return replace(settings, profile=SectionProfile(p.depths, p.peaks, p.roundness, p.direction)), p


def fixtures():
    base = TissueInflation(boundary_band=2, length_taper=0.3)
    rows = [
        case("distributed", base),
        case("reversed", base, True),
        case("disabled", replace(base, enabled=False)),
    ]
    return rows + control_fixtures(base) + section_fixtures(base)


def control_fixtures(base):
    control = replace(
        base,
        mode="CTRL_POINT",
        falloff_radius=0.15,
        direction_depth=0.07,
        control=(0.15, 0.06, 0.04),
    )
    return [
        case("control-" + f, replace(control, falloff=f)) for f in ("GAUSSIAN", "LINEAR", "SMOOTH")
    ]


def section_fixtures(base):
    rows = []
    for direction in ("LOCAL", "SMOOTH", "SECTION"):
        p = SectionProfile(
            depths=(0.01, 0.04, 0.025, 0.007),
            peaks=(0.3, 0.4, 0.6, 0.65),
            roundness=1.7,
            direction=direction,
        )
        rows.append(case("section-" + direction, replace(base, mode="SECTION_PROFILE", profile=p)))
    return rows


def run(addon, output):
    sys.path.insert(0, str(addon))
    rows = fixtures()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(sources=source_hashes(addon), cases=rows)
    output.write_text(json.dumps(payload, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps([r["name"] for r in rows]))


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]))
