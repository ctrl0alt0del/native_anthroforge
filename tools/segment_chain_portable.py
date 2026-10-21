"""Packaged parameter construction, target deformation and persisted editable stages."""

import json


def segment_chain(executable, cwd, invoke):
    invoke(executable, cwd, "--cli", "run", "examples/segment_chain.json")
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "segment-chain.anthroforge"))
    chain, plate = state["entities"]
    assert chain["primitive"]["kind"] == "SEGMENT_CHAIN"
    assert chain["primitive"]["chain"]["segments"][1]["bend"] == 0.5
    assert plate["deformers"][1]["shrinkwrap"]["surface"]["target"] == chain["id"]
    assert all(e["result"]["status"] == "ready" for e in state["entities"])
    render(executable, cwd, invoke, state["revision"])


def render(executable, cwd, invoke, revision):
    invoke(
        executable,
        cwd,
        "--cli",
        "render",
        "segment-chain.anthroforge",
        "segment-chain.png",
        "--revision",
        str(revision),
    )
