# Retained attachments during skeletal edits

- Task branch: `codex/retained-attachment-errors`; integration: `main`.
- Starting revision: `5f64e153b387f5c5e41b550b12109efbe7dcdd2a`.
- Status: implementation and qualification complete; ready for validated merge/push.
- Updated: 2026-10-23, Europe/Bucharest. Direct work; background-only validation.

## Outcome and acceptance

Investigate and fix the Humerus/Radius length and Thumb thickness attachment errors
in the migrated 96-muscle assembly. Establish the actual cause and explain the approach
to the user before changing attachment behavior. Preserve original project files,
retained binding intent, native numerical ownership and existing transaction semantics.

## Evidence and initial hypotheses

Migration qualification reproduced the same errors in both the original assembly and
the migrated copy. Humerus/Radius edits were +5%; the old Thumb helper added 0.05
to 0.07 (about +71%, incorrectly reported as +5%). A fresh actual +5% Thumb edit
reproduces the same seven failures; historical raw evidence is preserved. Humerus/Radius edits report missing tissue
material locations on FDS radial Fibers. Thumb thickness reports union-covered locations
on seven Fibers. Those error messages identify rejection sites, not proven physical loss
of a valid anchor. Diagnose active versus unused field influences, correspondence,
surface topology/provenance and dispatch/publication revisions before choosing a repair.

Native rejection sites: `material_binding_query.cpp`, `material_binding_frames.cpp`,
`triangle_material_frames.cpp`. Existing exterior placement policy qualifies new capture;
retained bindings must not silently choose a new nearest point during deformation.

## Recovery inputs

- Final copy: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
- Original copy, mappings and paired failures: same folder's `input.anthroforge`,
  `compact-mapping.json`, `failure-15.json`, `failure-16.json`, `failure-21.json`.
- Existing reproducer: `tools/probe_skeleton_control_failures.py`.
- Local diagnostic output: `build/retained-attachment-errors/` (ignored).
- Preserve unrelated root `__init__.py`; no desktop input or visible windows.

## Next actions

Regenerate the canonical source archive, then merge and push the validated branch. Runtime qualification below
uses `93a5872`; subsequent changes are inspection tooling and documentation only.

## Confirmed causes and approved correction

The FDS crop plane cuts away active attached material during Humerus/Radius changes.
Its base topology is unchanged. A failed endpoint changes signed distance from
+0.060001 to -0.081851. Using the original accepted crop base with the new inflated
rest resolves all 188 Humerus and 468 Radius failed material records without rebinding.
The user approved preserving the material cut; explicit crop edits define a new cut.
Accepted material state now retains `crop_base`; resource ownership and serialization
follow existing accepted-state contracts. Older accepted states use their own base.

Thumb source triangle rows are unchanged (all 708). Thickening actually buries the
proximal patches under the metacarpal. With an actual +5% edit, their signed exterior
distances change from positive to negative. The user approved following the same
object's exterior while retaining the original reference, including restoration.
Native Boolean provenance retains the untrimmed construction coordinates. Missing
material is projected to that union's exterior in construction coordinates and then
transported through the displayed triangle's deformation. Stored bindings stay intact;
no other object is eligible. Post-construction deformation must preserve this chart.

Evidence is in `build/retained-attachment-errors/`: `frozen-material-crop.json`,
`thumb-five-percent-coverage.json`, `true-five-percent-{15,16,21}.json`, and the
per-record diagnosis directories. `tools/diagnose_retained_attachments.py` is the
maintained read-only reproducer. Initial diagnosis and all approved runtime corrections
are complete; final evidence follows.

## Implementation checkpoint

