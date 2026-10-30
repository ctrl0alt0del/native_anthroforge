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
Next: integrate context-owned lifecycle subscriptions and typed service accessors, then extract
desktop responsibilities. This checkpoint is deliberately incomplete and remains off main.
