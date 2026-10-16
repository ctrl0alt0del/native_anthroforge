"""Qualify active Simple Solidify clamping and normal inversion against Blender."""

import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_primitive_parity import solidify_case  # noqa: E402


def cases():
    return [
        solidify_case(options(thickness, offset, even, angle, rim, flip))
        for thickness in (-4, 4)
        for offset in (-0.7, 0.6)
        for even, angle in ((False, False), (False, True), (True, True))
        for rim, flip in ((False, False), (True, True))
    ]


def options(thickness, offset, even, angle, rim, flip):
    return dict(
        thickness=thickness,
        offset=offset,
        even=even,
        clamp=1,
        angle_clamp=angle,
        high_quality_normals=even,
        rim=rim,
        flip=flip,
        invert=flip,
        minimum=0.2,
    )


def main():
    result = dict(blender=bpy.app.version_string, build=bpy.app.build_hash.decode(), cases=cases())
    Path(sys.argv[sys.argv.index("--") + 1]).write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(f"Captured {len(result['cases'])} clamping and normal fixtures")


if __name__ == "__main__":
    main()
