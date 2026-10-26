# Topology FLOW kernel

Maintained addon source, GPL-3.0-or-later; original fingerprint in sources.json.
The adapter namespaces the kernel, removes its standalone exports and adds cooperative
cancellation checkpoints. Numerical phase transport, robust weighting and iteration
counts remain unchanged. Native input validation and owned mesh leases live in the
standalone wrapper. Standalone qualification is recorded separately from source parity.

Guide capture joins accepted material charts in native code, preserving source-local
region provenance. Regional density retains the addon area initialization and eight
logarithmic smoothing/correction steps; hierarchy reservation remains metadata policy.
Source fingerprints are recorded alongside the original field kernel.

Skin proxy smoothing follows Blender 5.0.1 `MOD_smooth.cc` (GPL-2.0-or-later), with
all axes enabled and no vertex-group weights, as used by the addon skin pipeline.
It averages edge midpoints, uses Blender float arithmetic, and preserves the original
mesh through an owned result. Canonical edge iteration may change final float rounding;
four captured Blender fixtures qualify within 3e-7. This is not a replacement for
the still-pending decimation stage or a general-purpose smoothing modifier.

Ownership and conforming quad refinement are native ports of the fingerprinted addon
Python kernels. They retain sample/threshold policies, neighbor edge closure, split
patterns, parent provenance, two refinement passes and eight budget-search trials.
Original/reflected ownership samples remain instance-aware; source budget identities
are shared. Proximity uses accepted surface-tissue capability rather than a semantic
muscle/fat label. Bare Fiber sampling remains zero-radius. Deterministic ties and safe
rejection of malformed boundary graphs are intentional differences from incidental
Python iteration/exception behavior. Native result bundles own mesh and region/guide
labels until copied into the shared application resource lifecycle.

Proxy collapse adapts Blender 5.0.1 `bmesh_decimate_collapse.cc` and angle-normal
calculation (Blender Authors, GPL-2.0-or-later) to owned arrays. libigl's existing
MPL-2.0 topology traversal is serial; it does not introduce a worker pool. Blender
metric thresholds/boundary weighting/flip rejection are retained, but edge identity
and tie ordering differ. Qualification records surface errors rather than falsely
requiring identical connectivity. Compact captured Blender controls live in
`tests/fixtures/skin/proxy_decimation.json`; the comparison runner is
`tools/check_skin_decimation.py`. Broader MC33 evidence remains in ignored build data.

Closed-loop preparation ports addon `annuli.py` and `solver.py` rules to owned C++
arrays, reusing the maintained native graph route. Fixtures capture Blender's float
BVH output; native queries can select the other valid incident normal at a mesh edge.
Coordinate, pairing and incident-normal checks are separated. Run
`python -m tools.check_skin_loops tests/fixtures/skin/loops.json <report.json>` for
the maintained numerical comparison.

Annulus construction ports the same source's direct/planar/radial candidates, five
rings, 24–96 columns, inversion-based selection and reflection policies. Low-harmonic
periodic smoothing uses the equivalent bounded direct Fourier sum (at most 96 samples,
8 harmonics), rather than introducing another FFT runtime. SciPy 1.14.1's unchanged
BSD-3-Clause shortest-augmenting-path assignment kernel supplies ring symmetry matching;
see `native/vendor/scipy_lsap` for sources, hashes and license. It runs synchronously
on bounded <=96-column inputs inside the owning worker. All other repeated geometry
queries use the existing native surface and point indices.

`tests/fixtures/skin/annuli.json` records six direct addon controls exercising every
candidate. The planar stress fixture has deliberately reordered inner points; the
radial stress fixture has coincident rings. These isolate fallback behavior and are
not claims about ordinary anatomical guides. Run `python -m tools.check_skin_annuli`
with fixture/report paths. Whole anatomy and subsequent cut/stitch assembly remain
separate acceptance work.

Hole cutting and transitions port the fingerprinted `instant.py`, `cube.py` and
`solver.py` production calls. Shared ring projection/alignment and owned quad bundles
replace NumPy/SciPy/Blender numerical preparation. Compact captures live in
`tests/fixtures/skin/guide_cuts.json` and `stitch.json`; use the maintained background
capture/check tools. Their successful cases match source quads exactly. Boundary parity
and incorrect symmetry-side matches remain errors. Complete mesh assembly and wider
intersection-predicate equivalence still require qualification.

Complete assembly now has source-backed compact qualification in `assembly.json`:
side/centered/paired transitions, strict parity failure, explicit unstitched warning,
and disconnected closed components with mixed initial winding. Native welding retains
last-face region/guide provenance. `bmo_normals.cc` provides the outward seed and
manifold-neighbor orientation policy; its source fingerprint is in `sources.json`.
Annuli retain Blender float-coordinate materialization before cut/stitch: skipping
this boundary changed tied zipper ordering on symmetric rings. Numerical annulus
construction still uses double precision; only the accepted patch coordinates round.
These tests do not establish production anatomy or public workflow acceptance.

Symmetry uses owned triangle half cuts and the convex-planar subset of Blender beauty
triangulation, with source hashes under `half_mesh_reference`. Reflected output and
FLOW path clipping preserve the fingerprinted addon production policies. Seven small
fixtures in `symmetry.json` compare position and oriented connectivity. Duplicate
zero-area cut triangles on an exact-on-face plane are omitted intentionally. The addon
prototype `fill_unmatched_boundaries` is not part of the production call graph.
