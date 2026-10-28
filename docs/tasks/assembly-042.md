# Cross-project anatomy assembly — 0.4.2

- Task branch: `codex/assembly-042`
- Integration branch: `main`
- Starting revision: `de1f475`
- Status: complete; qualified release merged and pushed to main
- Last updated: 2026-10-28, Europe/Bucharest
- Active writer: local Codex

## Outcome and contracts

Implement the confirmed [assembly contract](../assembly_042.md) through desktop and headless
operations. Independent editable copies preserve world placement, internal sharing, accepted
geometry, material bindings and inherited mirror behavior. Excluded transform parents require
mapping/inclusion/detachment; other external references are declared and repairable. Explicit
Rebind uses existing exterior/current-shape kernels. External formula writes stay disabled.
Schema 8 reads 4–7 and persists import provenance/reference evidence. Source skin, workspaces,
cameras, fitted solutions, history and active calculations are excluded. Keep the single 0.4.2
distribution and preserve unrelated root `__init__.py`.

## Implementation and ownership

- Core: immutable provenance/declarations, typed graph adapters and explicit identities.
- Application: pinned package snapshots, selective resources, graph closure, compatibility,
  rebind evidence, stale-read rejection, preparation, publication and source-free repair.
- Native: existing content comparison, transforms, material/exterior queries and capture.
  No numerical algorithm changes, Python numerical fallback or additional worker pool.
- Desktop: File import, searchable/virtualized lists, optional provenance suggestions,
  automatic preparation, stable footer, attachment evidence, Issues navigation and one undo.
- Existing construction/control copying shares the typed remapper. Result publication uses
  the normal transaction/coordinator contract and declares retained accepted outputs.
- Prepared immutable indexes are reused only for their matching destination snapshot.
  Unrelated changes use the ordinary merge; changed mapped targets reject stale publication.
- Terminal jobs release captures; import releases the source/preparation after transferring
  owned resources to document/history/display. Explicit garbage-collection tests verify this.

