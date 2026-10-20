# Engineering guidelines

These rules apply to fixes, features and refactoring in the standalone AnthroForge
application. Apply them alongside [AGENTS.md](../AGENTS.md), the
[confirmed specification](../standalone_application_recommendations.md) and the
[current architecture](architecture.md). The specification defines product behavior;
this document governs how we implement it. It does not authorize additional product scope.

## 1. Diagnose before choosing the size of a change

For a defect, reproduce the observable failure and trace the path from input to result.
For a feature, identify the required behavior and the existing capabilities it extends.
Inspect related callers and previous approaches before recommending a replacement.
Keep an observed defect separate from a suspected cause; use a discriminating experiment
when the cause is uncertain.

Answer four questions before editing:

1. Which component should own this behavior, and why?
2. Which contracts and invariants must every affected path preserve?
3. Is the problem a local mistake, a shared implementation defect, or a missing boundary?
4. What evidence will demonstrate that the change addresses the user's actual outcome?

Choose a local correction when the current boundary already fits. Refactor the owning
component when the fix would otherwise duplicate rules, add another special case across
callers, or mix responsibilities with different reasons to change. Build an extension
point when current variants or a confirmed requirement need one. Do this analysis
proactively; the user should not have to steer each fix toward sound architecture.

## 2. Define ownership and contracts

Give each invariant one authoritative owner. Callers request operations through that
owner rather than maintaining parallel versions of its rules. Name components for their
domain responsibility; a Coordinator or Manager must still have a bounded purpose.

Separate decisions that vary by feature from mechanisms that must stay consistent.
For scheduling, workload estimates and delay policies vary; output reservations,
cancellation, revision validation and publication remain coordinated. A new policy
must not acquire its own competing queue or bypass lifecycle guarantees.

Make contracts explicit where relevant: input validity, output meaning, units and
coordinate frames, ownership/lifetime, allowed state transitions, failure behavior,
thread affinity, cancellation points and side effects. Specify these at boundaries;
do not scatter implicit assumptions among callers.

## 3. Apply SOLID in practical terms

These are design review criteria for modules and functions as well as classes.

| Principle | AnthroForge application rule |
| --- | --- |
| Single responsibility | Separate geometry calculation, scheduling policy, lifecycle control, persistence and presentation when they change for different reasons. A short function alone does not prove cohesion. |
| Open/closed | Put demonstrated variation behind a stable contract. A new task policy should usually require an implementation and registration; it should not require editing cancellation or save rules. Correct a flawed shared contract when necessary. |
| Liskov substitution | Every implementation must honor the same declared inputs, results, errors, ownership and side-effect guarantees. A replacement must not silently require GUI state, weaken cancellation, or publish behind the coordinator's back. |
| Interface segregation | Expose only the capabilities a consumer needs. Estimation should not require rendering or storage APIs. Avoid interfaces with unrelated methods that implementations can only ignore or reject. |
| Dependency inversion | Keep application rules independent of Qt, Blender and file-format details. Supply external dependencies at clear boundaries; clocks and execution facilities should be replaceable when deterministic tests require it. |

Prefer composition and small explicit protocols/callables over deep inheritance.
Inheritance needs a genuine substitutable contract; sharing a few lines is insufficient.
Dependency injection does not require a container or an interface for every concrete type.

## 4. Choose patterns by the problem they solve

Patterns provide vocabulary for a design decision. Record the concrete need and its
cost in indirection before adding one. Use the simplest implementation that fulfills
the responsibility; a function or data table may be enough.

