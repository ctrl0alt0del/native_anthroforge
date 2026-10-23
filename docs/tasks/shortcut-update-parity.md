# Shortcut update parity: completed investigation

Status: **comparison completed; parity failed**. Diagnostic tooling only; no production
attachment, geometry, scheduling or UI behavior was changed. Source projects were
not overwritten. Branch: `codex/shortcut-update-parity`, runtime base `8b33df9`.

## Inputs and inventory

Standalone input:
`E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
SHA256: `308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`.

There was no single Blender project containing the same 96 authored muscles. The
migration inventory identifies 74 donor files. The scripts composed a separate
native addon assembly from their frozen migration packages, using the existing
addon import API and explicit identity mapping. All 74 original donor hashes still
match the migration inventory. The skeleton source is
`serratus_anterior_partial_v001.blend` (SHA256
`fb199c4f466cb06380e3596d7f83e715dd72abf71b154d703818d4df75832acd`).

Comparison copy and all analytical outputs:
`E:/development/WIP_models/shortcut_update_parity_20261023/`.
The new `matching_96_muscles.blend` SHA256 is
`78a817f8aa9f4f6688da2aa2508a16a948257d8a2033081b94aa8c7a3e1cdaf3`.

Both inventories match **59 SCP instances, 96 authored muscles, 326 Fibers**.
The SCP count includes 33 original records (one empty grouping SCP) and 26 opposite
side instances. All identities are asserted before comparing. Opposite-side bones
are reported separately: the addon has live symmetry, while the app intentionally
has independent counterparts. No mirrored muscles are included.

**Reference limitation:** the combined Blender import cannot resolve the two FDS
radial Fiber bindings; its radial muscle consequently has no generated mesh.
The combined pair therefore has 95 comparable tissue outputs and 324 Fiber paths,
not 96 valid muscle outputs. The original FDS donor was also tested independently
for all five states. Both FDS baseline muscle meshes match the app within 4.86e-7,
but the original radial bindings fail after Ribs/Humerus/Radius edits and retain old
geometry. Thumb does not trigger this failure. The missing combined output and
stale original outputs are recorded, never substituted with imported geometry.

## Method and units

Each edit starts from the saved baseline. Actual shortcut operations are used:
addon `set_shortcut_value`, app `driver.value` or `shortcut.set`. Captures wait for
the real background pipelines and record their completion/errors separately from
geometry. Background Blender draining forces due work; these runs are **not a
performance benchmark** or an interactive UI test.

Blender evaluated meshes and published Fiber paths are exported in world
coordinates. App accepted results use their authoritative geometry frames.
Coordinates are normalized to metres using the addon root unit contract when
available, otherwise Blender scene scale; app geometry is already canonical
metres. Here scene scale and app coordinate scale are both 1. The addon root has
**no declared physical-unit contract**: the comparison uses the saved scene scale,
without guessing anatomical scale or fitting/rescaling the shapes. Controls retain
their semantic units: object scales are dimensionless, Thumb thickness is a length.
The normalizer has a separate centimetres-to-metres known-answer test.

Metrics:

- Bidirectional sampled point-to-triangle distance: all vertices plus all triangle
  centroids, using native batched nearest-surface queries. This is not an exact
  continuous Hausdorff bound and does not compare vertex indices across meshes.
- Baseline-qualified material displacement: only with unchanged triangle connectivity,
  close baseline vertices (1e-5), and one-to-one correspondence. Otherwise unavailable.
- Fiber endpoint displacement, plus explicitly labelled indexed sample distances.
  Interior indexed distances are not asserted to establish material correspondence.
- Pose-aligned SCP geometry: uses the recorded frames, not a best-fit registration;
  only interpreted where baseline local geometry already matches within 1e-5.
- Cropped addon BASE outputs are not compared directly with uncropped app base stages.
  Centroid differences are diagnostic only when tessellation changes.

Pre-existing construction differences are measured separately. Baseline maximum
surface gaps include Spine .162996, Ribs .121684, Scapula .094586 and Femur .084071;
these are not newly introduced shortcut errors. Among the 95 comparable baseline
tissues, the largest surface gap is .00157560.

## Four independent edit results

Last three values are +5% from the app baseline, rounded once to Blender float32.
Both runtimes receive exactly the same requested number. Blender's Humerus transform
decomposition yields 3.1134085655212402 after the requested 3.1134088039398193;
this one-float-step difference is recorded and cannot explain the placement error.

| Shortcut | Requested value | Changed authored SCPs / tissues | Largest affected SCP surface gap | Largest affected tissue surface gap |
| --- | ---: | ---: | ---: | ---: |
| Ribs Top Radius | 3.0 | 14 / 62 | 1.114876, Acromion | 2.314392, Extensor pollicis longus |
| Humerus Length | 3.1134088039398193 | 9 / 35 | .148263, Ring | .219755, Third dorsal interosseous hand |
| Radius Length | 2.5114212036132812 | 8 / 28 | .000024105, Index | .289809, Third dorsal interosseous hand |
| Thumb Metacarpal Thickness | .07350002229213715 | 1 / 6 | .00628144, Thumb | .237296, Flexor pollicis brevis superficial |

Distances use the common unit convention above. These maxima are measured
world-space discrepancies, not claims that all discrepancy is a new app bug.
Counts exclude mirrors and the unavailable combined FDS output. All four app
runs finish without scheduler errors; this does not establish parity.

### Confirmed Humerus cause

The Humerus local deformed surface matches to 1.17e-14 after aligning the recorded
poses. Its world surface differs by .148260 and its baseline-qualified material
response differs by .148258, propagating through the arm.

The app marks transform-edited SCPs for attachment recapture in
`application/operations.py` and `application/evaluation.py::captures_for`.
The addon shortcut session instead includes the owner in `scp_apply_target_ids`
and sets `scp_recapture_ids=[]`. This source shortcut has no owner-backsolve or
attachment overrides enabled.

A read-only native counterfactual using the original Humerus binding reproduces
the addon pose with maximum matrix-component difference 1.81e-6. This isolates
owner recapture as the cause; it is not a missing Ulna update or inflation failure.
The probe does not save or publish its candidate into the source document.

### Radius: matching bones, stale addon Fibers, different crops

Radius/Ulna/hand bone results are close (largest gap 2.41e-5). However, the addon
leaves Anconeus Fibers at their baseline positions after Ulna moves. Explicit addon
VCP refresh reduces Anconeus 0.2 path distance from .09402235 to .00032895;
its endpoint *response* error then falls to 1.17e-6. The remaining path difference
is close to the original baseline difference. This is observed stale addon output.

Many larger tissue differences occur on cropped muscles. Approved computation
change CH-065 preserves the material cut as anatomy deforms; the addon still uses
the spatial plane. For example, Third dorsal interosseous hand keeps 1065 vertices
in the app while the addon changes from 1065 to 777, with final surface gap .289809.
This is an intentional contract difference, not evidence that inflation itself
has regressed. It does not explain every tissue discrepancy automatically.

### Thumb and Ribs: measured differences requiring separate diagnosis

Thumb local geometry matches to 2.40e-7 despite different Boolean tessellation
(401 versus 405 vertices). The app retains its original pose; the addon translates
it during the update, leaving .00628144 world surface discrepancy. Unlike Humerus,
the Thumb binding is **not recaptured**; retaining it again in a native probe does
not correct the difference. Do not generalize the Humerus cause to Thumb.
Some Thumb-attached Fibers and tissues differ substantially as well. The approved
exterior-following attachment behavior is relevant, but its contribution has not
been isolated sufficiently to attribute all those discrepancies to that policy.

Ribs produces substantial clavicle/acromion differences and downstream muscle
changes. Existing local constructions are different, so pose-only normalization
is not a valid isolating test for these bones. The exact contribution of shared
hooks, construction differences and attachment resolution remains unproven.

Recommended next diagnosis/fix sequence: shared shortcut owner-binding semantics
for Humerus first, then Thumb child-anchor/exterior resolution, then Ribs shared
controls and shoulder attachments. Establish separate expected behavior for the
approved crop and symmetry differences. This investigation does not change those
policies or implement fixes.

## Evidence and reproduction

Machine-readable local outputs:

- `summary.json`: counts, controls, worst affected objects and supplementary probes.
- `<case>-comparison.json`: every mapped SCP, tissue and Fiber, including unavailable
  outputs, statuses, sample counts and metrics; baseline plus four edit cases.
- `app/<case>/` and `blender/<case>/`: `state.json` and compressed world geometry.
- `<case>-fds-comparison.json`, `fds-donor/<case>/`: original donor comparison,
  explicitly separate from the combined assembly.
- `radius-refresh-comparison.json`, `owner-binding-counterfactual.json`,
  `SHORTCUT_21-owner-probe.json`: discriminating experiments.
- `provenance.json`: all donor hashes, source/project/native DLL hashes, Python
  version and addon revision/dirty state. Existing addon working changes are recorded
  and preserved; this is not claimed to be a pristine addon release checkout.
- `reopened-presentation.json`: saved-copy presentation audit with the saved UI loaded.

All scripts are in `tools/shortcut_parity_*.py`. The plan script consumes the previous
all-muscle migration run, the shortcut-migration folder, and an output folder. The
assembly script takes addon path, skeleton `.blend`, output folder. Existing source
packages and `plan.json` preserve exact identities, selection and shortcut mappings.
Blender scripts use Blender 5.0.1 with `-b --factory-startup --python-exit-code 1` and
`--python <script> -- <arguments>`. Capture arguments are addon path, output, case.
App capture arguments are output, case. Comparison arguments are output followed by
`baseline SHORTCUT_4 SHORTCUT_15 SHORTCUT_16 SHORTCUT_21`; summarize takes output.
Run app tools with `.venv/Scripts/python.exe` from the app repository. Local binary
assets remain outside Git; tooling and this result record are recoverable in Git.

## Validation and ownership review

- All 481 selected identities match in each primary capture; missing geometry is
  explicit. Original FDS evidence supplements, rather than hides, reference failures.
- Source standalone hash unchanged; all 74 donor hashes match the frozen inventory.
- Source-only VCP normalization preserves all 190 existing base/final mesh digests.
  Reopened copy has 324 visible normal-display Fiber proxies, zero mirrored VCP
  proxies, native SCP colors and Solid/Object color mode in all saved viewports.
- Native metric known-answer checks pass: reversal, translation, correspondence
  permutation, duplicate-correspondence rejection, topology-change refusal,
  endpoint displacement and unit conversion.
- All 13 task Python scripts pass Ruff lint/format and the 15-line AST function check.
  `git diff --check` passes. No production code changed, so no application rebuild,
  new portable package or repeat of the full application regression suite was needed.
- Ownership review: Blender adapters use the addon API, app adapters use shared
  commands, captures own serialized arrays, and analysis uses compiled geometry
  queries. No new production dependency, Python optimizer, or silent fallback.

The comparison is complete. **The two applications do not update identically.**
The measured defects/reference limitations above are not marked as fixed.
