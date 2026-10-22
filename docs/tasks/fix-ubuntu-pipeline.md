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
- After type checking, Ubuntu exposed deprecated CGAL headers in vendored libigl.
  That same integration also contains the dead returns causing Windows MSVC C4702.
  Update the deprecated aliases to identical current CGAL types and remove only
  unreachable returns. Preserve warnings-as-errors and all numerical algorithms.
  [Vendor provenance](../../native/boolean/PROVENANCE.md) records the patches.
- Follow [cloud development](../cloud_development.md) and
  [engineering guidelines](../engineering_guidelines.md).

## Current state

Fetched and inspected current `origin/main`; clean checkout. Failure logs retrieved.
Local setup reproduced the identical mypy failure. The renderer now selects its
creation flags under a module-level `sys.platform == "win32"` branch, which
[mypy explicitly supports](https://mypy.readthedocs.io/en/stable/common_issues.html#python-version-and-system-platform-checks).
The selected flags and subprocess lifecycle retain their existing behavior.

## Verification

- GitHub Ubuntu job `120050219101`: dependency setup, host checks and Ruff passed;
  mypy failed before native build/tests.
- GitHub Windows job `120050219815`: mypy passed; native build failed.
- Local `bash tools/cloud/setup.sh`: reproduced the original mypy error after
  successful dependency refresh, host checks, ShellCheck and Ruff.
- After the correction, `uv run --no-sync python -m mypy` and the same command
  with `--platform win32`: both passed, 327 source files each.
- Targeted Ruff lint/format and `git diff --check`: passed.
- Real Linux renderer subprocess success, failure logging and cancellation passed.
- [Run 39864610919](https://github.com/ctrl0alt0del/native_anthroforge/actions/runs/39864610919)
  passed Ubuntu mypy and reproduced the subsequent CGAL `-Werror=cpp` build failure.
  The local gate reproduced the same build failure.
- Native compatibility corrections and full portable/remote gates pending validation.

## Next actions and blockers

1. Run the full portable gate and verify Ubuntu CI on the pushed correction.
2. Resolve any subsequent Ubuntu failures exposed after type checking.
3. Reconcile latest main, integrate the validated repair, and verify remote ancestry.

## Recovery inputs

Use `bash tools/cloud/setup.sh` and source `tools/cloud/environment.sh` in new
shells. Existing ignored environment/build outputs are available but predate main.
Network shell commands require the supported additional network permission.
The cloud host blocks `archives.boost.io`. Local validation uses the official
[Boost 1.89.0 no-docs release archive](https://github.com/boostorg/boost/releases/download/boost-1.89.0/boost-1.89.0-b2-nodocs.tar.xz),
SHA256 `875cc413afa6b86922b6df3b2ad23dec4511c8a741753e57c1129e7fa753d700`,
extracted into ignored `.tools/boost-1.89.0` and selected with
`cmake --preset portable-core -DFETCHCONTENT_SOURCE_DIR_AF_QUERY_BOOST="$PWD/.tools/boost-1.89.0"`.
Repository dependency URLs/digests remain unchanged; CI tests the configured archives.