| Need in this application | Suitable pattern or technique | Boundary to preserve |
| --- | --- | --- |
| Interchangeable scheduling or evaluation decisions | Strategy/policy | Policies return decisions; the coordinator controls execution. |
| Shared UI and headless editing with undo | Commands and explicit transactions | One application operation defines behavior for every client. |
| Qt, Blender conversion, native ABI or storage integration | Adapter | Translate at the boundary; keep external types out of domain contracts. |
| Job states and asynchronous completion | Explicit state machine | Define valid transitions and terminal outcomes; prevent conflicting boolean flags. |
| Worker input and reproducible saving | Immutable snapshots/value objects | State ownership and revision validity remain explicit. |
| Presentation reacting to accepted changes | Observer/signals | Keep notification direction clear; avoid feedback loops that mutate anatomy. |

These are options for the listed needs, not a requirement to introduce all patterns.
Reuse existing mechanisms before adding parallel infrastructure. Prefer one clear
composition point over automatic discovery unless discovery is itself required.

## 5. Keep abstractions useful and code readable

- Justify an abstraction by current behavior, demonstrated variants or a necessary
  isolation boundary. Identify its consumer and the variation it encapsulates.
- Separate shared domain knowledge from coincidentally similar code. Do not couple
  unrelated features merely because their implementations currently look alike.
- Keep the existing 15-physical-line function limit. Extract meaningful operations
  with names and coherent inputs; do not compress statements or create arbitrary
  numbered fragments to satisfy the limit.
- Use domain names, explicit types and named values for meaningful policies. Explain
  units and the evidence behind performance thresholds. Distinguish heuristics from
  guaranteed limits and define behavior when an estimate is wrong.
- Keep mutation and side effects visible. Avoid hidden mutable globals, ambient UI
  selection, broad catch-and-ignore handlers and silent production fallbacks.
- Release resources through their owning lifecycle. Preserve useful failure context;
  distinguish failure, cancellation and obsolete work in APIs and diagnostics.
- Keep refactoring focused on the affected responsibility. Remove superseded paths
  when safe; document intentional compatibility adapters. Preserve unrelated changes.

## 6. Preserve AnthroForge's runtime boundaries

Desktop presentation uses the shared `Ui*` controls and `Theme` metrics. Keep primary
actions and concise state visible; put optional explanations in help and technical
evidence in explicit disclosures. Preserve actionable failures and access to complete
details. Check hover/focus contrast, scrolling and narrow layouts with actual QML;
inspect captures as well as assertions. Background-only requests prohibit visible
test windows and desktop input; off-screen checks must state their rendering limits.

Minimize the steps needed to achieve the user's outcome. A direct setting should normally
apply when selected and produce one coherent undo action. Do not expose implementation
stages as extra buttons, mandatory previews, acceptance gates or confirmations without a
concrete product need. Background computation, validation and failure reporting belong
behind the interaction. Keep optional advanced settings optional. If the intended UI/UX
is unclear, ask the user before choosing or adding steps; do not invent a workflow.
Evaluate the complete interaction, including discoverability and repeated use, rather
than reducing click counts by hiding required controls or weakening shared validation.

The UI and headless adapters invoke the same document operations. Authored anatomy,
accepted calculation results, provisional previews and per-view presentation have
distinct ownership. Workers receive owned inputs rather than live UI objects.

All optimization loops and repeated numerical geometry queries belong in C++, using
batched native boundaries. Python owns orchestration, validation, serialization and
publication. A design pattern does not justify moving numerical loops back to Python.

Async changes must preserve the specified dispatch-time input capture, output
reservations, safe cancellation, obsolete-result rejection, undo/redo and save
checkpoint semantics. Queued work is part of the lifecycle. Account for preparation
and publication costs as well as computation; moving only the solver off-thread
does not establish responsiveness.

## 7. Prove behavior and review the design

Use a regression case for the reported failure and contract cases for any new
interchangeable implementation. Exercise affected existing callers. Add relevant
failure, cancellation, overlap or persistence cases when those contracts change.
Prefer externally observable outcomes over tests that reproduce private implementation.
Use injectable time and controlled completion for scheduling tests where practical.

