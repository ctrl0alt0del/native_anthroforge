# Restore the Ubuntu GitHub Actions pipeline

- Task branch: `codex/fix-ubuntu-pipeline`
- Integration branch: `main`
- Starting revision: `c74b28085c31f894f6ce343265d999da526a6feb`
- Status: implementation and validation complete; ready for integration
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
- `tools/check_core.py` must exclude `native/vendor` translation units from the
  authored function-size check, matching `tools/check-native-style.ps1` and the
  documented vendor exemption. Native compilation and all tests still include them.
- The complete GCC pass exposed misleading indentation in `simple_subdivision.cpp`
  and `stacking_results.cpp`, and a missing GCC counterpart to the tissue wrapper's
  existing scoped unused-function allowance. Correct these at their owning boundaries.
- Stacking's `order_pairs` held `std::minmax` references to temporary ID casts.
  Reuse the existing value-returning `relationship_key` and update maintained source
  provenance. [CH-045](../computation_history.md#ch-045--owned-stacking-relationship-lookup-keys-2026-10-22)
  records the ownership correction; ordering policies and numerical methods remain.
- Windows subsequently reached `curve_fit.cpp` and reported MSVC C4244 on the
  intentional double-to-float range constructor. Use an explicit conversion into
  the same float buffer, preserving the donor fitting precision and validation.
- Later MSVC failures in imported routing headers were unused OpenMP workers
  (C4189) and bounded `1/-1` conversion to `int8_t` (C4244). Complete the wrappers'
  scoped MSVC allowances for imported routing/stacking code and unused tissue
  entry points. Authored-code warnings-as-errors and pinned donor bytes stay intact.
  The complete MSVC build also identified C4267 in the donor's Eigen triplet index
  conversion; its allowance is scoped to the imported stacking headers.
- The full Linux suite exposed two tests comparing borrowed NumPy buffers from
  already-destroyed temporary geometry. Retain their reference mesh owners throughout
  comparison and document `Geometry.array`'s existing borrowed-view lifetime.
  Exact array equality and all runtime geometry/cache behavior remain unchanged.
- MSVC C4146 rejects unsigned unary negation in the PCG bounded sampler. Express
  the same modulo-2^32 arithmetic as unsigned subtraction from zero, preserving
  the existing NumPy-compatible random sequence. The shared Ninja build now
  collects all compiler errors (`-k 0`) before failing, so later diagnostics remain
  visible in one CI run; successful build/test behavior is unchanged.
- Follow [cloud development](../cloud_development.md) and
  [engineering guidelines](../engineering_guidelines.md).

## Current state

Both Ubuntu and Windows CI pass at `c4edc98`, with all 1722 tests on each platform.
Ubuntu also passes native style checks, setup and repeatable refresh. The complete
local gate passed at `70f4e62`, followed by a native rebuild and targeted checks
after the MSVC-only diagnostic allowance. All implementation increments are on
the task branch, ready for a normal merge into the unchanged `main` at `c74b280`.
No schema, solver tolerance, GUI feature or package version changes are included.

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
- Native compatibility corrections are validated by the complete local gate.
- Targeted clang-tidy on vendored `curve_fit_cubic.c` reproduced 20 function-size
  errors. This source is unchanged upstream code; the portable style check now
  applies the existing authored-code policy consistently.
- A mocked compile database confirmed the style check retains authored files,
  deduplicates entries and excludes only the actual vendor directory.
- `cmake --build --preset portable-core -- -k 0` collected every GCC compilation
  failure in one pass; the corrected native build passes. Targeted clang-tidy
  on the reformatted subdivision adapter passed.
- Full native compilation, all five CTests and all 162 authored clang-tidy inputs
  passed. All 57 targeted stacking/provenance/drawing tests passed.
- First full pytest run: 1720 passed, two failed from temporary mesh lifetimes in
  `tests/test_tissue_preparation.py`. Corrected tests plus architecture: 16 passed.
- `uv run --no-sync python tools/check_core.py --native-style` at `70f4e62`: passed
  all 1722 pytest cases (zero skips), five CTests, 162 authored clang-tidy inputs,
  Ruff/mypy, headless save/reopen workshop, wheel/source builds and wheel resources.
- `bash tools/cloud/refresh.sh`, fresh-shell doctor and Ninja `-k 0`: passed.
- Ubuntu [run 39867241612](https://github.com/ctrl0alt0del/native_anthroforge/actions/runs/39867241612)
  passed at `127b3a8`. Follow-up [run 39867569502](https://github.com/ctrl0alt0del/native_anthroforge/actions/runs/39867569502)
  also passed Ubuntu at `70f4e62`; Windows completed all compilation and found only the donor
  Eigen triplet conversion warning addressed by the latest scoped allowance.
- After the final MSVC-only allowance, the native rebuild, all five CTests and
  29 stacking/provenance tests passed locally at `c4edc98`.
- Final [run 39868831213](https://github.com/ctrl0alt0del/native_anthroforge/actions/runs/39868831213)
  passed on Ubuntu and Windows at `c4edc98`. Each platform passed all 1722 tests,
  five CTests, Ruff/mypy, the headless workshop and wheel/source builds. Ubuntu
  also passed native style checks, setup and repeatable refresh.
- Windows interactive GUI and portable executable qualification were not run;
  this task concerns compiler/check compatibility, not GUI behavior or release packaging.

## Next actions and blockers

Implementation and required checks are complete. Merge the task branch normally
into `main`, push it, and verify the remote tip contains the validated repair.
No blockers remain; Git ancestry records integration after the merge.

## Recovery inputs

Use `bash tools/cloud/setup.sh` and source `tools/cloud/environment.sh` in new
shells. Generated evidence is in `build/core/qualification/{passed.json,pytest.xml}`
and `build/core/ubuntu-pipeline-qualified.log`; these local outputs are ignored.
Network shell commands require the supported additional network permission.
The cloud host blocks `archives.boost.io`. Local validation uses the official
[Boost 1.89.0 no-docs release archive](https://github.com/boostorg/boost/releases/download/boost-1.89.0/boost-1.89.0-b2-nodocs.tar.xz),
SHA256 `875cc413afa6b86922b6df3b2ad23dec4511c8a741753e57c1129e7fa753d700`,
extracted into ignored `.tools/boost-1.89.0` and selected with
`cmake --preset portable-core -DFETCHCONTENT_SOURCE_DIR_AF_QUERY_BOOST="$PWD/.tools/boost-1.89.0"`.
Repository dependency URLs/digests remain unchanged; CI tests the configured archives.
