# SCP attachment kernel provenance

## Tissue inflation closure (0.2.2 in progress)

`tissue/sources.json` records byte-exact ranges and SHA-256 hashes from the production
addon's muscle grid and Section Profile numerical headers. Reproduce with
`tools/capture_tissue_kernels.py ADDON_PATH`. Only the numerical closure is compiled;
legacy batch exports, resampling and OpenMP dispatch are excluded. Owned adapters
use the application's coordinator, cancellation token and immutable mesh resources.
`tests/fixtures/tissue/inflation.json` contains nine actual addon outputs for
Distributed, opposite orientation, disabled inflation, three control falloffs and
three Section Profile directions. `tools/capture_tissue_reference.py` regenerates
them without Blender. Compact grid comparisons pass at absolute 1e-12.

Standalone settings retain double precision. Reference Section Profile inputs are
first canonicalized by the donor's float32 property boundary before comparison.
Tissue base refinement operates on the accepted membrane, retaining original grid
lines and using native bilinear interpolation; it never mutates or reevaluates a
Manual source from newer authored curves. This is an explicit standalone extension.
Branches, two-sided composition, constrained smoothing, relaxation, crop and stacking
qualification remain in progress.

Prepared branch inflation now ports `prepared_inflation.py` and `branch_connector.py`
into native geodesic fields, per-part kernels, shared seam displacement and Hermite
assembly. Eight source-hashed donor cases in `tests/fixtures/tissue/branches.json`
match within 1e-10; regenerate using `capture_tissue_branches.py ADDON_PATH OUTPUT_PATH`.
Explicit accepted material axes retain nonuniform connector spacing. The standalone
accepted-grid refinement additionally inserts shared seam/interior samples, preserving
the accepted piecewise-bilinear surface and original lines without editing its curves.

`kernel_4.hpp` pins the production Static PBD closure from `af_soft_tissue.hpp`.
Native adapters now prepare source goals, named/custom masks, geodesic feathering,
exact backing and soft tethers; geometric point/sweep/shell work also runs natively.
`tests/fixtures/tissue/relaxation.json` retains actual addon results captured through
background Blender 5.0.1 and a second donor solve with double-precision source goals.
The latter isolates the kernel port from Blender `mathutils` float32 input rounding:
three static envelope cases match within 1e-10. Legacy-input differences are separately
bounded by 2e-5 metres (observed maximum about 1.05e-5); four geometric cases agree
within 2e-7. Regenerate with `capture_tissue_relaxation.py -- ADDON_PATH FIXTURE_DIR`.
This evidence does not qualify target-relative region bindings or all point relaxation.

Intentional contracts: explicit constraints remain enforced with relaxation None;
the addon bypassed them in that mode. Static relaxation reuses canonical triangulation
instead of retriangulating polygons. The addon's sweep cap winding is retained, and
generic solver adjacency uses undirected edge counts, as the donor does. Strict source
winding remains a normal-shell construction requirement. No additional volume or contact
guarantee is implied. Material fields store their domain/connectivity signature and fail
explicitly after incompatible sampling changes rather than silently reassigning weights.

`tissue_shape_fields.cpp`, `tissue_normal_shell.cpp` and `tissue_profile_sweep.cpp`
port the addon's Python numerical preparation into native owned buffers. Source hashes
and six actual outputs are in `tests/fixtures/tissue/shapes.json`; reproduce with
`capture_tissue_shapes.py ADDON_PATH OUTPUT_PATH`. Comparisons include canonical polygons
and vertices at absolute 1e-12. Default boundary distances, area-weighted normals, all-zero
custom fields, backing/rims, cyclic sweeps and zero endpoint taper are covered.
Sweeps consume the standalone curve engine's accepted frames (including authored tilt)
instead of recomputing the addon's global-axis fallback normals. Radial scale is relative
to the retained Anchor frame. Those placement contracts are intentional extensions.

`tissue/unit_spheres.hpp` contains the four finite Blender 5.0.1 bmesh unit icospheres
used by the addon at resolution thresholds 24/64/128. Regenerate via background Blender
and `tools/capture_tissue_spheres.py -- OUTPUT`; the companion JSON pins version/hash.
Runtime ellipsoid assembly is native and independent of Blender; rounded seed coordinates
are preserved. No authored geometry is baked or replaced by these unit templates.

