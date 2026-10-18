"""Capture the addon's bind-time owner blending without loading Blender or touching scenes."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np


def load_reference(path):
    spec = importlib.util.spec_from_file_location("reference_attachment_weights", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def case(reference, name, points, owners, pins, closed=False):
    output = reference.attachment_owner_weights(points, owners, pins, closed)
    return dict(
        name=name, points=points, owners=owners, pins=pins, closed=closed, influences=output
    )


def regular_cases(reference):
    groups = ([0] * 5 + [1] * 6, [0, 1, 0, 2, 2, 1, 1, 0, 0, 0, 1], [0] * 11)
    points = np.column_stack((np.linspace(0, 1, 11), np.zeros((11, 2)))).tolist()
    return [
        case(reference, f"open-{index}-{pins}", points, owners, pins)
        for index, owners in enumerate(groups)
        for pins in ([0, 10], [0, 4, 10])
    ]


def cyclic_cases(reference):
    t = np.linspace(0, 2 * np.pi, 13, endpoint=False)
    points = np.column_stack((np.cos(t), np.sin(t), t * 0)).tolist()
    owners = [0] * 5 + [1] * 3 + [2] * 5
    return [
        case(reference, f"closed-{pins}", points, owners, pins, True)
        for pins in ([0], [4], [0, 5, 9])
    ]


def uneven_cases(reference):
    generator = np.random.default_rng(2761)
    points = np.cumsum(generator.uniform(-1, 1, (25, 3)), axis=0).tolist()
    owners = [0] * 7 + [1] * 3 + [2] * 5 + [0] * 10
    return [
        case(reference, "uneven", points, owners, [0, 6, 15, 24]),
        case(reference, "zero-span", [[0, 0, 0]] * 5, [0, 1, 1, 2, 2], [0, 4]),
    ]


def run(addon, output):
    path = addon / "core/vcp/fiber_node_attachment_weights.py"
    reference = load_reference(path)
    cases = regular_cases(reference) + cyclic_cases(reference) + uneven_cases(reference)
    provenance = dict(
        source="core/vcp/fiber_node_attachment_weights.py",
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dict(provenance=provenance, cases=cases), indent=2) + "\n")
    print(json.dumps(dict(cases=len(cases), **provenance)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("addon", type=Path)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    run(arguments.addon, arguments.output)
