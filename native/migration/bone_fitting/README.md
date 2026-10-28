# Maintained shortcut bone fitter

Pinned from the AnthroForge addon's `native/bone_fitting/native.cpp`; exact input hashes
are in `sources.json`. Dem Bones 1.2.1 headers and source license are retained in `vendor`.
Source: <https://github.com/electronicarts/dem-bones>.

The private adapter preserves Scale Aware independent-axis scale fitting, bounds 0.25–4,
Dem Bones initialization/weight updates, four influences, four OpenMP threads, and the
authoring-only Single Active TRS solver. Original iteration counts and tolerances remain.
The legacy whole-job deadline becomes coordinator cancellation; no additional worker pool
is created. The source's SLERP prediction is separate from actual channel-linear playback.
Parity and complete product integration are required before release.
