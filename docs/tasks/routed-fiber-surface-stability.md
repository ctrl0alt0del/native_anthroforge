# Adaptive routed fibers and downstream material stability

- Task branch: `codex/routed-fiber-surface-stability`
- Integration branch: `main`
- Starting revision: `4be30b49e484957a62c548beffcb4d07f7a30021`
- Status: complete; canonical package and source qualified
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Verify adaptive routing through actual Fiber creation and retained anatomical bindings,
then through surfaces/Membranes and downstream attached construction. Exercise evaluated
sample growth and shrinkage, source movement, persistence and undo/redo. Preserve authored
controls, endpoint bindings, consumer material correspondence and topology restrictions.
Fix demonstrated defects at their owning boundary; do not weaken collision validation.

## Decisions and current state

After reviewing the requested comparison, the user confirmed “preserve exact corners.”
Production work now retains normalized surface stations and self-contained source material
coordinates on accepted tissue results. Shared attachment resolution transports each
binding location and frame through material charts, independently of sample indices.
Geometry payloads/native handles are not embedded in that metadata. Captured bindings
remain unchanged. Runtime `c30211d` replaces the rejected harmonic-disk candidate
`9427d13`; its full development gate and refreshed hidden-render checks pass.

Native compilation/three CTests and targeted tests now cover actual Base/Final Anchors,
downstream Fibers, saved captures, undo/redo, nonzero offsets with nonuniform transforms,
closed seams, branches and patches. Patch coordinates now use projected positions and
mean-value boundary transport; harmonic disk mapping was rejected for 0.1173 m drift on
unchanged geometry after adding one collinear sample. Rim queries now choose compatible
material planes at shared sheet/rim edges. Six new square/concave, edge/corner, shell,
resolution and rigid-transform checks pass, alongside routed consumer regressions.
Normal-shell/crop/envelope outputs retain owned source coordinate bases. Old metadata-free
captures and indexed authored weight fields keep explicit existing topology restrictions.

`tools/routed_material_acceptance.py` completed hidden Direct3D texture renders and a runtime
profile; all three images were visually inspected. Accepted route counts are 3/4/3 and
surface vertices 9/18/9. Both anchors return to their original locations with unchanged
records. The final local report recorded 30 native material-frame calls: mean 0.409 ms,
max 2.099 ms with profiling enabled; this small scene is not a general responsiveness
benchmark. The capture is complete, with no lost events and no unattributed geometry
bytes. Its observed peak is 8,818,848 geometry bytes; overlapping owner totals are not summed.

The first full pytest run had 1,358 passes and two donor parity failures caused by removal
of zero-width strips. Tests now preserve the source donor fixtures and explicitly verify
their canonical nondegenerate geometry. The final development gate passes 1,378 tests,
three native CTests, type/style/function/numerical checks and doctor. Additional targeted
checks cover target-region goals and source-handle disposal. The canonical package passes
the complete minimal-PATH portable suite and `tools/routed_material_portable.py`: reopened
exact projects shrink/grow to 9/18 surface vertices and 3/4 samples per routed Fiber.
All results are ready, captures are unchanged, and packaged hidden GPU images were inspected.
No visible-window, hands-on editing or physical input/display-latency acceptance is claimed.

Deliverables are the single `dist/0.2.2/AnthroForge.dist` and companion
`dist/AnthroForge-0.2.2-source.zip`. Packaged runtime is
`c30211d7b3102083e4d840649be5dcaed1764445`; executable SHA-256 is
`bdfc5adb250403cb36fe9d2c51dec1405bd09bd47860de6c7f9b40940d31dd40`.
Its native DLL exactly matches the qualified development DLL:
`0aec658faaf9c3f7322e3f4b47ab40b886a74037310c66d7309256ff0afd4cb4`.
The scientific native-patch view was also inspected. Extra collinear sampling plus a
resolution change produces at most `4.58e-16` m drift; a new boundary bend moves retained
locations with the patch. Data/image are local `patch-material.json`/`.png` in the build folder.

## Historical baseline and comparison (`18dfeba`)

The following results describe the pre-fix baseline.

