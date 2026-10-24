# Shortcut update performance — 0.3.3

The user workflows and shared commands are unchanged. Numeric metadata notifications follow
relevant definitions and relationships instead of every accepted geometry revision; hidden
fields do not request metadata. Formula observation uses a reverse read index and retains
exact input validation. Publication avoids rebuilding an unchanged shortcut context, and
priority dependency links are maintained with active job registry mutations.

Temporary urgency still propagates to prerequisites. This release does not change geometry
algorithms, attachments, numerical tolerances, update modes, history, schema 5 or saving.

## Production measurements

The four controls use the migrated 96-muscle assembly. Three recorded baseline/candidate
pairs per control ran serially, alternating order. Baseline is `31fc158`; native library,
fixture and settings were shared. Opening, fingerprinting and report export are outside the
edit timer. These headless measurements exclude desktop rendering. Background load is
recorded; thermal conditions and other applications are uncontrolled.

| Update | Baseline median | Candidate median | Reduction |
| --- | ---: | ---: | ---: |
| Ribs Top Radius to 3 | 11.114 s | 9.237 s | 16.9% |
| Humerus Length +5% | 5.542 s | 4.509 s | 18.6% |
| Radius Length +5% | 4.573 s | 3.635 s | 20.5% |
| Thumb Metacarpal Thickness +5% | 1.061 s | 1.030 s | 2.9% |

The small Thumb change should not be treated as a strong responsiveness improvement.
Ribs publication fell from 6.283 to 4.755 seconds inclusive; priority ordering fell from
1.014 to 0.755 seconds. These overlapping intervals must not be summed with worker times.
Profiler overhead is included and cannot be exactly subtracted.

All trials preserve coordinates, resolved poses, bindings and oriented connectivity. Thumb
can differ in triangle enumeration, the existing Boolean output behavior; canonical oriented
connectivity and attachment references remain unchanged. Ulna attachment publication remains
around 1.8 seconds into the Ribs update in the inspected paired traces.

Local artifacts: `build/shortcut-performance-033/headless-summary.json`, paired `.afprofile.zip`
files and fingerprint JSON under `build/shortcut-performance-033/trials`. Reproduce an individual
trial using `tools/shortcut_performance.py OUTPUT_PREFIX SHORTCUT_4` (or 15, 16, 21).
The tool uses the existing local parity plan; production assets are not bundled into Git.

## Desktop measurements

A serial ABBA comparison ran 30 update ticks with the production Shortcuts panel open.
Baseline runs took 14.659/14.730 seconds; candidate runs took 10.693/10.031 seconds
(29.5% lower mean). Both left 492 active jobs and no errors. This bounded partial workload
does not measure full completion or physical frame latency. Uncached property metadata
queries fell from 6,330 (3.37–3.39 seconds) to zero during these result updates. Metadata
was already populated before the timer; authored changes still invalidate it.

The captures use application-boundary profiling and offscreen QML; they do not establish
GPU performance or full Qt binding attribution. Reports are under
`build/shortcut-performance-033/desktop`. Reproduce with
`tools/shortcut_performance_desktop.py OUTPUT_PREFIX` in the appropriate source checkout.

## Qualification

Metadata subscriptions, exposure/driver edits, undo and Hook topology-lock changes pass
focused regression tests. Offscreen editors and hidden native rendering pass, including
Parametric consumer updates and exact undo. Final gate and portable delivery are pending. See the
[task record](tasks/shortcut-performance-033.md). Background/offscreen checks do not establish
physical display latency or hands-on interaction acceptance.