Native exterior following is implemented with a persistent untrimmed construction
chart, layer-isolated spatial queries, and unchanged binding records. First combined
gate: 1,980 tests/five CTests pass, including native function limits. Real first edits
all complete without the original attachment errors. During history validation, the
profiler revealed a separate discarded Ulna pose job: formula invalidation cancelled
it while queued, then an unchanged formula result did not replace it. This is now
reproduced by `test_pose_formula_refresh.py` and corrected through the existing
renewable-job/restart contracts. Humerus edit/reverse now restores tissue vertices
within 1.8e-12, including through save/reopen. Final combined verification is below.

Final contract review also covered adaptive source sampling: keeping only old vertex
indices would reject a changed sample count. `tissue_crop_reference.cpp` now uses
the existing material-chart transport to sample the retained crop reference at current
material locations. A regression changes sampling and deforms the base; the cut follows
the original material boundary. Unsupported material topology/closure changes reject
with an explicit redefine-cut message. Eighteen focused material/pose tests pass.

## Final qualification

- Full Windows `tools/check.ps1`: **1,983 tests**, five native CTests, native style,
  function limits, Ruff, typing, PowerShell checks, numerics and Qt-free doctor pass.
  Log: `build/retained-attachment-gate-final.log`.
- `tools/qualify_retained_attachment_edits.py` exercises actual +5% edits of controls
  15/16/21 in the original 96-muscle assembly. All finish with ready SCPs and no failed
  jobs. Original Fiber binding records, attachment assets and support identities remain
  unchanged through edit, undo/redo, save/reopen and reversal. Maximum tissue vertex
  restoration error is approximately 1.8e-12 (Humerus), 6.4e-14 (Radius), and zero (Thumb).
  Individual measured edit waits were 2.85 s, 2.37 s, and 0.67 s respectively; these are
  single qualification runs, not controlled performance benchmarks.
- Inspected saved original/edited surfaces and paths from two angles for each case,
  generated by `tools/review_retained_attachment_shapes.py`. FDS cut/contours remain
  continuous and attached radial paths move with the tissue. Seven Thumb Fibers remain
  connected with the affected muscles after growth; no new spikes or disconnected
  shapes are visible. Images: `build/retained-attachment-errors/qualified/shapes-*.png`.
  The read-only capture tool owns copies of native buffers beyond resource lifetime.
- Canonical executable rebuilt at `dist/0.3.0/AnthroForge.dist`. Full minimal-PATH portable
  suite passes, including hidden QQuickRenderControl viewport pixels. Evidence:
  `build/retained-attachment-portable/portable-check.json`. No physical-window interaction
  or interactive dragging acceptance is claimed.
- `tools/check_retained_attachments_portable.py` also passes all three actual-assembly
  edits, undo/redo, save/reopen and retained-reference/readiness assertions in that
  executable. Each capture includes a profiler archive. The hidden desktop opens
  all 59 SCPs; its offscreen QML screenshot does not establish viewport rendering.
  A separate hidden native QQuickRenderControl capture displays the edited assembly
  and was inspected: `build/retained-attachment-errors/packaged/21/rendered.png`.
  Logs: `build/retained-attachment-real-portable.log` and
  `build/retained-attachment-render.log`.
- Source project SHA256 remains
  `308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`.
  Generated projects/reports/captures stay in ignored `build/retained-attachment-errors/`;
  they are local evidence, not cloud-accessible fixtures.

## Ownership and coupling review

The accepted material record owns the crop reference and existing resource traversal
retains it across documents, history, checkpoints and jobs. Native material charts own
resampling and union projection; neither UI nor Python carries numerical repair loops.
The shared material-frame resolver covers Anchor and Fiber callers without named-bone
exceptions. Existing exact visible-material resolution remains first; exterior following
is limited to the original object's original Boolean layer. The original material record
is never overwritten. Pose refresh reuses the single coordinator's renewal/restart
contracts, including temporary shortcut reads and output reservations.

Source topology/closure changes can still invalidate material correspondence and must
explicitly redefine the crop. Older union results without a construction chart load
unchanged; their next construction calculation supplies it. No blanket load-time
recalculation or new parenting/rebinding policy was introduced.