Fibers use the corrected routing evaluator with resolved binding inputs. Actual two-endpoint
Fibers with preferred samples 3 grow 3 → 4 → 3 as an independent cube enters/leaves the path.
Their points, retained endpoint bindings and capture assets stay unchanged.

Default exact lofts union all evaluated path stations, which changes connectivity even
when path counts stay equal. Retained tissue Base bindings correctly reject old vertex
indices: `Anatomical surface topology changed; explicitly rebind.` The exact station
union also retains almost-identical floating-point stations, producing degenerate tissue
frames. `tools/experiments/routed_sampling/exact_limit.py` reproduces both observations.

The isolated C++ experiment compares:

1. Exact stations with a `1e-12` normalized-length merge and a material-coordinate probe
   at along/across 0.33/0.5. This preserves geometry corners; it is not an integrated
   Base/Final attachment implementation.
2. Fixed 32-station consumer sampling, matching actual application vertices to `1e-12` m.
   A second fixed-8 run checks sensitivity.

Both consume the very same accepted routed Fiber buffers. Three matched phases and
scientific figures are generated from those buffers, not illustrative geometry.

### Original comparison verification

The experiment's real uniform-surface tissue Base and Final Anchors retain their bindings
through grow/shrink, undo/redo and project reopening; no scheduler errors occur.
Both exact/fixed material probes return to their starting positions. The exact probe
only qualifies coordinate transport on this open loft, not frame/offset/role transport,
arbitrary branches, patches, fields, crops, or final production integration.

When the obstacle enters:

| Variant | Surface columns | Corner-to-boundary deviation | Full boundary-segment check |
| --- | ---: | ---: | --- |
| Exact prototype | 6 | 0 m | Both boundaries clear |
| Fixed 32 | 32 | 0.005983517833 m | Both cross obstacle at segment 10 |
| Fixed 8 | 8 | 0.024706827625 m | Both cross obstacle at segment 2 |

Deviation is not penetration depth. The boundary test does not establish whole-surface
collision safety. Before and after obstacle entry, all variants' boundaries are clear.
At that comparison revision, the production exact-consumer Base failure remained unrepaired.

16 routing/layout/workflow/architecture checks pass. Experiment Python style and function
limits pass; the isolated C++ helper compiles with the existing native toolchain. No
production C++ or Python files changed, so no new application build or full release gate
is claimed. Canonical executable SHA-256 remains
`20fadb07aec7d14fd2a71ae3b5994ec7bbece79c3b3e96ed6d2611906bb0090b`.
Official OMPL interpolation and Blender Surface Deform sources were consulted;
repository contracts and actual native results establish these findings.

## Completion

The approved exact-corner route is integrated through the shared material service.
No implementation or acceptance work remains. Indexed authored fields and old captures
without the required coordinates retain their explicit restrictions; this repair does
not guess correspondence or promise collision-free interiors for arbitrary lofts.

## Ownership review

Coordinator-authored review: surface construction owns exact stations and parameter charts;
native material queries own location/frame transport, cancellation and coverage validation.
The shared provider boundary serves all three attachment callers. Python only packs batches
and publishes results. Accepted meshes own plain coordinate buffers; native handles are not
serialized or retained in those buffers. Existing task scheduling, authored transactions,
history and revision reservations are unchanged. No competing worker pool or numerical
Python fallback was introduced. Canonical same-domain resolution is retained deliberately
for prior attachment semantics rather than duplicated in individual consumers.

## Recovery inputs

The compact `tests/fixtures/routing/solver_fail1.json` reproduces the prior failure.
Keep local evidence under ignored `build/routed-fiber-surface-stability/`.
Preserve unrelated root `__init__.py`; all validation stays background-only.
The maintained [experiment instructions](../../tools/experiments/routed_sampling/README.md)
recreate data and images. Local `compare/comparison.json`, `.npz` buffers, three saved
projects, `comparison.png`, `corner-closeup.png` and `timeline.png` are generated artifacts
and are not pushed. `exact-limit.log` retains the historical exact-mode rejection;
the maintained script now requires that same attachment to become ready.