attachment_wave_reference.hpp is an unchanged copy of the addon's
native/fiber_ccd/af_attachment_wave.hpp, captured 2026-10-16.
SHA-256: 5BAF4DD3681EE327BF184639EAA2A8386DA43228004BE55345988E6F17097750.

The standalone adapter reuses its surface frame and propagation mathematics.
Its process-global worker setting is fixed at one: the document scheduler owns
concurrency, avoiding competing OpenMP pools. Native cancellation occurs between
SCP operations. Blender capture is replaced with owned native mesh queries.

The original addon remains the parity reference and is not a runtime dependency.

## Bind-time owner transitions

`src/attachment_weights.cpp` ports the numerical work from the addon's
`core/vcp/fiber_node_attachment_weights.py`, captured 2026-10-18.
Source SHA-256: `fbc0a79439ace1f82b6b5ac7bbe9a280e682843a25bfe173bdc4a70f8e37b712`.
It preserves hard-pin span partitioning, arc-length owner runs, quintic transitions,
cyclic spans, duplicate-position handling and the one/two-influence thresholds.
Python only packs inputs and returned records. Eleven compact reference cases are in
`tests/fixtures/attachments/owner_weights.json`, reproducible with
`tools/capture_attachment_weights.py ADDON_PATH OUTPUT_PATH`.

Generic point capture/resolution now shares `attachment.cpp`'s existing surface capture
and the unchanged migration kernel's `af_surface_frame`. Batched input avoids synthetic
SCPs and per-point Python numerical queries. Bindings retain canonical triangle vertices,
barycentric coordinates and frame offsets; ordinary resolution never selects a new parent.

## Production routing kernel closure

`routing/upstream_sources.json` pins the original addon's numerical headers and the collision
portion of `af_fiber_ccd.cpp` by source hashes and exact line ranges. Reproduce with
`tools/capture_routing_kernels.py ADDON_PATH`. These reference files retain
the upstream formatting. Owned adapters in `src/routing*.cpp` follow the function limit.
Only this numerical closure is compiled: no addon Python, Blender objects or dependency
graph, muscle/skin code, public legacy ABI, or competing OpenMP pool. Kernel entry points
are private to the adapter. The application's existing coordinator owns work concurrency.

0.2.3 maintains a narrow extension to `af_fiber_v3_native_sqp.hpp`: per-job candidate
strategy/context, shared trust limiting, and iteration-cap consistency (never change
active membership after the last solved candidate). `routing/sources.json` records
maintained hashes, separately from originals. `routing_qp_problem.cpp` adapts the
benchmark's QP assembly and `routing_piqp.cpp` uses sparse PIQP 0.6.4. See CH-020.

Native adapters own surface snapshots, transforms, direct-reference allocation, open
hard-pin spans/global closed paths, production SQP settings, cancellation between trials,
path correspondence and output preparation. Planner preparation ports
`core/vcp/v2/planner.py` and its production session helpers, including sparse/dense/expanded,
pin-exit and warm recovery plus the separate handoff clearance check. A pinned 1050-node
pin-tree fixture checks its graph and thirteen paths; compact end-to-end cases remain
separate evidence. Warm continuation remapping ports `core/vcp/v3/warm.py`: each previous
authored span is arc-length resampled to the newly allocated pin interval, then pins are
restored exactly. Authored point identities, closure and binding parents gate compatibility.
Six donor-generated cases cover open/closed curves and 24/32/48 samples after anchor motion;
both remapping and resulting solves agree to absolute 1e-10.

`tests/fixtures/routing/addon.json` contains compact actual addon outputs and loaded-source
hashes. The four current cases cover clear open/closed paths and a cube detour/bound route.
They match the standalone numerical output to absolute 1e-10. Capture through
`tools/capture_routing_reference.py ADDON_PATH OUTPUT_PATH` without Blender/desktop input.

