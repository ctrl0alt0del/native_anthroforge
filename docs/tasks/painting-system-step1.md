# Painting System — Step 1

- Task branch: `codex/painting-system-step1`
- Integration branch: `main`
- Starting revision: `713d963ecc5cad9aad939141acc140a73180324e`
- Status: complete; integrated into main and qualified for canonical delivery
- Active writer: local implementation session
- Last updated: 2026-10-30

## Delivered scope

Qt-independent, context-owned Painting System for tissue weights and SCP collagen.
Desktop, Python and JSON clients share begin/append/finish, read-only preview/explicit
commit, status, paged results and cancellation. Existing inspection/job-commit commands
remain compatible. The coordinator owns batching, workers, publication and finalization;
consumer adapters own effects and domain commits. Native numerical kernels are unchanged.

Schema 9 and package version 0.4.3 remain unchanged. This is a foundation increment,
not Muscle Paint, Paint Outer, envelopes, physical-width brushes or completion of 0.5.0.
See [design/API/evidence](../painting_system.md) and
[computation history](../computation_history.md).

## Qualification

- Full `tools/check.ps1` passed: Ruff, formatting, mypy (652 source files), native build,
  6 CTest checks, native style, PowerShell checks, **2,880 pytest cases**, numerical
  dependency checks and native doctor. The test suite took 404.24 seconds. Existing
  Qt deprecation/vendor warnings remain; no failures were hidden or skipped.
- Qt-free headless strokes, one-action undo/redo, no-op history, finish-before-preview,
  exact ready-candidate reuse, queued/running cancellation, supersession, failures,
  context isolation, pending-save publication and saved-state round trips pass.
- Desktop and authoring candidates match exactly. Mirror/workspace restrictions,
  frozen input settings, sample/page limits, stale baselines, camera metadata,
  previous preview retention, exported preview restoration and resource release pass.
- Serial old/new/new/old trials preserve every scalar array across 36 conditions on
  a 66,049-vertex dense SCP and the full 96-muscle assembly. Peak unique geometry
  ownership is unchanged. Small additional upfront baseline-check costs are documented;
  no speedup is claimed. Timings, variance and source hash are in the design evidence.
- A fresh temporary executable was relocated and passed **37 portable workflow groups**
  with minimal PATH and no development Python/Qt settings. The new shared painting
  sequence and legacy image exports pass alongside the existing complete workflow suite.
- Actual hidden GPU images were inspected for both consumers at two angles, cancellation,
  and packaged inspection export. No visible window or physical desktop input was used.
  This is offscreen/hidden-render evidence, not manual interactive acceptance.
- Documentation links and UTF-8 were checked. Functions satisfy the 15-line limit.

The installed 0.4.3 contained existing local assembly fixes. They remain uncommitted
in the original working branch and were preserved in the final executable/source archive.
The combined working tree passed Ruff, formatting, mypy and **2,885 pytest cases**
(421.65 seconds), and its rebuilt/relocated executable passed all **37 portable groups**
again. Packaged input files were checked against those local edits. No unrelated work
was silently reverted, staged into this feature or included in its remote commits.

## Defects caught during qualification

The initial save-admission helper assumed a live Session and broke captured formula
contexts. The final shared admission function supports both existing context contracts;
the complete regression suite passes. An isolated image-export restore adapter still
called the removed desktop retention method; it now uses the shared service/token and
has a regression. Legacy commit routes also enforce no merging into another gesture.
Profiler evidence exposed duplicate field validation, which was removed without dropping
geometry, field or occluder validation at capture/dispatch/publication.

## Ownership and coupling review

Reviewed separately from test success: immutable records belong to Core; context state,
read validation, cancellation and publication belong to Application; explicit consumer
composition owns tissue/collagen policy. Desktop captures input and presents leased
resources. No new numerical algorithm, dependency, worker pool, Qt timer, document-owned
paint session or accumulating stroke archive was added. Existing projection-cache budgets
and independent viewport leases remain in use.

## Recovery and delivery

Worktree: `E:/development/anthroforge/build/painting-system-step1`.
Painting runtime code: `88b2ce24`; later task commits contain qualification documentation only.
Main integration: `a3bf04e0`. Final runtime build: that revision plus the preserved local
assembly changes, honestly marked `tracked_changes: true` in its build identity.
Temporary package: `build/painting/package/AnthroForge.dist`.
Relocated qualification: `build/painting/relocated`; evidence: `build/painting/portable-final`.
Gate log: `build/painting/gate-final.log`; portable log: `build/painting/portable-final.log`.
Profiles/arrays: `build/painting/profiles` and `build/painting/final-serial`.
Combined checks: `build/painting/combined-gate.log` and `build/painting/portable-combined.log`.
Delivery hashes: `build/painting/delivery.json`.
These local-only artifacts are reproducible with the committed qualification tools and
the external production fixture identified in the design document; they are not in Git.

Delivery replaces the existing canonical `dist/0.4.3/AnthroForge.dist` and
`dist/AnthroForge-0.4.3-source.zip`; no additional release distribution name is created.
Primary checkout remains on its unfinished assembly branch with all unrelated changes
and the legacy root `__init__.py` preserved. Recovery copies/hashes of those 12 local files
are under `build/painting/integration-recovery`. Git ancestry establishes integration.
