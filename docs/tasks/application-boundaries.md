# Application ownership boundaries

Status: implementation in progress; not qualified or merged.

## Scope and recovery

- Request: fix the audited command catalogue, Session lifecycle and desktop Controller ownership problems. Preserve commands, guards, transactions, journals, previews, numerical results and UI workflows.
- Writer: Codex desktop, direct work. Branch `codex/application-boundaries`, integration `main`, starting revision `db492517eb84cddbb8d67eedfea9c012fc3e9aff`.
- Isolated checkout: `build/application-boundaries`. The primary checkout has unrelated assembly/mirror/resource edits and the legacy root `__init__.py`; preserve them. The installed package also contains those assembly fixes.
- No schema, numerical algorithm or package-version changes. All GUI validation stays background/offscreen.

## Observed causes and intended ownership

- `commands.py` centrally owns operation tables, prefix routing, repeated bound-lambda dictionaries and edit policy exceptions. Feature command declarations should supply variation; one executor should own shared guards, transactions and journals.
- Session/context lifecycle currently initializes and resets named feature services individually. Explicit registered lifecycle participants should own their cleanup while typed service access remains available.
- Desktop Controller mixes project, selection, camera, transform and panel responsibilities. Inspect callers before extracting cohesive view models; preserve Qt engine ownership and existing interactions.
- Related readiness and preview contracts will be checked for actual duplication; do not add speculative frameworks or a second scheduler.

## Delivery and evidence

1. Capture command/lifecycle contracts; migrate commands in feature families.
2. Integrate explicit context/session service lifecycle.
3. Extract desktop responsibilities and provide tooling-visible QML interfaces.
4. Run behavior, type/style, development gate, background GUI and portable checks; review ownership separately; integrate preserving unrelated changes.

Research: Qt's QML singleton/type registration documentation and model ownership guidance; Fowler's dependency injection discussion. Context properties are not inherently uncheckable in newer Qt: verify the actual toolchain rather than repeat that audit claim.

First checkpoint: immutable, explicit feature command declarations now cover 385 operations,
including profiler controls. Shared execution owns permission/variant checks, isolated-gesture
admission, implicit transactions, comparison recording and profiling. Project-wide scope is
declared by the feature. Removed superseded prefix routers and per-call bound-command tables.
Service methods resolve the active context at dispatch. No numerical behavior changed.

Evidence so far: 68 targeted registry, painting, skin, assembly, variant and query tests pass;
mypy passes across 670 modules. Full development/UI/package qualification remains pending.
Second increment: explicit context-owned lifecycle subscriptions now initialize services for
root/variant contexts and own gesture/history reactions, document notifications, synchronization
and teardown. Named typed accessors remain on Session; no service lookup registry is exposed.
Preview teardown cancels owned work and drops inspection/query leases. Skin-status subscriptions
survive ordinary project adoption. Cleanup attempts every registered close handler even if one
fails, and is idempotent.

Lifecycle evidence: 48 targeted tests pass, including existing painting, assembly, variant and
history cases plus per-context notifications, replacement and teardown-failure tests. Mypy
passes across 676 modules. A preliminary full pytest run is ongoing; final qualification is
still pending. Next: extract desktop view models and register tooling-visible per-engine QML
interfaces. This checkpoint is deliberately incomplete and remains off main.

Desktop checkpoint: project, selection, viewport, construction, mirror and runtime view models
own the extracted interaction/state responsibilities. QML uses the typed `AnthroForge.Desktop`
module and an explicitly bound per-engine `App`; no application context properties or shared
QML singleton instances remain. Existing feature panels retain their owners and behavior.

Evidence: main-window offscreen loading reports no QML warnings; 46 targeted desktop tests
passed before final ownership extraction, followed by 16 binding/interaction tests. A preliminary
full run passed 2,887 tests; two QuadWild checks failed because this worktree lacked the pinned
`.tools` bundle. Its junction is now restored; rerun remains required. Static metadata generation
works with the official Qt 6.12 registrar. The maintained API lint check deliberately probes an
invalid method and records all legacy/dynamic-state diagnostics separately; its complete run is
pending. Native build, full gate, hidden-render inspection and portable qualification remain pending.

Qualification checkpoint: all 185 QML files pass the registered-model API check (46 model
classes), including intentional invalid-method detection. The Windows gate now runs it.
Existing dynamic property maps and legacy QML style warnings remain reported, not silently
classified as typed coverage. Native CTest passes all six groups. Offscreen workbench and
shortcut-editor interactions pass; actual hidden GPU tissue/collagen painting and cancelled
previews were inspected. Foreground/manual interactive acceptance has not been performed.

Serial ABBA dispatch trials (`preferences.get`, seven batches of 10,000 per process) measured
baseline medians 15.77/16.07 us and candidate medians 2.78/2.68 us. Batch ranges were
15.27–17.47 us baseline and 2.63–2.81 us candidate. Native style checking was running in the
background; these figures establish only removal of dispatch overhead, not application or
geometry speedup. Each process also released 30 sessions with separate candidate contexts;
headless imports remained Qt-free. Reproducible tool: `application_boundary_qualification.py`.

Ownership review: feature declarations own variation, executor owns cross-cutting mechanics,
context participants own service cleanup, per-engine view models own desktop interaction.
Controller retains composition/staged publication. Existing readiness providers and generic
Preview transitions already own their contracts; no duplicate framework was introduced.
The unused clear-preview lifecycle event and redundant model signal forwarding were removed.
Issues repair synchronization remains before shortcut cleanup. Full gate and relocated package
checks are still running/pending; this is not yet a completed delivery.

The maintained authoring audit now consumes the registry directly rather than introspecting
removed dispatch tables. It reports 385 registered operations, 308 literal desktop calls and
zero missing registrations, including the extracted view-model directory.

The first complete gate reached 2,892 passes and three failures: two smoke-readiness test
fixtures still modeled Controller-owned pending projects, and SkinPanel dynamically looked up
the former `object_selection`. The production lookup now uses the explicit selection owner;
fixtures use ProjectView. All five targeted regression/engine-isolation checks pass. Search
found no other stale dynamic state lookups. Final complete-suite confirmation remains pending.

Primary-checkout integration for qualification: `codex/remaining-muscle-assembly` was
fast-forwarded to `8bc5cd8e` (main has not advanced). All 12 unrelated inputs were backed up
under `build/application-boundaries/build/integration-recovery`. Ten unchanged unrelated
files retain their original bytes; all local computation-history additions were verified.
The existing operation-aware mirror guard moved from the retired commands helper to
`command_execution.require`, passing `command.name`; that remains an unrelated local edit,
not part of this branch's commits. The temporary stash was verified/restored and removed.
Fourteen combined local assembly/mirror/registry regressions pass. A temporary combined package
is building under `build/application-boundaries/build/package`; installed files remain intact.

The combined temporary package completed. Its compilation report contains all seven new
view-model modules and neither retired dispatcher module. Packaging inspection found that
source staging retained deleted files from older builds; staging now replaces its owned
source subtree with a verified build-local path. A temporary-directory check confirms removed
files disappear and original sources stay intact. This packaging-tool change does not change
runtime code. Relocated qualification is running against the completed combined executable.
