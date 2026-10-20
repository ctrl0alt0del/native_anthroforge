# Adaptive routed fibers and downstream material stability

- Task branch: `codex/routed-fiber-surface-stability`
- Integration branch: `main`
- Starting revision: `4be30b49e484957a62c548beffcb4d07f7a30021`
- Status: exact corners approved; shared material-frame implementation in progress
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
remain unchanged. Canonical package replacement remains pending.

Native compilation/three CTests and targeted tests now cover actual Base/Final Anchors,
downstream Fibers, saved captures, undo/redo, nonzero offsets with nonuniform transforms,
closed seams, branches and patches. Patch coordinates use native harmonic disk mapping;
normal-shell/crop/envelope outputs retain owned source coordinate bases. Old metadata-free
captures and indexed authored weight fields keep explicit existing topology restrictions.

`tools/routed_material_acceptance.py` completed hidden Direct3D texture renders and a runtime
profile; all three images were visually inspected. Accepted route counts are 3/4/3 and
surface vertices 9/18/9. Both anchors return to their original locations with unchanged
records. The local report recorded 30 native material-frame calls: mean 0.372 ms, max
3.365 ms with profiling enabled; this small scene is not a general responsiveness benchmark.

The first full pytest run had 1,358 passes and two donor parity failures caused by removal
of zero-width strips. Tests now preserve the source donor fixtures and explicitly verify
their canonical nondegenerate geometry. The full development gate is running; canonical
package replacement and final acceptance remain pending. No release acceptance is claimed.
The original experiment results below describe the pre-fix baseline.

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

## Verification

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
The production exact-consumer Base attachment failure remains reproduced, not repaired.

16 routing/layout/workflow/architecture checks pass. Experiment Python style and function
limits pass; the isolated C++ helper compiles with the existing native toolchain. No
production C++ or Python files changed, so no new application build or full release gate
is claimed. Canonical executable SHA-256 remains
`20fadb07aec7d14fd2a71ae3b5994ec7bbece79c3b3e96ed6d2611906bb0090b`.
Official OMPL interpolation and Blender Surface Deform sources were consulted;
repository contracts and actual native results establish these findings.

## Next actions

1. Complete remaining crop/target-region and resource qualification; review coupling.
2. Finish the full gate, rebuild/check the canonical package and verify latest native edits.
3. Qualify actual Fiber → Membrane → Tissue → attachment chains and package/merge only
   after the selected repair is complete.

## Recovery inputs

The compact `tests/fixtures/routing/solver_fail1.json` reproduces the prior failure.
Keep local evidence under ignored `build/routed-fiber-surface-stability/`.
Preserve unrelated root `__init__.py`; all validation stays background-only.
The maintained [experiment instructions](../../tools/experiments/routed_sampling/README.md)
recreate data and images. Local `compare/comparison.json`, `.npz` buffers, three saved
projects, `comparison.png`, `corner-closeup.png` and `timeline.png` are generated artifacts
and are not pushed. `exact-limit.log` contains the current exact-mode rejection.
