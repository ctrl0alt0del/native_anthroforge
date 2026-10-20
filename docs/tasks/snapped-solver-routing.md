# Solver behavior on snapped curve and fiber

- Task branch: `codex/snapped-solver-routing`
- Integration branch: `main`
- Starting revision: `248cc66f62684c7218253335777aaf75f2e20949`
- Status: qualified and delivered; integration recorded in Git ancestry
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat

## Outcome and acceptance

Investigate the user's saved snapped curve/fiber, reproduce the expected surface route,
and correct any demonstrated runtime or editing defect at its owning boundary. Preserve
the original file and unrelated root `__init__.py`. Use background-only validation.

## Observed evidence and contracts

The supplied schema-4 project contains one unit cube, a two-point Curve, and its independently
bound Fiber copy. Both saved engine settings are BEZIER, resolution 24. Both accepted paths
are ready without routing diagnostics. This establishes that the saved objects have not
accepted routing conversion; it does not establish why the user's workflow left them so.

The user confirmed selecting ROUTED without Preview/Accept. The UI change now labels
the active engine, the conversion target and unapplied preview separately; its selector
synchronizes to the selected object's actual engine, including undo/redo and selection
changes. Background full-QML qualification on the original project passes.

Explicit conversion revealed a separate numerical defect on these exact inputs: no sampled
point is interior, but the first/last segments cross the cube near the pins. The independent
path collision checker reports segment 0. Native trace shows the planner initially accepts
the direct chord, its subdivided handoff fails, and SQP's owner-contact exemption permits
an invalid result. The cause was the graph search's separate edge checker: it bypassed
the planner's solid-interior owner-chord rejection. It now calls the existing shared
`clear` policy. No new solver, Python geometry loop or migrated kernel change is needed.

Rejected experiment: removing adjacent-edge expansion from owner_span made conversion
fail and changed four existing parity cases. Those changes were reverted. Do not treat
an increased iteration budget or a successful solver return as geometry acceptance.

Per specification_020.md and specification_021.md, snapping and anatomical binding do not
silently change the path engine. Conversion is explicit, previewed and undoable; a Fiber
preserves its copied engine. Check conversion on these exact coordinates before drawing
conclusions about native solver correctness or the UI.

## Verification and delivery

28 focused routing/architecture tests pass, including exact user pins, bound/unbound
contacts at 32/64/128 samples, warm continuation and independent whole-segment checks.
The original donor bound-box output fails that check; its corrected output passes.
This intentional geometry correction is documented in native/migration/README.md.
All other donor/skull cases remain numerically identical. Temporary diagnostics removed.

Full-QML `tools/snapped_routing_acceptance.py` passes on the original project, exercising
selection/preview without document edits, explicit application, curve/fiber independence,
undo/redo, selector synchronization and cancellation without QML warnings. Captures inspected;
this offscreen platform does not render the 3D scene. Separate hidden-GPU captures cover shape.

At runtime `64fe0ef`, `tools/check.ps1` passes: 1,294 pytest cases (732 existing Qt
deprecation warnings), three CTests, native function/style, Ruff/format, mypy, script
checks, numerical imports and native doctor. Existing solver/routing editor acceptance
tools also pass. Full portable qualification passes with minimal PATH and offscreen UI.

The clean packaged executable separately converts both original objects, saves revision
312, and reopens with ROUTED/ready results. Whole-segment checks return [-1] for both,
at tolerance 1.7320508075688772e-9. Its hidden-GPU capture was inspected. Original SHA-256
still matches the compact fixture. No visible windows, desktop input or hands-on
acceptance is claimed; frame times in capture screenshots are not performance evidence.

Installed the qualified package at `dist/0.2.2/AnthroForge.dist` after the user's running
application closed. No extra versioned distribution was created. Its executable hash is
`38cb503e260af33988317f0d9b32df3dba77f9ab67ab7c13cbbc3a9613ac29d6`;
native doctor passes from that final location. Corresponding source uses the existing
`dist/AnthroForge-0.2.2-source.zip` path. The separate user deliverable is
`E:/development/WIP_models/solver_doesnt_work_routed.anthroforge`.

Ownership review: the native graph search now invokes the already-established edge policy,
removing duplicate weaker logic. QML only presents active/target/preview states; shared
conversion transactions remain unchanged. No native fallback, new scheduler or silent
engine switch was added. Numerical failures remain failures. The original unsafe donor
fixture is retained as counterevidence, not rewritten to manufacture parity.

The final documentation checkpoint records qualification after the runtime build.
Follow the ordinary validated merge/push workflow; Git ancestry identifies integration.
Untracked root `__init__.py` remains unrelated and preserved.

## Recovery inputs

Original: `E:/development/WIP_models/solver_doesnt_work.anthroforge`.
Local-only evidence: `build/snapped-solver-routing`.
Relevant owners: `desktop/qml/CurveConversion.qml`, application conversion operations,
`application/routing_evaluation.py`, and `native/src/routing*.cpp`.
