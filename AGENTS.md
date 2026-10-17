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
- In Codex Cloud/Linux, follow [cloud development](docs/cloud_development.md). Run `bash tools/cloud/setup.sh` for first setup; source `tools/cloud/environment.sh` in new shells and run `uv run --no-sync python tools/check_core.py --native-style` for the portable gate. This gate includes the complete pytest suite but does not certify Windows GUI or executable packaging.
- Existing root __init__.py is an unrelated legacy Blender stub. Preserve it; the standalone package lives in src/anthroforge.
- Keep local SDKs, environments, outputs, fixtures, and captures in ignored directories. Do not commit large binaries or production anatomy assets.

## Design quality for fixes and features

- Read and apply [engineering guidelines](docs/engineering_guidelines.md) before implementation or design review. These are project working rules; the confirmed product specification remains authoritative.
- Own architectural diagnosis. Before choosing a fix, identify the cause, responsible layer, affected callers and invariants. Determine whether the defect is local or exposes a missing responsibility, contract or extension point. Do not wait for the user to request this analysis.
- Fix shared causes at their owning boundary. When behavior varies by task or feature, separate that policy from shared lifecycle and safety mechanisms. Integrate the affected callers; adding an unused abstraction does not complete the work.
- Apply SOLID through cohesive responsibilities, narrow contracts, substitutable implementations and explicit dependencies. Prefer composition. Justify each new abstraction with a current requirement, observed variation or necessary isolation boundary.
- Choose the smallest coherent design that solves the actual problem and supports confirmed requirements. A small patch is appropriate when the existing boundary is sound. Do not minimize changed lines at the expense of duplicated rules, hidden coupling or inconsistent behavior; do not build speculative frameworks.
- For changes spanning responsibilities, state the observed cause, proposed ownership, preserved contracts and validation in a short progress update. Proceed within authorized scope; this is not an approval gate or a requirement to create a design document for every fix.
- Test the failed behavior and relevant shared contracts. Use representative performance/GUI evidence when those are the issue. Review design quality separately from test success; passing tests alone does not establish appropriate ownership or extensibility.

