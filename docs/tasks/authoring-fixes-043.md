# Authoring parity fixes — 0.4.3

- Branch: `codex/authoring-fixes-043`; integration: `main`.
- Baseline: `31e9138f`; writer: local direct work, no delegation.
- Status: implementation started; no qualification or release claim.

## Authorized outcome

Implement the confirmed [authoring contract](../authoring_043.md), closing audit A1–A4:
resolved editing queries, candidate images/numerical inspection, contextual queries,
and literal JSON arguments. Recovery/project-library and feedback services remain out
of scope. Preserve calculation algorithms, attachments, undo, schema 9 and source files.
Follow engineering guidelines and 15-line functions. Background/offscreen testing only.

## Sequence and recovery

1. Contracts and regression fixtures.
2. Shared component read model; desktop integration and paging.
3. Candidate adapters, capture lifetime, geometry paging and isolated scene rendering.
4. Domain choice/effective-state queries and desktop integration.
5. JSON Pointer literal paths; transport compatibility.
6. Full gate, production profiling, visual/offscreen and portable qualification; release.

Use `uv run --no-sync`. Native build:
`C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`.
Set `AF_NATIVE_BUILD` and `ANTHROFORGE_NATIVE_LIBRARY` consistently. Temporary outputs:
`build/authoring-fixes-043`; isolate preferences there. Preserve unrelated `__init__.py`.
Checkpoint/push coherent increments and validated merge under standing repository workflow.

## Acceptance

Paired UI/API controls and effective-state results; immutable preview geometry and images;
stale/cancel/release/export retry; JSON references/literals; unchanged geometry/bindings/
history; native resource release; 96-muscle profiling; full development and portable gates.
Deliver one `dist/0.4.3/AnthroForge.dist` and companion source archive only after qualification.

## Research

Existing shared helpers and native borrowed buffers are authoritative. Reviewed official
[Qt model/view](https://doc.qt.io/qt-6/model-view-programming.html) and
[RFC 6901](https://www.rfc-editor.org/info/rfc6901/) for adapter separation and pointer syntax.

Checkpoint: shared component buffers and `editing.inspect` now serve the desktop editor.
Moved-Fiber paired UI/API regression, immutable buffer ownership, bounded paging and
changed-revision rejection pass (31 targeted runtime tests; architecture and focused mypy
pass). Queries preserve authored data/history. No release qualification yet.

Remaining: broaden restriction/provenance coverage (junctions, driven controls, fields),
then implement candidate capture/render/export, contextual queries and JSON literals.
Full gate, production profiling and packaging remain pending.
