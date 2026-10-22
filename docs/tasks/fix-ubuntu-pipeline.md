# Restore the Ubuntu GitHub Actions pipeline

- Task branch: `codex/fix-ubuntu-pipeline`
- Integration branch: `main`
- Starting revision: `c74b28085c31f894f6ce343265d999da526a6feb`
- Status: in progress
- Last updated: 2026-10-22 UTC
- Active writer: Codex Cloud, Ubuntu pipeline repair

## Outcome and acceptance

Diagnose and fix the Ubuntu job, preserve existing runtime behavior and required
checks, and validate the complete cloud gate plus setup/refresh in GitHub Actions.

## Decisions and relevant files

- [Failed run 39843406324](https://github.com/ctrl0alt0del/native_anthroforge/actions/runs/39843406324):
  Ubuntu mypy rejects `subprocess.CREATE_NO_WINDOW` in
  `src/anthroforge/application/report_renderer.py:33`; its `os.name` guard does
  not narrow platform-specific stubs. The renderer owns subprocess launch policy.
- Preserve Windows console suppression, non-Windows zero creation flags, renderer
  isolation, cancellation, logging and cleanup. No numerical approach changes.
- The same run has an independent Windows MSVC C4702 failure in vendored libigl
  Boolean headers. Track separately unless Ubuntu validation exposes a shared cause.
- Follow [cloud development](../cloud_development.md) and
  [engineering guidelines](../engineering_guidelines.md).

## Current state

Fetched and inspected current `origin/main`; clean checkout. Failure logs retrieved.
Implementation and local reproduction pending.

## Verification

- GitHub Ubuntu job `120050219101`: dependency setup, host checks and Ruff passed;
  mypy failed before native build/tests.
- GitHub Windows job `120050219815`: mypy passed; native build failed.
- Local checks have not yet run.

## Next actions and blockers

1. Confirm mypy's supported platform guards and reproduce the Ubuntu error locally.
2. Correct the guard, run the full portable gate, push and verify Ubuntu CI.
3. Reconcile latest main, integrate the validated repair, and verify remote ancestry.

## Recovery inputs

Use `bash tools/cloud/setup.sh` and source `tools/cloud/environment.sh` in new
shells. Existing ignored environment/build outputs are available but predate main.
Network shell commands require the supported additional network permission.
