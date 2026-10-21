# AnthroForge 0.2.3 — Preferences and ROUTED solver choice

Confirmed application preferences with **Custom / PIQP** selection and future-calculation
semantics. Project schema remains 4; 0.2.2 files remain supported. Qualification is recorded
in [the task record](tasks/preferences-routing-023.md).

## Interaction and persistence

Open **Edit → Preferences…** and choose **ROUTED solver**. Selection saves immediately;
there is no Apply/Accept step. Custom is the default. PIQP selects sparse PIQP;
dense PIQP and automatic backend selection are not exposed.

Preferences belong to the application, outside documents, workspaces and undo history.
They persist across launches and projects in `%LOCALAPPDATA%/AnthroForge/preferences.json`
(Linux: `~/.local/share/AnthroForge/preferences.json`). Storage has its own schema,
independent of the application version. Saving is atomic; failed persistence leaves the
previous choice active. Invalid/unsupported files use defaults with an explicit error
in Preferences and are not overwritten automatically.

Shared API: `preferences.get` and `preferences.set`. Embedded callers can inject an
in-memory `PreferenceStore`; automation can override the file location through
`ANTHROFORGE_PREFERENCES_PATH`. Qualification isolates its settings.

## Execution semantics

Changing the setting preserves current results and running work. Queued jobs capture
the latest preference when dispatched. Newly requested calculations and conversion
previews use the captured backend. **Recalculate** explicitly evaluates existing
objects when desired. Opening a project or changing preferences does not reroute.
Curves and Fibers share this contract. Live/On Release/Manual behavior, undo/redo,
save checkpoints, dependent surfaces and retained material bindings remain unchanged.

Native calls own their selection and solver state; concurrent jobs can use different
backends safely. No global/thread-local selector, silent fallback, competing worker pool,
or Python numerical loop. PIQP uses the existing pinned 0.6.4 library. Sparse setup
is reused only for unchanged matrix dimensions and sparsity patterns.

Both solve the same inner quadratic objective, pins and linearized contacts. Planning,
trust limiting, exact pin restoration, CCD, accepted-step logic, adaptive corner retention
and final validation remain shared. Numerical paths may differ. PIQP subproblem failure
is explicit and retains accepted output through existing Issues. Cancellation checks
surround bounded PIQP solves and outer iterations. Accepted path diagnostics and profiler
path spans identify the backend.

There is no universal speed claim: the [prior experiment](tasks/routing-piqp-benchmark.md)
found workload-dependent results. This release gives the user an explicit choice.