`tests/fixtures/routing/skull.json` additionally pins four evaluated SCP meshes from the
original `skull_muscles.blend` (9,158 vertices), explicit endpoint choices from four saved
fiber paths, nearest-parent choices and actual addon cold/warm solve outputs. Blender/file
and loaded-addon source hashes are included. Saved BAKE paths supply endpoints, not expected
solver output. These four cold/warm pairs match to absolute 1e-10. Extraction uses background
factory-startup Blender and does not save or modify the source. Reproduce with
`capture_skull_routing.py`, `skull_routing_qualification.py`, then
`capture_skull_routing_reference.py`. These fixtures establish those cases, not unrestricted
anatomical route correctness or complete release acceptance.

## Standalone routing contact and continuation corrections

The October 20 snapped-cube regression exposed inconsistent edge validation:
`routing_search.cpp` called the donor's owner-exempt surface test directly, bypassing
the standalone planner's solid-interior chord rejection. Search now calls the same
`clear` policy as shortcutting and anchor filtering. No donor kernel was changed.

`tests/fixtures/routing/snapped_cube.json` records the exact saved points, cube topology,
transform and source hash. Segment checks cover bound/unbound pins, three resolutions
and warm continuation. The donor's existing `bound-box` result also cuts its owner at
the first/last segments; its fixture remains unchanged as evidence of an intentional
correction. `test_snapped_routing.py` proves that reference intersects and the new result
does not. Other donor and skull numerical parity checks remain exact.

The `solver_test.anthroforge` regression is captured compactly in
`tests/fixtures/routing/surface_pins.json`, including its source hash and accepted warm
path. Unbound ordinary curve knots may touch explicitly selected surfaces. Native nearest
queries classify only contacts within the captured world's numerical floor, independently
of anatomical bindings; explicit owners remain authoritative. This extends the addon
adapter to the first-class curve contract without modifying its pinned numerical kernels.

Warm seeds crossing solid interiors are replanned. This check permits recoverable clearance
deficits and retains localized contact exemptions; the solver still enforces its clearance
policy. A warm solve reported infeasible receives one cold planning attempt. Existing addon
cold/warm fixtures remain unchanged and pass. The new user case additionally checks actual
intersections; numerical parity alone does not establish collision clearance.

## Accepted authored-fiber collision checks

`path_collisions.cpp` uses the pinned routing collision-world, segment-triangle distance and
closed-mesh containment kernels for read-only advisory checks. `routing_world.cpp` separates
collision capture from planner snapshot construction so advisory work does not allocate a
routing graph. Batches own transformed path samples and reuse one captured collision world;
cancellation is checked between samples, segments and surfaces. The numerical contact
tolerance is `max(1e-9, 1e-9 * world diagonal)` metres, with an eight-tolerance arclength
neighborhood at explicitly bound knots. This is not a clearance-radius calculation.
`tests/test_path_collisions.py` covers crossings between samples, containment, closing edges,
attachment contact, transforms and cancellation. Original pinned kernel provenance remains
in `routing/sources.json`.


## Two-sided tissue envelope composition

`tests/fixtures/tissue/envelopes.json` contains sixteen outputs of the addon's production
`_compose_closed_envelope_native`, with donor hashes and source cases. Reproduce with
`tools/capture_tissue_envelopes.py` in background Blender 5.0.1. Both boundary choices,
source flips, inactive sides and connectors match to 1e-10 with exact canonical faces.
The adapter preserves zero-side suppression of branch connector construction and the
donor's coincident-face compaction. Retained tissue material/side bindings must account
for that compaction; raw output vertex IDs cannot imply stable material identities.

## Constrained tissue height smoothing

`smoothing/` pins the addon's maintained native/smoothing core and height adapter unchanged;
`sources.json` records each source hash. `src/tissue_smoothing.cpp` owns batched native mesh
capture, canonical triangle/part selection, cancellation checks, result metadata and publication
buffers. Python sends settings and receives owned output plus per-part/side diagnostics.
The donor's cotangent biharmonic objective, PIQP settings and independent KKT/face checks remain.
Cancellation occurs before/after each part's synchronous QP; no mid-factorization cancellation
is claimed. Off bypasses the native call entirely. No extra worker pool or Blender runtime.
Seventeen cases captured from the actual addon DLL in `tests/fixtures/tissue/smoothing.json`
match to absolute 1e-10 with exact material topology. Source DLL/source hashes are in the fixture.
Reproduce using `tools/capture_tissue_smoothing.py` under background Blender 5.0.1.

