# Persistent variants, catalogue and reconstruction comparisons

- Branch: `codex/reconstruction-042`; integration: `main`; starting revision: `16f550b`.
- Status: implementation complete; final portable qualification in progress. Not merged.
- Updated: 2026-10-29, Europe/Bucharest. Direct local work; no subagents.
- Contract/walkthrough: [reconstruction_042.md](../reconstruction_042.md).
- Preserve unrelated root `__init__.py`; hidden/background testing only.

## Implemented

Schema9 with4–8 readers; immutable typed catalogue/review/stage/region/work records and
non-recursive variant snapshots. One Session/coordinator/executor serves explicit scoped
histories, services, reservations and callbacks. Normal tools edit alternatives with pinned
supports. Checkpoints fork; saves/autosaves project committed contexts; lifetime follows
document/history/jobs/views. Promotion/refresh reuse isolated evaluation, retained material
bindings, complete read checks, explicit conflicts and one Undo. Numerical algorithms unchanged.

Dockable Reconstruction panel has Variants/Catalogue/Regions/Stages/Reviews/Queue. Frozen
split/overlay comparison supports available accepted/variant/imported surfaces and paths,
shared camera, mesh sections, region selection and inspection export. Imports/evidence are
embedded; anatomical type ownership and independent review dimensions retain history.
Assembly copies applicable metadata and explicitly requested variants. Project-assembly
import belongs in accepted anatomy; scoped reference repair remains allowed.

Native batches compute region outlines and transformed cached bounds. Stage frame includes
geometry-origin offsets. Fiber-stage traversal excludes bone guides. Material regions check
construction source lineage as well as sampled domain; unrelated same-topology replacement
requires explicit redefinition. Canonical package remains0.4.2; no new anatomy algorithm.

## Evidence

- Full development gate built native and passed native/script style, then pytest reported
  2,755 passed with one stale 18-line qualification-tool violation. That function was fixed
  during the run; subsequent architecture and relevant regression suite:19passed.
  Latest context/lifecycle/architecture:11passed. Ruff/format/configured mypy624sources pass.
  Numerical dependency imports and doctor pass. Existing6native ctests passed.
- Source96-muscle assembly unchanged (SHA256
  308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac).
  SCM alternative inflation/promote/undo/save/reopen and Ribs Top Radius3 match accepted-only
  geometry and retained bindings exactly. Explicit support refresh1.660s; second promotion
  preparation1.003s/Apply.0072s. Initial create.105s/edit.346s/prepare1.152s/Apply.0067s.
  Peak about3.04GB initially,4.20GB with multiple retained snapshots. Single trials, no speedup claim.
- Twelve multi-angle hidden GPU comparisons inspected; matching transferred/final shapes,
  isolated fibers/base, reference/base and rest/final. No QML warnings/visible windows.
  Populated360px panels at400/700/960height and frozen inspection export also inspected.
  Qt-free export caller spawns existing hidden renderer. No interactive acceptance claimed.
- First portable run exposed Nuitka PEP695 type-variable NameError in ContextField.cast.
  ContextField/SchedulingField now use explicit Generic/TypeVar with scoped UP046 exclusions;
  source context/lifecycle checks pass. Rebuilt executable passed the complete relocated
  portable suite under minimal PATH, including reconstruction import/promotion/export.
- Portable project opening exposed a scene-cache epoch bug for controls. Scene and Issues
  projections now invalidate on change-journal identity, not only context name. Async-open
  regression and source smoke pass. Full pytest rerun:2,759passed; extra open regression5
  checks and profiler/context suite10checks pass. Profile boundaries now identify/enumerate
  jobs across contexts. Final package needs these final attribution/panel-smoke additions.
- Final panel check found Variants ListView collapsed inside the scroll container; added
  the same minimum height as the other pages and an actual row-count/height assertion.
  Populated hidden panels pass again. Source Reconstruction smoke passes with Windows
  fonts configured. The smoke CLI now accepts the reconstruction panel selector.

## Remaining delivery

1. Rebuild final package; repeat profiling/reconstruction/example checks and inspect panel.
2. Verify API docs/examples/links, final source archive and qualification status.
3. Check latest main, validate combined changes, checkpoint/push and merge/push normally.
   Do not claim completion until portable/runtime workflows pass.

## Paths and reproduction

Native: `C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`.
Set AF_NATIVE_BUILD and ANTHROFORGE_NATIVE_LIBRARY to its bin/af_native.dll for source checks.
Hidden GPU QQuickRenderControl requires normal Windows platform (no visible window);
setting QT_QPA_PLATFORM=offscreen prevents its GPU initialization. The portable harness
handles offscreen CLI versus hidden renderer platforms itself.

Production source:
`E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
Evidence: `build/reconstruction-042/{production,followup,production-views,gui}`.
Profiles: production/workflow.afprofile.zip and followup/followup.afprofile.zip.
Tools: reconstruction_qualification.py, reconstruction_followup.py,
check_reconstruction_042.py, check_reconstruction_production.py, reconstruction_portable.py.
Logs: development-gate.log, final-focused.log, package.log, portable.log.
Run `uv run --no-sync python tools/check_portable.py dist/0.4.2/AnthroForge.dist/AnthroForge.exe
build/reconstruction-042/portable --offscreen` after package finishes. Canonical archive:
`uv run --no-sync python tools/source_archive.py`.
