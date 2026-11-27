# Separate Draft initialization and topology budgets

- Task branch: `codex/skin-count-controls`
- Integration branch: `main`
- Starting revision: `1ed75b8b`
- Status: source, package and normal-launch acceptance passed; full regression gate and delivery pending
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

Authoring, worker capture, checkpoint invalidation and UI separation are implemented.
Focused tests cover defaults, invalid values, persistence/undo, builder isolation, ancestor
budgets, applied-versus-pending capture, checkpoint invalidation and later-route delegation.
The initial 33 focused tests passed; after the clearance retry correction, the affected
25-test group and mypy passed. Ruff/format checks passed. Functions remain within 15 lines.

Real source numerical acceptance: default 402 reproduced the old cube connectivity exactly
and coordinates within 1e-10. Targets 402/602/802 yielded 468/777/1,024 vertices respectively.
At target 802, adding a VCP grew 1,024 vertices / 2,044 triangles to 1,229 / 2,454. Therefore
the target is approximate and is not a cap on later refinement. The first higher-target
trials failed native clearance while reporting no outside/crossing faces; the original
retry omitted that case. The corrected retry uses the existing feature-preserving native
method with the same target and clearance checks. Self-intersections, degeneracy and unrelated
tool failures remain errors. Initial failed jobs retained accepted meshes as expected.

`tools/skin_count_acceptance.py` passed QTest root editing/undo, ancestor selection,
document-budget focus/editing, subtree editing and narrow-window scrolling. Captures were
visually inspected; offscreen viewport pixels are not geometry evidence. Local-only records
are in `build/skin-count-controls/{qualified,ui-final}`; failed pre-fix jobs remain in
`numerical`. The full development gate is running (`development-gate-resumed.log`). The
initial gate passed the Python static checks, six native CTests, native style, PowerShell
parsing and function limits, then stopped because its default Qt SDK path was absent in
this worktree. The remaining gate resumed with the installed SDK explicitly selected;
QML validation passed (187 files, 46 models, zero API errors).

The compiled package contains clean implementation revision
`67b7d41b76622b9b3b945a4b29e29ddb74154a2f`. Its executable SHA-256 is
`AB53766B5B7B7D0CB2726AE9812BB81732B6EA3A6E183889CDF32A65ECDEC9C6`.
Relocated-package acceptance passed without developer environment settings: fresh AVBD
generation, failure retention, checkpoint reuse, ordinary save, Final construction and
direct update, changed-root prefix invalidation, and VCP growth. A normal native-window
launch then opened a separate fixture, edited the root target to 802, rebuilt the envelope
and saved an accepted 1,024-vertex / 2,044-triangle mesh. Topology controls and inherited
document budget were visually inspected in that window. The saved test app was closed.
Package and native-window evidence is local-only under
`E:/development/anthroforge/build/skin-count-controls-release`.

Next: finish the full regression gate, replace canonical 0.4.3 plus source archive, then
merge/push main. Preserve unrelated source edits and any open user project. Small fixtures
do not establish whole-body quality.

## Recovery inputs

Work in `C:/Users/alexe/.codex/worktrees/general-agent-instructions/anthroforge`.
Reuse `E:/development/anthroforge/.venv`, Qt SDK 6.12.0, native `build/skin-pipeline` and
the verified numerical image at `build/avbd-p8xfe46u/runtime`. Main checkout and
`E:/development/anthroforge/build/application-boundaries` contain unrelated edits.
Delivery: `E:/development/anthroforge/dist/0.4.3/AnthroForge.dist`.
