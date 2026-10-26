# MC33 extraction subset

Pinned source: `https://github.com/computational-cell-analytics/bioimage-cpp`, commit
`492ff9b329cfa81af6781bc5b67b7c727eeb0445`. Source hashes are in `sources.json`.
Only marching-cubes headers and their small dependencies are included, unchanged.
MIT and derived scikit-image BSD-3-Clause notices are retained in `LICENSE`.

The addon uses scikit-image 0.25.2's compiled Lewiner extraction, not classic marching
cubes. This C++17 port was selected only after exact coordinate/connectivity comparison:
254 nonconstant binary cube cases, every ternary (-1/0/+1) cube with both signs, and
random volumes through the 33-cubed production tile size (6,344 initial comparisons).
The committed `tests/test_skin_meshing.py` reruns these case classes against scikit-image.
Both coordinate and triangle arrays match exactly, including zero-corner degeneracies.
This qualifies extraction only; assembled/smoothed envelopes need separate acceptance.

Authored adapters keep numerical work in C++, use bounded 33-cubed tiles, check
cancellation before/after each tile and do not enable the upstream profiler or threads.
