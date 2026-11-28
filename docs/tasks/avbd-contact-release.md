# Complete AVBD contact optimization and full-project qualification

- Task branch: `codex/avbd-contact-release`; integration branch: `main`.
- Starting revision: `6ac2f11561aa6b8101ea9ca6281a4d907959eea1`.
- Status: final packaged full-project validation in progress.
- Active writer: current desktop chat; updated 28 November 2026.

## Outcome and acceptance

The user selected no vertex elimination and asked to finish the full project. Integrate
the measured contact optimizations with the SCP skin fully active, generate the complete
AVBD draft for `skeleton_all_reconstructed_muscles_v001.anthroforge` (58 bone and 265 muscle
instances), and deliver portable 0.4.3 to the main project's `dist/0.4.3/AnthroForge.dist`
with its matching source archive. Qualify normal GUI generation without external runtime
configuration. Preserve the original authored document and save the result separately.
Full-model quad topology is outside this draft-generation task.

## Decisions

- **D1, user-confirmed:** no dynamic sleeping, inherited sleeping or SCP activity masks.
  Existing VCP regional boundary conditions remain. Combined sleeping tests showed no net
  gain; the earlier performance/sleeping reports retain those rejected experiments.
- **D2:** canonical contact ordering and candidate allocation belong to the native contact
  pipeline. Two stable 64-bit GPU radix passes preserve full tuple order and duplicates.
  Keep force transfer, motion guards, fallback processing and the 2 GiB owned GPU bound.
- **D3:** a typed radius initialization setting preserves root 0.03 and fixed VCP 0.012;
  subsequent local SCP stages start adaptively at the measured 0.0065. The radius can grow.
  This changes the solve trajectory; it is not byte-equivalent to the original 0.03 run.
- **D4:** prefer eight candidates per contact, bounded by the shared workspace estimator;
  retain the supported four-times/page minimum. Explicit requests that cannot fit fail.
- **D5:** the app release checkout is `C:/Users/alexe/.codex/worktrees/general-agent-instructions/anthroforge`.
  The native runtime is `E:/development/anthroforge/build/application-boundaries`, with
  extensive pre-existing uncommitted work. Preserve exact preimages and a task-only patch;
  the shipped `avbd-sources.zip` retains the complete qualified native baseline and delta.
- **D6:** preserve content-based runtime/checkpoint identities. A changed runtime invalidates
  incompatible app prefixes. Native continuation fixtures are explicit numerical tests,
  not an application checkpoint-identity bypass.
- **D7:** initialize the shared compact/base/full-width key policy before choosing batched
  SCP or unbatched VCP storage. Remove the latter's obsolete 32,768-vertex cap; preserve
  signed 32-bit vertex-ID bounds. This fixed the first complete-run failure.
- **D8:** replace the shared input reader's historical 64-collider cap with a bound derived
  from file bytes and the minimum valid mesh record. Keep positive counts, dimensions,
  finite coordinates, valid indices and truncation rejection. The spatial audit shares
  this validator and checks combined signed 32-bit index bounds before merging geometry.
  This changes admission, not numerical settings or geometric acceptance.
- **D9:** guard optional final containment-audit calls with the same feature macros as their
  declarations. Rebuilding all reader callers exposed this existing legacy compile error;
  enabled diagnostics and solving remain unchanged.
- **D10:** an old temporary package's Python DLLs were held by the native continuation.
  Finish a fresh `package-v3/AnthroForge.dist`; never alter the canonical running package.
  The native continuation and fresh app run overlapped within available GPU memory, each
  retaining its owned-memory bound. Their timings are contended qualification measurements.

## Implementation and preserved evidence

The [task-only native delta and portable host tests](avbd-contact-release/README.md) cover
ten changed source files and four new headers. App source, native ABI and orchestration
code are unchanged from the compiled app revision. The original authored model hash is
`b5c50e721cc15e052d26871cbe2668a858118f9819690b7e6d590ca957ea6d8b`.

All ignored local evidence is under `E:/development/anthroforge/build/avbd-release-20261128`
(`R` below). Original failure evidence is in `build/avbd-full-muscles-001-20261127`; matched
performance and sleeping experiments are in `build/avbd-performance-20261128` and
`build/avbd-sleeping-optimized-20261128` in the main project directory.

| Run | Observed result | Retained evidence |
| --- | --- | --- |
| Original baseline | 31 min 23 s; 37 bones, then Fibula allocation failure | Original failure folder |
| Packaged v1 | 58 bones in 1,236.24 s; 2 already-clear muscles; unbatched key cap failed on muscle 2 | `R/full-project` |
| Packaged v2 | 58 bones in 895.73 s; 190 muscles; 70-collider deltoid hit the reader cap; 4,272.42 s total | `R/full-project-final` |
| Native v3 continuation | All 265 muscles accepted, in recipe order; 159 already clear, 63 movement, 43 local fill | `R/muscles-v3/qualification.json` |
| Fresh packaged v3 | All 58 bones accepted; full muscle sequence still running | `R/full-project-v3` |

