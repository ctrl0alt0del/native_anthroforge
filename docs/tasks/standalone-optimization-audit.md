# Standalone optimization audit

- Branch: codex/standalone-optimization-audit
- Integration: main
- Starting revision: 966ae1224a11c8c6a2948be7be58525998e84529 (0.1.5)
- Status: analysis and validation complete; ready for normal integration
- Completed: 2026-10-18, Europe/Bucharest
- Writer: desktop analysis chat; no delegation

## Scope

Review the migrated application for remaining addon constraints and opportunities
enabled by owning document, evaluation, scheduling and rendering. Inspect both the
current code and migration provenance. Use existing runtime captures and bounded
experiments to distinguish measured bottlenecks from scaling risks and hypotheses.
No production behavior changes or new release are authorized by this analysis task.

## Measured findings

Activity's 0.1.5 fix is present. Mesh BVHs, native batch picking, immutable snapshots,
revision guards and staged rendering already exist; do not recommend adding them again.
The existing 0.1.5 Ctrl-drag/open-Activity capture has 80 Controller.refresh spans
averaging 20.55 ms inclusive while recording. It still rebuilds the entire scene
projection and broadcasts selectionChanged; authoring state serializes complete
definitions and replaces curve-choice models. Hidden ControlInspector bindings also
execute. These overlapping recorded durations must not be summed or treated as
unrecorded input latency. The previous unrecorded confirmation is 12.19-14.17 ms.

New unrecorded synthetic star-hierarchy measurements (nine repeats, one Body and
remaining empty groups, no GUI or worker dispatch):

| SCPs | Revision-only document replacement | Dependency graph | Scene projection | Live point-edit admission |
| ---: | ---: | ---: | ---: | ---: |
| 16 | 0.021 ms | 0.026 ms | 0.364 ms | 0.374 ms |
| 64 | 0.157 ms | 0.201 ms | 1.521 ms | 1.169 ms |
| 256 | 1.443 ms | 1.322 ms | 7.390 ms | 7.312 ms |
| 1024 | 19.666 ms | 13.152 ms | 50.532 ms | 86.845 ms |

A separately instrumented 512-SCP edit rebuilds the dependency graph three times
and validates the document twice before dispatch. Document.entity is linear;
descendants and native.attachments.ordered repeatedly scan the entire hierarchy.

The current Body path finalizes five native meshes per reevaluation with an accepted
previous mesh: base, base deformation, bending, curve-frame transform, topology reuse.
Each builds bounds, BVH and render chunks. A diagnostic-only, cached-base experiment
for one open capsule with identity curve frame and no deformers/thickness takes
0.43-0.57 ms versus 2.22-2.38 ms (482 vertices), 5.08-5.26 ms versus 26.39-28.40 ms
(4,034 vertices), and 27.33-27.80 ms versus 137.42-138.13 ms (16,258 vertices).
Serial ABBA, 12 evaluations per leg; all five canonical arrays, counts, bounds and
one picking ray match at eight edited positions per size (24 total, tolerance 1e-12).
This validates an opportunity, not a general replacement or full-app speedup.

Coordinator.jobs is append-only. Tick and invalidation scan terminal history too;
terminal jobs retain snapshots. In artificial completed-job histories, the latest
25-repeat run has idle tick medians 0.001/0.213/4.916/32.533 ms at
0/1,000/10,000/50,000 records. This is a scaling stress case, not a real-session soak.
The Activity model's 40-row limit does not bound coordinator retention.

## Recommended order and ownership

1. **Incremental desktop presentation.** [Controller.refresh](../../src/anthroforge/desktop/controller.py)
   rebuilds all scene records and emits selectionChanged on each document revision.
   [Authoring state](../../src/anthroforge/desktop/authoring_state.py) converts the whole
   selected SCP to dictionaries, then converts curves/bindings again. The curve combo
   reports 80 model replacements during 80 point edits even though curve identities
   do not change. Give desktop projections stable row identities and narrow change
   notifications; cache hierarchy choices and visual layers by their actual inputs.
   Application mutations should supply affected IDs/fields for all clients. Preserve
   immediate numeric feedback, component selection, focus, workspace rules and the
   displayed geometry/picking revision. Validate the cube/Body interaction with
   inspectors visible/hidden, ordinary/Ctrl movement, long curves and many SCPs.

2. **Indexed immutable document and dependency structure.**
   [Document](../../src/anthroforge/core/document.py), [tree validation](../../src/anthroforge/core/entities.py)
   and [dependencies](../../src/anthroforge/application/dependencies.py) own this cost.
   Reuse ID/children indexes and forward/reverse port dependencies when structural
   inputs are unchanged. Separate structural validation from validating edited values;
   keep full validation at load/import and structural mutations. Do not remove
   immutable snapshots or validity checks. Structural inputs include attachment modes,
   enabled state and control references, not just the parent tree. Reuse immutable
   indexes safely across history and workers; keep derived indexes out of the project
   format. Validate constant-size edits across growing documents, real cycles versus
   pose-following, Manual prerequisites, hierarchy edits, undo and publication guards.

