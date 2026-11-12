# Painting System — Step 1

Implemented foundation for tissue weights and SCP collagen; qualification is recorded
in [the task record](tasks/painting-system-step1.md). This is not completion of Muscle
Paint or 0.5.0. Package version 0.4.3 and project schema 9 are unchanged.

## Responsibility and extension boundary

`core.painting` defines immutable brush, stroke-input, surface-reference and provenance
records. `application.painting` owns transient strokes in each editing context, including
variants. Painting is not authored document state. `painting_jobs` uses the existing
coordinator for capture, coalescing, cancellation, computation and publication.

`painting_consumers` explicitly composes tissue_weights and collagen adapters. Each owns
target eligibility, baseline/currentness, surface provenance, numerical effect, bounded
result projection and domain commit. Effects are consumer-owned candidates; the common
lifecycle does not require a vertex array. These two consumers expose scalar fields.
Future region/path consumers must supply their own effect and read adapters.

Native projection, visibility, material mapping and blending are unchanged. Desktop
captures camera/pointer input and displayed occluders, presents leased preview resources
and reports service status. It owns no worker completion, timer or automatic commit logic.
Qt objects remain on the presentation thread; jobs receive owned snapshots, consistent
with [Qt threading guidance](https://doc.qt.io/qt-6/threads-qobject.html).

## Public operations

Run `anthroforge run examples/painting.json` from the repository root for a complete
Qt-free collagen stroke, inspection and save. Tissue-weight usage follows below.

| Operation | Arguments and behavior |
| --- | --- |
| `painting.describe` | `consumer`, `target`, consumer options; returns availability/reason, defaults, ranges and supported capabilities without submitting work. |
| `painting.begin` | `consumer`, `target`, `view`, optional `brush`, consumer options; captures a fixed baseline/view/settings and returns a token. |
| `painting.append` | `token`, ordered `samples` batches of `[x,y]`; requests the latest preview sequence. |
| `painting.finish` | `token`; freezes input and automatically computes/commits one complete stroke. No confirmation. |
| `painting.preview` | Complete `samples` plus begin arguments; read-only preparation, for authoring and hover. |
| `painting.commit` | `token`; explicitly commits a ready complete-stroke candidate, once. Cannot join another gesture. |
| `painting.status` | `token`; state, job, sequence, candidate revision, pending finalization, provenance, report and error. |
| `painting.result` | `token`, `offset=0`, `limit=4096`, optional `expected_revision`; returns scalar values, total and candidate revision. Maximum page size 16,384. |
| `painting.cancel` | Optional `token`; cancels work, releases service-owned candidates and leaves authored values unchanged. Omitted token cancels all context painting. |

Consumer identifiers are `tissue_weights` and `collagen`. Tissue options include an existing
field `name` and displayed `stage` (`rest`, `intrinsic`, `final`); BASE/REST is the field's
material domain, not a replacement for the displayed stage. Collagen uses accepted SCP
geometry. Optional `expected_asset` must identify the actual displayed resource. `obstacles`
uses the existing explicit surface/asset/frame records. IDs and revisions are public;
native handles are never request arguments.

The existing 14-number `view` camera convention and screen coordinates are preserved.
`brush` accepts either the legacy `[radius, weight, strength, falloff, through]` list or
a named object. Defaults are radius 40 pixels, weight 1, strength 1, falloff 1 and Through
false. Ranges remain radius 1–4096, weight/strength 0–1 and falloff 0.05–20. Only SCREEN
space is supported. A stroke has at most 4,096 finite two-dimensional samples.

```python
state = session.command("painting.begin", consumer="tissue_weights", target=tissue,
                        name="paint", stage="final", view=camera,
                        brush={"radius": 40, "weight": 0.7})
session.command("painting.append", token=state["token"], samples=[[0, 0], [20, 10]])
session.command("painting.finish", token=state["token"])
session.wait()
assert session.command("painting.status", token=state["token"])["state"] == "committed"
```

## State, revisions and ownership

One interactive stroke or pending finalization is allowed per editing context. Previews
coalesce through the coordinator's 60 ms interactive schedule. Finish has no batching
delay and reuses an exactly matching ready candidate; otherwise it computes the final
sequence. `Session.wait()` drives publication without Qt or desktop callbacks.

States are drawing, queued, running, ready, committed, cancelled, obsolete, failed or
stale. Status reports pending finalization separately. Input settings stay fixed. A valid
previous preview remains visible while its replacement computes; changed geometry hides it.
Paging can read the latest ready candidate during replacement, but its revision identifies
that candidate rather than the pending sequence. Require the revision on later pages.

Begin captures source geometry and baseline identity. Dispatch acquires owned input
resources and validates them; publication rechecks currentness and edit capabilities.
The existing conservative geometry signature includes scene membership and explicit
occluders. Camera/bookmark metadata does not invalidate unchanged geometry. Field/settings
changes, deleted targets, read-only mirrors and workspace restrictions remain enforced.

Finalization reserves its writer through the coordinator. A pending save blocks new user
edits but permits an already-admitted publishing writer to complete its ordinary edit
transaction. A changed stroke produces one undo action; previews/no-ops create no history
or placeholder revision. Undo/redo cancels obsolete painting before history navigation.
Selection/workspace changes retain desktop cancellation behavior. Context/project closure
and teardown cancel and release service ownership. Viewport leases remain independent.

Each context retains at most one candidate per registered consumer, not a stroke archive.
Superseded job payloads are retired by existing coordinator cleanup. Native projection
caches retain their existing budgets. Painting sessions/candidates are never serialized.

## Compatibility and numerical contract

`tissue.inspect.paint`, `skin.inspect.paint`, their status/cancel commands, and
`tissue.field.paint.commit` / `skin.collagen.paint.commit` are compatibility adapters.
Their inputs, read-only preview behavior, response fields and job-qualified commit remain
supported. Other tissue-inspection consumers keep their lifecycle.

Coverage remains screen-space distance to the stroke polyline, maximum coverage within
one stroke, existing falloff and interpolation toward the requested value. There is no
dab accumulation, point resampling, smoothing, new visibility rule or numerical fallback.
Native computation, resource preparation, publication and downstream domain work remain
separately visible through the existing profiler (`painting` task kind).

Muscle Paint, Paint Outer, envelope generation, physical-width brushes, gap interpolation,
queued consecutive strokes and transient-paint history remain outside this increment.

## Qualification evidence

The numerical baseline is production code at `713d963e`; the comparison checkout
`308ca03d` has identical application/native code. Candidate runtime is `b306e77f`.
Both use the same qualified native DLL. No native painting source changed.

`tools/painting_qualification.py` runs serial old/new/new/old trials. Twelve preview
conditions vary camera projection, sparse/dense sample sequences and Paint Through,
with explicit occluders. All 36 sets of scalar arrays match bit-for-bit across runs.
The first two previews per process are cold; the following ten form the warm summary.

| Workload | Values | Old/new warm median | Old/new standard deviation |
| --- | ---: | ---: | ---: |
| Dense SCP collagen | 66,049 | 21.24 / 21.11 ms | 5.07 / 4.67 ms |
| 96-muscle assembly SCP collagen | 10,242 | 66.02 / 70.84 ms | 5.37 / 6.00 ms |
| 96-muscle assembly tissue REST field | 13,845 | 72.77 / 74.52 ms | 11.65 / 11.49 ms |

These are command-to-ready times, not solver-only times. Variation includes deliberately
different conditions, so the standard deviation is not a confidence interval for a speed
claim. Earlier ABBA trials measured assembly collagen at 67.80 / 67.10 ms. System busy
fractions during final trials were 4.8–12.3%, including the tested application; background
processes and thermal state were uncontrolled. This refactor does not establish a speedup.

Profiler investigation found redundant validation in the new capture path. Removing it
reduced material-axis calls from 400 to 224 in the assembly recording (baseline 214).
New preview creation also checks baseline identity immediately, as required by the new
stroke contract; the old preview captured it only at dispatch. In separate recorded runs,
34 preview requests cost 56.52 ms total versus 26.27 ms previously. Native preparation
remained 24 calls, 1,423.97 versus 1,461.43 ms; native effects remained 24 calls,
53.31 versus 52.64 ms. These overlapping inclusive timings must not be added or subtracted
as exact profiler overhead. Cancellation alone averaged 0.13 ms in the recorded assembly;
unrecorded request/cancel/wait medians were 1.08 ms collagen and 1.57 ms tissue versus
0.26 / 0.49 ms previously, including the new upfront capture checks.

Commit-and-wait measurements, including downstream evaluation, remained comparable:
assembly collagen 9.04–10.12 ms and tissue 309.23–314.30 ms, versus 9.04–9.35 ms and
308.75–314.88 ms. Exact candidate reuse, cancellation during work, supersession, save
waiting, no-op history, undo/redo, context isolation and resource release have dedicated
regressions. Desktop candidates match authoring values exactly; mirror and workspace
edit restrictions are enforced through the shared services.

Measured peak unique geometry ownership was identical: 48,510,644 bytes on the dense
fixture and 658,979,620 bytes on the assembly. This is profiler-accounted geometry, not
total process RSS. Dense projection caching retained 47,453,666 bytes in both versions;
the full explicit assembly exceeds that cache's existing budget and retains no projection
entry in either version. Repeated previews replace resources rather than accumulating
an archive; viewport-held owners remain valid until their leases end.

The production input was `skeleton_96_muscles_shortcuts_v001.anthroforge`, SHA256
`308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`.
Its hash was unchanged after every run. Raw arrays, profiles and hidden GPU captures
are local under `build/painting/`; the committed qualification tools reproduce them
when that external fixture is available. Actual two-angle preview/cancel images were
inspected. Hidden/offscreen rendering does not establish interactive user acceptance.

Ownership review is separate from these tests: Core contains immutable inputs only;
the application owns context state and coordinator jobs; explicit consumer adapters own
domain validation/effects/commits; Desktop owns input and leased presentation. Legacy
inspection routes delegate instead of retaining another state machine. No Qt object,
new worker pool, numerical algorithm, transient project record or stroke archive was added.
Full gate and relocated executable results are recorded in the recovery task record.