## Tissue material-domain cropping

`src/tissue_crop*.cpp` ports the material-domain clip from `core/vcp/muscle_domain_clip.py`
to owned native meshes. Source coordinates decide plane membership; shared edge
intersections interpolate both material correspondence and output positions. Two-sided
outputs clip both full sides before envelope composition, preserving the donor's
triangulation and cut-edge height. Twenty background-Blender fixtures in
`tests/fixtures/tissue/crops.json` include source hashes and match at 1e-10. Reproduce
with `tools/capture_tissue_crops.py`. Empty results are prepared owned geometry, distinct
from incomplete buffers; attachment consumers reject empty surfaces explicitly.

The October 22 assembly qualification additionally ports the donor's dominant-plane
polygon projection, convex fan, concave ear clipping and nonplanar-quad fallback.
These material triangles are intentionally independent of display quad tessellation.
Wholly excluded polygons are rejected before triangulation. See CH-035 for the
adductor magnus fixture and the native nonplanar-quad regression.

Section Profile's adapter in `src/tissue_profile.cpp` retains the pinned profile
formula but rejects sub-threshold raw normals before normalization. Collapsed boundary
poles therefore contribute zero instead of amplified floating-point noise. Inflation
and stacking direction queries share this policy; positive-height degenerate interior
frames still fail. Pinned kernel bytes stay available for provenance and parity tests.

## Vector tissue stacking

`stacking/` pins the addon's production pair detection, base-ray ordering, relationship
policy, vector transport, localized constrained PIQP solve, and independent validation
headers. `upstream_sources.json` retains the original donor hashes; `sources.json`
records the current maintained files. `src/stacking*.cpp` supplies a
synchronous owned batch interface and uses the existing native cancellation token.
No donor asynchronous executor, legacy exported API, Blender object system, OpenMP pool,
or Python numerical implementation is included. The component uses one translation unit
because the maintained donor headers define non-inline cache methods.

October 22 compiler qualification (CH-045) replaces `order_pairs`' dangling
`std::minmax` references to temporary ID casts with the existing value-returning
`relationship_key` helper. Sorted IDs, policy/exclusion semantics and numerical
methods are unchanged. `sources.json` records the corrected bytes; original hashes
remain in `upstream_sources.json`.

Fourteen compact fixtures captured from the actual addon DLL cover ordinary and tangential
transport, chains, multiple providers, zero inflation, exact weighted constraints, hidden
crop variables, selected regions, explicit/requested/excluded relationships and deliberate
failures. `tests/fixtures/tissue/stacking.json` pins the DLL hash; reproduction uses
`tools/capture_tissue_stacking.py`. Positions match at absolute 2e-7; rejection status and
messages match. Cache reuse/cancellation pass separately. Native material preparation,
provider-first application scheduling, atomic opposite-side groups and desktop relationship
editing are now integrated. Workflow tests separately cover relaxed shells, exact backing,
source pins, regions, Manual providers, failure retention and cancellation. Donor parity
alone does not establish those integration contracts or anatomical correctness.

October 21 standalone changes (CH-018): ambiguous supports use the farthest distinct
positive geometric-base-normal hit. The new `vector_stacking/normal_support.hpp`
adapter calls the application's native BVH query; unambiguous vector transport and
exact constraints remain unchanged. Correspondence and solve cache keys were revised.
`layer_stacking/collision.hpp` permits crossings within a tissue; other-tissue and
bone validation remain. These are intentional product differences, not donor parity
claims. Original hashes remain available for auditing each changed header.

The October 21 intersection policy (computation history CH-016) permits tissue
self-intersections without changing raw solver parity. Native acceptance still rejects
nonfinite output and new collapsed faces. The separate diagnostic API compares canonical
connectivity for crossings, reports baseline crossings separately and permits large normal
rotations. This supersedes the earlier intrinsic rejection of crossed Pouch output;
it adds no self-contact resolution or automatic solver/preset substitution.