For performance changes, record representative inputs, baseline, changed behavior and
measurement limits. For viewport or geometry changes, inspect the actual result.
Passing a numerical proxy or creating a file is insufficient when the user's problem
is visual or interactive. Verify the packaged app when delivering runtime changes.

Run the checks appropriate to the change, including the repository development gate
for implementation work. Documentation-only edits need link/content review, not an
application rebuild. Do not add tests for trivial reversible edits merely to increase
test counts. Automated checks complement a separate review of ownership and coupling.

Before delivery, verify:

1. The observed failure or requested feature is handled end to end.
2. The responsible component owns the rule, and affected clients use it consistently.
3. New abstractions have concrete uses and clear contracts; existing ones were reused.
4. Relevant failure paths and product invariants remain valid.
5. Evidence supports correctness and any claimed performance improvement.
6. Documentation describes changed boundaries and material limitations accurately.

If three or four refinements fail to produce an acceptable result, reconsider the
approach and test a materially different alternative. Do not accumulate patches around
an assumption that the evidence has undermined.

## 8. Explain architectural changes without adding approval steps

For a change spanning responsibilities, give a short design note in the progress update:
observed cause, proposed owner/contracts, why that scope is justified, and validation.
Update architecture.md when a durable boundary changes. Keep this proportional to the
work; no separate design document is required for an ordinary local correction.
Proceed with authorized implementation. Ask only when a real unresolved product
decision, destructive action or explicit approval rule requires user input.

The parent/child delay fix illustrates the standard. The observed path published the
parent before worker-based attachment results arrived. The resulting design puts
complexity estimation and delay in per-task policies, with one coordinator retaining
lifecycle guarantees. Its usefulness is supported by the drag comparison and contract
tests recorded in [development status](development_status.md). A new class name alone
would not establish either architectural improvement or a successful fix.

## 9. Preserve computational rationale and evidence

Maintain [computation inventory and history](computation_history.md) in the same
change set as every change of computational approach. Read the relevant inventory
IDs and earlier records before replacing an algorithm or reviving a rejected idea.

This includes algorithm/objective changes, sampling and refinement, constraints and
tolerances, geometry acceptance, dependency/invalidation rules, scheduling, caching,
and movement of work between Python, native code, workers and publication. An
optimization intended to preserve results still needs its reason and evidence recorded.

Update the current inventory and add a change record: observed failure, old approach,
replacement, why it addresses the cause, preserved contracts/intentional differences,
baseline and candidate revisions, representative evidence, and remaining costs or
failures. Use the document's template and stable IDs. Link task details, committed
fixtures/tests and profiler summaries; identify raw local-only artifacts explicitly.
Do not infer shape correctness from solver success or whole-app speed from a kernel
microbenchmark. Preserve rejected/superseded approaches with their reasons and links
to replacements. Pure formatting/renaming requires no computation entry.

An initial checkpoint may mark evidence pending; the validated merge must describe
what was actually demonstrated. This is documentation of the existing engineering
process, not a new approval requirement or an additional runtime subsystem.

## Stable editing layouts

Transient calculation, pending, error and completion feedback must not add/remove editor
rows or change their width. Use the shared nonmodal bottom-right toast without taking
focus or pointer input. Keep full details in Activity/Issues or operation details.
Reserve scrollbar gutters; use stable, elided rows for changing diagnostic values.
Verify actual field bounds and focus while dragging, not only an idle screenshot.
Deliberate user mode changes may expose controls; background work must not move them.

## Design references

The concrete rules above are AnthroForge project decisions. The following sources
provide supporting design background:

- [Microsoft: architectural principles](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles)
  discusses separation of concerns, explicit dependencies and encapsulated shared rules.
- [Martin Fowler: YAGNI](https://martinfowler.com/bliki/Yagni.html) explains why speculative
  extensibility has a cost while refactoring for easier modification remains valuable.
- [Martin Fowler: Refactoring](https://martinfowler.com/books/refactoring.html) describes
  disciplined design improvement through behavior-preserving transformations.