3. **Native evaluation buffers with deliberate finalization.**
   [Body evaluation](../../src/anthroforge/application/construction_evaluator.py) composes
   fully finalized mesh operations; [mesh rebuilding](../../native/src/mesh_build.cpp)
   constructs spatial and display products each time. Let native construction stages
   share canonical topology and operate on worker-owned vertex buffers; prepare BVHs,
   normals and render chunks when an output actually requires them. Cache immutable
   base geometry by all construction inputs. Reuse previous canonical connectivity
   before finalization, instead of rebuilding once more in
   [topology preservation](../../native/src/mesh_topology.cpp). The diagnostic shortcut
   is not the production design: generalize the boundary across bodies, lofts and
   ordered deformers. Required validation includes Blender parity, mixed deformers,
   closed curves, transforms, attachments, cancellation, ownership and visual results.
   The measured 4-5x gain applies only to the limited capsule evaluation experiment.

4. **Separate active execution from historical job records.** The existing
   [coordinator](../../src/anthroforge/application/coordinator.py) should remain the sole
   lifecycle owner. Maintain active/runnable indexes by ID, coalescing key and affected
   outputs/ports; keep compact history/retry/restart records separately. Release terminal
   execution payloads when no owner needs them. Preserve cancellation, bounded delay,
   reservations, earliest-running save checkpoints and undo/redo restart semantics.
   Do not cap all history at the Activity panel's 40 rows. Prove tick/admission costs
   depend on active work in a real long-session soak. Terminal snapshots currently
   retain authored state; this audit does not establish a native mesh leak.

These are responsibilities within the existing stack, not a recommendation to replace
Qt/Python/C++ or add a general-purpose framework. The Activity optimization demonstrates
incremental presentation already works here; scene/authoring projections have different
owners and must preserve their own geometry leases and selection contracts.

## Lower-priority hypotheses and capabilities already present

- [Attachment capture](../../native/src/attachment.cpp) creates a transformed
  [Surface/BVH](../../native/src/spatial.cpp) for each capture. Batch captures against
  an unchanged parent could share that world-space structure by mesh revision/transform.
  This has not been benchmarked; measure a many-child capture fixture first. A naive
  local-space nearest query is incorrect under nonuniform scale.
- Native scene picking already batches queries and uses cached per-mesh BVHs.
  It still loops over all eligible meshes. A scene-level acceleration structure is
  a hypothesis for many-object scenes; current captured af_scene_pick averages
  0.048 ms, so this is not the demonstrated small-scene drag bottleneck.
- Geometry collection scans retained documents/history and worker-input preparation
  copies the asset-handle map. Profile large histories before choosing reference-counted
  asset reachability or smaller dependency-specific payloads. Array views themselves
  are already zero-copy; immutable geometry and staged viewport leases already exist.
- No GPU execution timing or large-file I/O benchmark establishes a renderer rewrite,
  new file format, GPU solver or extra worker threads as a priority.

The addon already has native batch kernels, owned captures, revisions and caches.
Inspection of core/scp_runtime/depsgraph_state.py and attachment_wave_capture.py found
Blender evaluated-object/fingerprint capture and RNA lifetime handling that standalone
already avoids. The current whole-state scans and eager mesh finalization are primarily
standalone architectural opportunities; they should not all be described as copied
Blender limitations. Keep the qualified migrated attachment/Hook/Lattice/curve algorithms
and optimize their surrounding data flow before replacing numerical behavior.

## Evidence, reproduction and validation

[Machine-readable evidence](standalone-optimization-audit-evidence.json) includes raw
timing samples, source hashes, capture build identity, native call counts and limitations.
Raw ZIPs and pstats remain local. No production code or version changed. Tools contain
read-only diagnostic paths; the cached Body experiment is deliberately restricted.

Run serially from the configured standalone checkout:

```powershell
uv run --no-sync python tools/standalone_audit.py build/standalone-audit
uv run --no-sync python tools/standalone_geometry_audit.py build/standalone-audit
```

Both experiments ran successfully. tools/check.ps1 passed: 421 pytest tests, lint,
formatting, mypy, native build/CTest/style, PowerShell style, numerical checks and
native doctor. Final evidence and ownership review are complete. The two diagnostic
scripts do not enter production dispatch, UI, serialization or numerical paths.
No new GUI or portable build is needed because production behavior is unchanged. The
limited geometry comparison is not acceptance for a future optimized implementation.

Official references support the design options, not the measured AnthroForge gains:
[Qt performance guidance](https://doc.qt.io/qt-6.12/qtquick-performance.html),
[Blender dependency graph](https://developer.blender.org/docs/features/core/depsgraph/),
[libigl AABB queries](https://libigl.github.io/tutorial/).

Keep raw captures/experiments in ignored build/standalone-audit. Preserve the unrelated
untracked root __init__.py. Final findings should state ownership, unchanged semantics,
evidence limits and discriminating acceptance for each proposed change.