Separate ownership/coupling review is recorded in [the contract](../assembly_042.md#ownership-review).
Research reference: [OpenUSD relationship remapping](https://openusd.org/release/user_guides/namespace_editing.html).
No USD dependency or live project composition was introduced.

## Observed failures and corrections

1. Copied accepted formulas initially looked like new edits and changed clavicle geometry.
   Shared accepted-output adoption now preserves saved outputs without spurious reevaluation.
2. Selective loading omitted normal-reader legacy Fiber capture-frame restoration. That caused
   shortcut propagation differences. Both readers now reuse the same restoration.
3. Inherited mirror rule IDs were mistaken for copied bone IDs when the rule owner was excluded.
   Boundary mapping, external-output disabling and accepted read rewriting now distinguish them.
4. Origin-attached grouping roots incorrectly requested mesh evidence. They now use the existing
   native origin anchor. No dummy geometry or new attachment behavior was introduced.
5. Index reuse initially attempted to merge incomplete candidates. Blocking findings now remain
   editable in preparation; only ready candidates retain validated merged indexes.
6. Four old tests asserted schema 7 or rejected schema 8; assertions were updated for the
   approved format transition. Failed gate logs remain under the ignored evidence directory.
7. Final audit found accepted automatic stacking providers absent from the graph-copy reference
   contract. They now retain explicit final-surface evidence, including mirrored instances.
   Missing providers block planning/final output even during explicit evaluation. Changed
   providers invalidate stacking stages only; pending results use normal scheduler admission.
   Equivalent supports preserve accepted geometry. Regression checks cover repair without the
   source, schema persistence, Manual mode and mirrored targets. Inactive exclusions remain
   non-blocking. The repair UI preserves the explicit mirrored-target selection. No stacking
   kernel changed.

## Verification

- Final full gate: **2,690 passed**, `development-gate-final.log`, 472.94 s; 3,461 existing
  Qt/dependency deprecation warnings. Earlier failures and successful intermediate reruns remain
  recorded in the ignored evidence directory.
- Six native suites, native style, Python lint/format/type checks (568 modules), PowerShell
  parsing/function limits, numerical imports, native doctor and wheel resource checks pass.
- Assembly-specific tests cover missing/mapped supports, incompatible materials despite equal
  counts, partial explicit rebind, frame restoration, rule identity, ordinary parents, formulas,
  stale targets/unrelated edits, cancelled candidates, gesture boundaries, save/reopen, undo/redo,
  source deletion, reference removal and temporary resource release.
- The final combined gate covers the stacking-reference and UI corrections. Subsequent edits
  are documentation only. No native numerical implementation changed in this task.
- All **33 relocated portable checks pass** in `portable-release-final.log`, with minimal PATH,
  developer Python/Qt/native settings removed, Qt-free headless operations and hidden rendering.
  The canonical executable matches the tested copy; its build revision is `8762b4b`.

## Production and visual evidence

Immutable source:
`E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`

SHA256: `308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`.

The maintained [qualification tool](../../tools/assembly_qualification.py) copies the skeleton
and all 96 tissues in separate operations with explicit bone mapping. It compares **492**
geometry-bearing records before and after Ribs Top Radius→3, Humerus Length, Radius Length and
Thumb Radius edits. The final `qualification-stacking-final.log` rerun has no differences/errors
in all five comparisons. Compare poses/world coordinates, path samples, every tissue stage,
canonical oriented triangles and normalized binding records. Tolerance is 1e-8 m. Raw Boolean
face enumeration is nondeterministic for Thumb; canonical orientation/connectivity is retained.
This is source-standalone/import parity, not a new Blender parity claim.

Matched front/oblique hidden GPU renders show 1,184,586 displayed vertices; the anatomy pixels
match exactly (viewport rows 90–889 exclude dynamic timing text). The 625-object import dialog
was inspected offscreen with readable lists and no QML warnings. Initial blank render probes
mixed the development viewport DLL with a different native geometry DLL; using one matched
qualified native directory corrected the probe. No source project was changed. A separate
GUI probe had a teardown-only signal traceback after capture; this was not an interaction test.
These checks do not establish physical desktop interaction acceptance.

## Performance evidence and limits

Recorded 281 MB / 625-object inventory takes about 2.2 s. All-muscle preparation takes about
22 s on existing workers. cProfile identified 0.717 s of redundant document/index rebuilding;
prepared-index reuse reduced one matched Import command from **0.936 s to 0.184 s**. Adoption
was 0.070 s, source snapshot disposal 0.109 s. These include profiler overhead and do not
establish an unprofiled 100 ms latency guarantee. Import plus service waiting was about 0.83 s
in the corresponding run. Source/imported shortcut times are not an overhead comparison:
only the destination was recorded. Final rerun also overlaps packaging, so its timings are
qualification observations rather than isolated performance trials.

Raw local-only artifacts: `build/assembly-042/production/`, `visuals/`, `assembly-dialog.png`,
`import-cost/`, `qualification*.log`, `pytest*.log`, `development-gate.log`, `package*.log`.
The `.afprofile.zip` records preparation, native calls, publication and retained resource data.
See [computation history](../computation_history.md) for the preserved algorithm contracts.

The final runtime report retains all 104,747 events without truncation or declared collector
loss. It records native/cache/invalidation/resource boundaries; as a headless capture it has
no Qt frame/input/binding evidence. Final all-muscle preparation was 13.90 s and import plus
wait 0.671 s. Native-style checks and packaging overlapped, so these remain observations, not
a controlled performance comparison. The packaged construction-only screenshot shows both
curves and its embedded reference image after import/undo/redo/save/reopen.

## Delivery

Merged and pushed to `main` in `f92ea5d`, preserving checkpoint history. Integration main
remained `de1f475` throughout qualification, so the merged code is the validated tree.
The canonical release is `dist/0.4.2/AnthroForge.dist/AnthroForge.exe`, with the single companion
`dist/AnthroForge-0.4.2-source.zip`. Packaged build revision `8762b4b` identifies the final runtime
code; later commits contain qualification documentation only. Relative documentation links
pass. The unrelated root `__init__.py` remains untouched and untracked.

Qualified native runtime: `C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`.
All temporary qualification outputs belong under ignored build directories, not WIP_models.
