# Separate Draft initialization and topology budgets

- Task branch: `codex/skin-count-controls`
- Integration branch: `main`
- Starting revision: `1ed75b8b`
- Status: implementation in progress
- Last updated: November 27, 2026, Europe/Bucharest
- Active writer: desktop skin count controls chat

## Outcome and decisions

Move subtree quad budgets and FLOW controls into Topology, beside the document total.
Identify the nearest explicit ancestor/document budget and allow direct navigation to it.
Expose a saved AVBD-only initial root vertex target. The existing native
`sphere-isotropic` / `sphere-isotropic-features` interface accepts vertices (default 402),
not triangles or quads. It sets initial sampling density, not an exact count or a cap on
later SCP/VCP refinement. Keep default behavior, native algorithms and admission unchanged.

The qualified numerical runtime is an independently dirty checkout. Leave it untouched;
the application-owned adapter will specialize root seed orchestration and delegate all
later stages to the existing runtime. Capture this setting with the job and fingerprint
it in checkpoint prefixes. Preserve pending/applied settings, save/load and undo contracts.

Official API research: [Qt numeric input](https://doc.qt.io/qt-6/qml-qtquick-controls-spinbox.html).
Actual native target semantics were verified in `frame_instant_seed.hpp` in the qualified
runtime: target vertices determine an edge length, so achieved counts are approximate.

## Validation and next steps

Implement authoring, worker capture, checkpoint invalidation and UI separation. Test
defaults, invalid values, persistence/undo, builder isolation, ancestor budgets, changed
root count, later growth and checkpoint reuse. Run the development gate, inspect the UI,
build/qualify and promote the complete 0.4.3 package and matching source archive. Commit,
push and merge after validation. No tests or new build completed yet.

## Recovery inputs

Work in `C:/Users/alexe/.codex/worktrees/general-agent-instructions/anthroforge`.
Reuse `E:/development/anthroforge/.venv`, Qt SDK 6.12.0, native `build/skin-pipeline` and
the verified numerical image at `build/avbd-p8xfe46u/runtime`. Main checkout and
`E:/development/anthroforge/build/application-boundaries` contain unrelated edits.
Delivery: `E:/development/anthroforge/dist/0.4.3/AnthroForge.dist`.