The v1/v2 harness files named `complete-result.anthroforgex` are partial failure documents,
not completed skin results. Do not deliver them. The v2 native diagnostic continuation
was deliberately stopped after 22 accepted muscles; its explicit stop receipt is retained.

Native v3 completes with 103,059 vertices and 206,114 triangles, finite positions and valid
indices. Minimum recorded clearance is 0.06361128 against required 0.06324186. Its final
75 stages took 1,846.94 s, partly overlapping fresh v3; total recorded muscle stage wall
time including the old prefix is 5,099.93 s. This is numerical qualification, not a saved
application result. A read-only application publication probe also bound all 103,059
vertices to 323 sources in 12.65 s, with finite arrays, normalized weights and valid owners
(`R/publication-audit.json`). The probe imports the normal Session bootstrap first; direct
storage-first imports hit an existing circular module import, not a solver failure.

## Validation

- Host C++ tests: 200,032 randomized/duplicate/boundary keys; stable canonical ordering;
  candidate budget minima/preferences/bounds and invalid requests; root/local/fixed radius
  isolation; 1/64/65/70/323 collider inputs, exact geometry and malformed/truncated input.
- Native builds: both numerical workers and all 21 affected reader/audit targets compile.
  Optional diagnostic configurations compile after D9. Native pinned-orientation CTest passes.
- Matched Fibula/Radius/finger controls: same-radius positions, faces, velocities and contact
  checkpoints are byte-identical; native geometric audits and motion guards pass. The
  isolated Fibula prototype improved 165.62 s to 4.18 s; release replay took 4.78 s under
  contention. A 2.3-million cache fits at reduced candidate preference; 2.8 million correctly
  rejects insufficient workspace. Maximum full bone-chain owned GPU memory: 2,113,992,300 bytes.
- All 58 bone checkpoints match across v1/v2/v3. Previously accepted large-muscle replay
  matches byte for byte after D8. The first 14 fresh v3 muscle checkpoints match v2; the
  complete common 190-stage prefix will be compared after the fresh run reaches it.
- Development gate: lock/static/type/format, native build, six native CTests, native style,
  PowerShell, QML (187 files, 46 models, zero API errors), numerical imports and native
  doctor pass. Missing worktree-local Qt SDK was handled by explicitly using the installed SDK.
  Full pytest: 3,026 passed, one unchanged tetrahedralization subprocess access violation
  in the X/INSTANT topology case. Its complete six-test module passed separately in 97.55 s.
  Do not call the initial suite clean or claim that dependency crash is fixed.
- Changed/test/harness function review: 86 functions at most 15 physical lines. The saved
  unified patch retains valid blank context lines; these are not source trailing whitespace.
- Final v3 package: official `package_release.finish()` and all 8,536 file hash/size checks
  plus 1,166 isolated imports pass. Executable SHA-256:
  `cdf6b61b5fdf33a47135386d025359d5d06537caf8b33bc78207e4fb42962e44`.
- Final v3 GUI generation: ordinary no-argument launch with external runtime variables
  removed; open small bone/muscle control, Rebuild envelope, observe Applied AVBD / current /
  Idle, save revision 32 and close. Accepted result: 690 vertices / 1,376 triangles.
  `R/gui/v3-generation.png` and accessibility capture retain actual inspection.

## Resume and finish

Only `R/package-v3/AnthroForge.dist` is the final candidate. The canonical distribution is
unchanged pending full-app success. The fresh full app run is active (initial PID 32724,
`R/full-project-v3/process.json`); diagnostics survive under `afskin-zusm4lf_`.
Run `R/full_progress_v3.py` and inspect `authoring.jsonl`, `stderr.log`, `exit.json`.
Do not duplicate the solve. Native `muscles-v3` is complete and stopped.

1. Wait for every muscle, app publication and `complete-result.anthroforgex` save.
2. Run `final_audit_v3.py`, analysis, complete common-prefix comparison and final native
   surface parity. Audit stage order, exact saved geometry, metadata, pipeline current and ZIP CRC.
3. Open the completed full project normally in the GUI; inspect and retain the final view.
4. Finish documentation, refresh packaged docs and create/CRC-check the corresponding source
   archive with the exact v3 runtime source. Preserve original model; copy result to a new sibling.
5. Run reviewed `R/deliver.ps1` only after candidate/canonical processes close. It backs up the
   prior complete same-version build/source under `R/delivery`, preserves other versions and
   promotes the candidate to the canonical location. Verify hashes after promotion.
6. Commit/push final record, fetch/reconcile and merge/push normally to `main`; verify ancestry.

The native checkout's pre-existing implementation remains local and dirty. The task patch
alone cannot recover it; exact runtime source recovery is provided by the release archive.
