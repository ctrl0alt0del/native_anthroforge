# AnthroForge standalone development

- Read README.md and the confirmed specification before changing behavior. The specification takes precedence over proposals in the stack analysis.
- Search official sources for existing APIs, approaches, algorithms, packages, and tools before choosing an implementation.
- Keep every new function at 15 physical lines or fewer. Use focused helpers, not compressed unreadable statements. Python checks enforce this; native code also has a clang-tidy configuration.
- Work directly unless the user explicitly requests delegation. Preserve unrelated changes. Do not contact a Git remote, fetch, pull, push, or open a PR without an explicit user request.
- Implement optimization, iterative numerical work, and repeated numerical geometry queries in C++. Python owns orchestration, validation, serialization, and UI/API adapters. No Python optimizer fallback or per-iteration Python callbacks.
- Keep core/application/native Python modules independent of Blender and the desktop UI. UI, CLI, tests, and later MCP adapters use the same application operations. Numerical headless use must not initialize Qt.
- Keep authored data, completed results, provisional previews, and per-view presentation distinct. Own geometry and its lifetime explicitly; do not pass mutable UI objects to workers.
- Preserve the exact scheduling, undo, checkpoint, blocked-save, import, unit, startup, and skin-only export decisions in the specification. Do not invent simplified product semantics while scaffolding.
- Reuse qualified addon kernels and contracts. Inspect existing capabilities before recommending replacement; distinguish observed failures, hypotheses, and verified improvements.
- Tests must exercise behavior and relevant failure cases. Run tools/check.ps1 for the development checks. GUI/packaging checks are separate and must be reported honestly.
- Existing root __init__.py is an unrelated legacy Blender stub. Preserve it; the standalone package lives in src/anthroforge.
- Keep local SDKs, environments, outputs, fixtures, and captures in ignored directories. Do not commit large binaries or production anatomy assets.

