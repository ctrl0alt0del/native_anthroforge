# Automatic skin pipeline — Draft and Final modes

**Status: Implemented and qualified; see the evidence and limits below.**

Confirmed by the user on **2026-11-27** after the refinement and grilling interview
through Q30. This document is the durable specification of that agreement. The requirements
do not select a new numerical algorithm or assign a release number. Concrete schema mapping,
implementation evidence and qualification limits are recorded in the documents below.

The [existing skin specification](specification_040.md), [skin workflow](skin_workflow.md),
[application architecture](architecture.md) and
[engineering guidelines](engineering_guidelines.md) remain applicable except where the
explicit changes below supersede their earlier behavior. The
[documentation task record](tasks/skin-pipeline-spec.md) records the original specification
delivery. [Implementation qualification](skin_pipeline_validation.md) maps all acceptance
cases to executable evidence; the [implementation record](tasks/skin-pipeline.md) tracks integration.

## 1. Outcome, scope and terminology

An author chooses which skin result should follow the main anatomy:

- **Draft mode:** committed SCP/VCP changes cause background draft construction.
- **Final mode:** compatible changes deform final skin while preserving its topology.
  The pipeline automatically performs prerequisite construction when it is explicitly
  required to obtain a valid final result.

The switch selects the **requested result**, not the stage currently executing.
Draft construction may therefore run inside Final mode as required prerequisite work.
It does not make both pipelines update continuously.

Scope is the **main accepted anatomy**. Editable variants, candidate skeleton replacement
previews and other temporary candidate contexts are excluded from this feature. Existing
context isolation remains mandatory. Desktop and headless clients use the same application
operations and policies.

| Term | Meaning in this specification |
| --- | --- |
| SCP/VCP source | A physical SCP or finished TissueVCP contributor, including supported reflected instances. Builders can require additional source roles, such as VCP base correspondence. |
| Draft | The accepted constructed envelope surface, before skin topology/reference stages. |
| Topology | The retained constructed skin mesh and its vertex/connectivity identity. |
| Reference | The immutable deformation data and anatomical correspondence needed for compatible final updates. |
| Final | The accepted deformation result; ordinary updates change positions while preserving connectivity. |
| Applied configuration | The builder selection/configuration associated with an accepted successful draft build. |
| Pending configuration | Authored builder parameter edits that have not yet been applied successfully. |
| Requested mode | Saved user intent: Draft or Final. It is distinct from a transient execution phase. |
| Required work | A structured stage assessment identifying a missing or incompatible prerequisite. It is distinct from a numerical failure. |

Selection, display visibility and a narrow workspace do not remove physical contributors.
Bare Fibers and other construction objects are not substitutes for finished VCP volume.
Guides for topology remain separate from draft physical inputs.

### Diagram 01 — Feature map (mind map)

~~~mermaid
mindmap
  root((Automatic skin pipeline))
    Requested output
      Draft
        Committed edits
        Background catch-up
      Final
        Compatible vertex updates
        Required prerequisite repair
    Builder specialization
      FIELD
        Own settings and inputs
      AVBD
        Own settings and reuse
    Configuration
      Pending values
      Applied snapshot
    Lifecycle
      Revision checks
      Undo and save
      Retain accepted output
    Presentation
      Mode follows user intent
      Actual running stage is visible
~~~

### Diagram 02 — System context (C4 context)

~~~mermaid
C4Context
    title Skin authoring context
    Person(author, "Anatomy author", "Edits SCPs and VCPs; selects Draft or Final")
    System(skin, "AnthroForge skin pipeline", "Shared application operations, planning and execution")
    System_Ext(workers, "Native worker processes", "Owned numerical construction and deformation")
    System_Ext(files, "Project files", "Authored settings and accepted results")
    Rel(author, skin, "Desktop controls")
    Rel(skin, files, "Saves and restores")
    Rel(skin, workers, "Runs calculations")
    UpdateRelStyle(author, skin, "#444", "#666", "0", "-25")
    UpdateRelStyle(skin, files, "#444", "#666", "40", "0")
    UpdateRelStyle(skin, workers, "#444", "#666", "-45", "-20")
    UpdateLayoutConfig("2", "1")
~~~

The context drawing shows integration boundaries; it does not introduce a service,
network protocol, external worker vendor or new deployment requirement.

## 2. Normative behavior

“MUST” identifies an acceptance requirement. Stage names and model names used in
diagrams describe responsibilities; they are not mandated class names or command spellings.

| ID | Requirement |
| --- | --- |
| SKP-01 | Main anatomy MUST use one saved, exclusive requested mode: Draft or Final. |
| SKP-02 | New projects and projects without a saved mode MUST default to Draft. |
| SKP-03 | In Draft mode, committed source add/update/remove operations MUST request background catch-up after required source calculations are ready. No real-time draft target is imposed. |
| SKP-04 | The first eligible automatic build MUST use the selected builder and its current initial configuration, without a preliminary manual build. |
| SKP-05 | Opening a project MUST restore saved state without blanket skin recalculation; the next eligible committed edit can trigger catch-up. |
| SKP-06 | Automatic draft jobs MUST NOT be user-cancelable in either mode; Draft mode MUST offer no separate Pause or Disable control. |
| SKP-07 | Final mode MUST normally preserve draft, topology and reference while compatible changes update final positions. |
| SKP-08 | Final scheduling MUST respect the existing project Live, On Release and Manual timing rules and upstream source readiness. |
| SKP-09 | Selecting Final MUST wait for draft catch-up to current committed anatomy before the downstream handoff. |
| SKP-10 | Selecting Draft MUST stop pending final updates, reject late final publication and catch draft up with intervening changes. |
| SKP-11 | A Final request MUST automatically obtain explicitly required prerequisites, including draft, topology and reference rebuilding where necessary. |
| SKP-12 | Required prerequisite construction MUST preserve the requested Final mode and retain the previous accepted final until replacement is ready. |
| SKP-13 | Topology/reference MUST be replaced automatically when a stage's compatibility contract requires it; ordinary compatible updates MUST preserve topology identity. |
| SKP-14 | Stage assessments MUST distinguish required work, unsupported/blocked inputs, obsolete work and computation failure. A numerical failure alone MUST NOT trigger a full rebuild. |
| SKP-15 | FIELD and AVBD MUST participate through the shared pipeline while owning their own settings, validation, required inputs, invalidation dependencies and reuse rules. |
| SKP-16 | Legacy FIELD collagen/gap parameters MUST NOT be imposed on other builders through shared models, validation, capture or dependency signatures. |
| SKP-17 | After initial construction, builder parameter edits MUST remain pending until an explicit draft rebuild succeeds; automatic work MUST use the applied configuration. |
| SKP-18 | Successful explicit rebuilding MUST promote its captured configuration with its accepted draft. Failure MUST retain the prior applied configuration and result. |
| SKP-19 | Failure MUST preserve accepted results and diagnostics. Retry requires changed effective inputs or explicit Retry; the same failed inputs MUST NOT loop indefinitely. |
| SKP-20 | AUTO display MUST follow requested mode while preserving explicit stage selection, hidden-skin state and independent fit previews. |
| SKP-21 | Removing the last contributor MUST hide the current draft and show “No contributing anatomy,” while retaining resources required by undo. |
| SKP-22 | One skin-domain planner MUST own target planning; the existing task coordinator MUST retain execution and lifecycle authority. |
| SKP-23 | Workers MUST use owned input snapshots. Publication MUST validate relevant revisions, context and requested-mode intent before accepting a result. |
| SKP-24 | Automatic work MUST preserve established undo/redo, save/checkpoint, project-switch and resource-lifetime contracts. |
| SKP-25 | Fit snapshots MUST remain retained; replaced construction MUST mark affected fits outdated. Final-only, frozen-revision export contracts MUST remain intact. |
| SKP-26 | Builder-specific incremental reuse MUST be compatibility checked and must preserve that builder's geometry and diagnostic contracts. |
| SKP-27 | Read-only status queries and notifications MUST NOT themselves start computation, mutate authored state or create history. |
| SKP-28 | No generic or client-specific path may bypass these mode, configuration, cancellation and publication rules. |

## 3. User control and mode transitions

There is one checkbox or two-position switch with unambiguous meaning:
**off = Draft**, **on = Final**. The exact UI label is a presentation choice; it must
communicate exclusive modes. It must not imply that checking it continuously updates
both draft and final skin.

The requested mode is saved per project. A change of mode uses the application's shared
document operation and normal undo semantics. Effective mode, operation phase and
readiness are reported separately.

| Requested mode / event | Required behavior |
| --- | --- |
| Draft; first usable contributor becomes ready | Request the initial draft automatically. |
| Draft; source edit commits | Wait for required source results, then catch up. Do not follow every drag sample. |
| Final; compatible anatomy changes | Request position updates according to project timing. |
| Final; prerequisite is explicitly invalid/missing | Request the required producer stages automatically; remain in Final. |
| Draft → Final | Wait for current draft catch-up, then assess and execute required downstream stages. |
| Final → Draft | Stop final work and reject its late results; catch draft up automatically. |
| Project opens | Restore saved results/configuration/mode; do not treat loading as an edit. |
| No physical contributors | Expose the empty-anatomy state and hide current draft presentation. |
| Unsupported builder/source capability | Keep requested mode and accepted output; explain the specific blocked capability. |

### Diagram 03 — Requested mode (state diagram)

~~~mermaid
stateDiagram-v2
    state "Draft mode" as Draft
    state "Final mode" as Final
    [*] --> Draft: New project or absent saved mode
    Draft --> Final: Select Final
    Final --> Draft: Select Draft
    Draft --> Draft: Commit source changes
    Final --> Final: Compatible update or required repair
~~~

### 3.1 Timing and readiness

The mode switch chooses the requested result. Existing update modes still govern
when final evaluation is allowed:

| Project Update mode | Final behavior |
| --- | --- |
| Live | Compatible final updates can run during interaction. |
| On Release | Automatic final evaluation waits for release. |
| Manual | Final evaluation requires the existing explicit evaluation/recalculation request. |

An explicit selection of Final requests the mode transition and required initial
downstream work; subsequent anatomy-driven updates follow the table. It does not force
upstream sources that are intentionally held in Manual mode to calculate behind the
user's back. Required source readiness and the existing explicit recalculation workflow
remain visible.

There is no promised frame rate, latency budget or geometry approximation for Draft.
Final mode retains the existing interactive deformation behavior; this document makes
no new measured performance claim.

### 3.2 Handoff consistency

The downstream handoff must use a coherent combination of draft, source identities,
anatomy revisions and applied builder configuration. The existence of an envelope asset
alone is not proof that it represents the intended handoff inputs.

If committed inputs change while waiting or computing, obsolete work cannot publish
as the new current result. The planner reassesses the current requested target through
the coordinator's existing coalescing and revision mechanisms. A mode transition must
not mix an old draft with incompatible new construction inputs.

Pending builder parameter edits do not become applied merely because the user selects
Final or a Final request needs an automatic draft repair.

### Diagram 04 — Execution phase, separate from requested mode (state diagram)

~~~mermaid
stateDiagram-v2
    [*] --> Assess
    Assess --> Current: Reusable target
    Assess --> Waiting: Source or draft not ready
    Assess --> Running: Ready
    Assess --> Blocked: Unsupported
    Waiting --> Assess: Input ready
    Running --> Validate: Result returned
    Validate --> Current: Target accepted
    Validate --> Assess: More stages or obsolete result
    Running --> Failed: Failure
    Current --> Assess: Input or mode changed
    Blocked --> Assess: Changed input or Retry
    Failed --> Assess: Changed input or Retry
~~~

The diagram does not add a second scheduler. Waiting, running and publication continue
to use the shared coordinator and existing context/job lifecycle. A blocked or failed
phase is not a polling loop.

## 4. Pipeline planning and required work

The normal fast path in Final mode is **deformation only**. An input change does not
automatically invalidate every construction stage.

Each stage assesses whether its accepted result or prerequisites remain suitable for
the current operation. That assessment must be specific enough to explain required work.
Examples include changed contributor identity, lost material correspondence, incompatible
topology/reference, unavailable builder capability, or incompatible applied settings.

The planner requests the required producer work, accepts only validated results,
and then reassesses the requested target. It reuses results that remain compatible.
It must not infer a recovery path by parsing exception text, blindly retrying the same
stage, or rebuilding the entire chain after every numerical error.

### Diagram 05 — Stage dependency graph (data-flow diagram)

~~~mermaid
flowchart LR
    A["Accepted SCP / VCP surfaces"] --> D["Draft surface"]
    C["Applied builder configuration"] --> D
    D --> T["Skin topology"]
    G["Guides and topology settings"] --> T
    T --> R["Deformation reference"]
    D --> R
    S["Anatomical support and correspondence"] --> R
    R --> F["Final positions"]
    U["Current compatible source state"] --> F
    F --> V["Display / fitting / frozen export"]
~~~

Arrows describe construction/input relationships, not an unconditional “recompute
everything downstream” rule. A frozen draft and retained reference can remain valid for
compatible Final-mode position updates. Purpose-specific compatibility determines reuse.

### Diagram 06 — Target planning (activity / decision flow)

~~~mermaid
flowchart TD
    E["Edit, mode request, accepted result or Retry"] --> P["Assess requested target"]
    P --> K{"Assessment"}
    K -->|"Already valid"| O["Keep accepted result"]
    K -->|"Ready to compute"| J["Submit stage through coordinator"]
    K -->|"Requires prerequisites"| N["Resolve required producer plan"]
    N --> J
    K -->|"Unsupported / unavailable"| B["Blocked with specific reason"]
    J --> X["Capture and execute owned inputs"]
    X --> Y{"Outcome"}
    Y -->|"Validated current result"| A["Accept result"]
    A --> P
    Y -->|"Obsolete"| P
    Y -->|"Numerical failure"| F["Retain accepted result; report failure"]
    B -->|"Changed inputs or explicit Retry"| P
    F -->|"Changed inputs or explicit Retry"| P
~~~

The set of permitted stage dependencies must be explicit and acyclic for a particular
request. An assessment that cannot make progress must produce a blocked reason rather
than resubmitting identical work indefinitely. Mode changes and revision changes cause
reassessment of the target, not unconditional retries of the formerly requested stage.

### 4.1 Required repair in Final mode

When the Final pipeline explicitly requires draft rebuilding, the planner triggers it
automatically. The user is not required to turn the switch off and on.

If compatibility also requires replacing topology and reference, those stages run
automatically. Their new vertex identities are permitted for this reconstruction path.
Ordinary compatible deformation still preserves vertex identities and connectivity.

During repair:

- The requested mode stays Final.
- The last completed final remains visible until its replacement is accepted.
- Previously accepted results and valid retry intermediates remain owned and recoverable.
- Existing fitted snapshots remain retained and are marked outdated when their construction
  is replaced.
- A failed calculation remains a failure. It does not, by itself, prove that more
  upstream rebuilding would fix the problem.
- Repair uses the applied builder configuration. It does not silently apply pending
  parameter changes.

Reference-only reuse must have a valid contract for the retained geometry and current
sources. The current operation that reconstructs a reference from stored topology is
not automatically equivalent to “rebind the currently deformed final shape.” Any such
capability must be explicit and qualified before the planner relies on it.

### Diagram 07 — Background draft update (sequence diagram)

~~~mermaid
sequenceDiagram
    actor Author
    participant App as Shared operation
    participant Sources as Source calculations
    participant Planner as Skin planner
    participant Coordinator as Task coordinator
    participant Builder as Selected draft builder
    participant Store as Accepted results
    Author->>App: Commit SCP / VCP edit
    App->>Sources: Existing source update workflow
    Sources-->>Planner: Required accepted inputs available
    Planner->>Coordinator: Request Draft target work
    Coordinator->>Builder: Owned snapshot and applied configuration
    Builder-->>Coordinator: Surface and provenance
    alt Inputs and requested mode still permit publication
        Coordinator->>Store: Accept draft
        Store-->>Planner: Accepted-result notification
    else Obsolete work
        Coordinator-->>Planner: Reject and reassess latest target
    end
~~~

### Diagram 08 — Entering Final mode (sequence diagram)

~~~mermaid
sequenceDiagram
    actor Author
    participant Planner as Skin planner
    participant Coordinator as Task coordinator
    participant Draft as Draft builder
    participant Stages as Topology / reference stages
    participant Store as Accepted results
    Author->>Planner: Request Final mode
    Note over Planner,Store: Final remains selected. Previous accepted output stays visible.
    opt Draft behind current committed inputs
        Planner->>Coordinator: Request draft catch-up
        Coordinator->>Draft: Build matching applied inputs
        Draft-->>Coordinator: Draft result
        Coordinator->>Store: Validate and accept matching draft
    end
    Planner->>Planner: Assess downstream requirements
    Planner->>Coordinator: Request required downstream stages
    Coordinator->>Stages: Capture coherent handoff inputs
    Stages-->>Coordinator: Topology / reference / final candidates
    Coordinator->>Store: Publish valid accepted replacement
~~~

### Diagram 09 — Final fast path and prerequisite repair (sequence diagram)

~~~mermaid
sequenceDiagram
    participant Inputs as Eligible anatomy update
    participant Planner as Skin planner
    participant Stage as Stage assessment
    participant Coordinator as Task coordinator
    participant Worker as Numerical workers
    participant Store as Accepted results
    Inputs->>Planner: Request Final target
    Planner->>Stage: Assess compatibility
    alt Compatible reference and topology
        Stage-->>Planner: Ready for deformation
        Planner->>Coordinator: Request final positions
        Coordinator->>Worker: Deform against retained reference
        Worker-->>Coordinator: Positions with retained connectivity
    else Explicit prerequisite requirement
        Stage-->>Planner: Requires draft, topology or reference work
        Planner->>Coordinator: Request required producer stages
        Coordinator->>Worker: Execute qualified stage plan
        Worker-->>Coordinator: Owned prerequisite and final results
    end
    Coordinator->>Store: Validate current target and accept
    Note over Planner,Store: Final remains selected throughout repair
~~~

### Diagram 10 — Returning to Draft during final work (sequence diagram)

~~~mermaid
sequenceDiagram
    actor Author
    participant Planner as Skin planner
    participant Coordinator as Task coordinator
    participant Final as Final worker
    participant Draft as Draft builder
    participant Store as Accepted results
    Author->>Planner: Request Draft mode
    Planner->>Coordinator: Invalidate pending final target work
    Coordinator-->>Final: Lifecycle stop / obsolescence
    Final-->>Coordinator: Possible late result
    Coordinator->>Coordinator: Reject obsolete final publication
    Planner->>Coordinator: Request current draft catch-up
    Coordinator->>Draft: Owned current inputs
    Draft-->>Coordinator: Draft candidate
    Coordinator->>Store: Validate and accept draft
    Note over Store: Previous accepted resources remain available for undo
~~~

Internal supersession, undo, project shutdown and mode invalidation are lifecycle controls.
They are distinct from a user Cancel command for an automatic draft job.

## 5. Architecture and ownership

The feature uses a **skin-domain planner with the existing computation coordinator**.

| Responsibility | Owner |
| --- | --- |
| Requested mode, target planning and required stage selection | Skin-domain planner |
| Stage suitability, required inputs, supported repair and reuse assessment | Owning stage contract |
| FIELD/AVBD parameters, input requirements, validation, construction and compatible checkpoints | Selected draft builder |
| Dispatch, coalescing, reservations, resource admission, internal cancellation and publication lifecycle | Existing task coordinator and its shared services |
| Durable authored state and accepted resources | Document/application resource owners |
| Display and controls | Desktop adapter using shared operations and status |
| Numerical iteration and geometry computation | Existing native numerical boundaries |

A missing producer is not created merely by listing a prerequisite port. The domain
planner must request that producer through the shared application execution path.
Adjacent source pipelines already provide examples of requesting provider stages before
their consumers.

The planner has a bounded responsibility. It does not introduce its own queue, worker
pool, timer, cancellation system or alternate publication path. Generic coordinator
code must not accumulate FIELD/AVBD parameter or anatomy-specific branching.

The architecture follows declared-dependency evaluation: a target requests the
prerequisites it needs and can resume when they are available. [Skyframe's primary
documentation](https://bazel.build/reference/skyframe) illustrates this principle.
This is a design reference, not a requirement to adopt Bazel or reproduce its runtime.

### Diagram 11 — Responsibility boundaries (component diagram)

~~~mermaid
flowchart TB
    UI["Desktop controls"] --> API["Shared skin operations"]
    CLI["CLI / API clients"] --> API
    API --> P["Skin pipeline planner"]
    P <-->|"Assess requirements"| AS["Stage contracts"]
    P --> TC["Existing task coordinator"]
    TC -->|"Dispatch"| ST["Builder and stage strategies"]
    ST -->|"Owned native results"| TC
    TC --> R["Owned accepted resources"]
    R -.->|"Accepted-result event"| P
    R --> V["Read-only status and presentation"]
    subgraph Domain["Skin domain decisions"]
        P
        AS
    end
    subgraph Shared["Shared lifecycle authority"]
        TC
        R
    end
~~~

### 5.1 Structured stage assessments

The interface must convey these semantic outcomes without depending on user-facing
message text. The names below are illustrative contract categories.

| Outcome | Meaning | Planner response |
| --- | --- | --- |
| Reusable | Accepted result satisfies this request. | Reuse it; continue assessment. |
| Ready | Required inputs are available and computation is appropriate. | Submit ordinary stage work. |
| Requires work | A specific prerequisite must be produced/replaced. | Request that producer and reassess. |
| Waiting | An eligible source producer is already pending. | Wait through the shared lifecycle. |
| Blocked / unsupported | A capability or valid input is unavailable. | Report the owning source/stage and reason. |
| Obsolete | The captured request no longer matches current allowed intent. | Reject output and assess the current target. |
| Failed | Numerical or execution failure occurred. | Retain accepted output and follow Retry policy. |

Contracts include ownership, coordinate frame, source identity/order, revision footprint,
builder/solver version, configuration provenance and supported output semantics.
A changed producer plan that alters outputs/reservations requires a new valid job request;
renewing only a read list is not sufficient.

### Diagram 12 — Builder specialization (UML class / realization diagram)

~~~mermaid
classDiagram
    class DraftBuilder {
        <<interface>>
        describeInputs()
        validateConfiguration()
        assessReuse()
        buildOwnedSurface()
    }
    class FieldBuilder
    class AvbdBuilder
    class FieldConfiguration
    class AvbdConfiguration
    class FieldReusePolicy
    class AvbdCheckpointPolicy
    class OwnedDraftSurface
    class DraftStage
    DraftBuilder <|.. FieldBuilder
    DraftBuilder <|.. AvbdBuilder
    FieldBuilder *-- FieldConfiguration : owns
    AvbdBuilder *-- AvbdConfiguration : owns
    FieldBuilder *-- FieldReusePolicy : owns
    AvbdBuilder *-- AvbdCheckpointPolicy : owns
    DraftStage --> DraftBuilder : selected strategy
    DraftBuilder --> OwnedDraftSurface : returns
    note for DraftBuilder "Conceptual contract; composition or protocols are sufficient."
    note for FieldConfiguration "Collagen and gap controls belong here."
~~~

The realization arrows describe interchangeable contracts. They do not mandate a Python
inheritance hierarchy. A protocol, registered strategy or small set of callables may
provide the boundary. Numerical construction remains native.

### Diagram 13 — Stage specialization and planning (UML class diagram)

~~~mermaid
classDiagram
    class StageContract {
        <<interface>>
        assessTarget()
        describeInputs()
        executeOwnedSnapshot()
    }
    class DraftStage
    class TopologyStage
    class ReferenceStage
    class DeformationStage
    class StageAssessment {
        outcome
        requiredStages
        reason
        provenance
    }
    class SkinPipelinePlanner {
        requestedMode
        planTarget()
    }
    class TaskCoordinator {
        submit()
        validatePublication()
    }
    StageContract <|.. DraftStage
    StageContract <|.. TopologyStage
    StageContract <|.. ReferenceStage
    StageContract <|.. DeformationStage
    StageContract --> StageAssessment
    SkinPipelinePlanner --> StageContract : assesses
    SkinPipelinePlanner --> TaskCoordinator : submits ordinary jobs
~~~

## 6. Builder configuration and specialization

Builder selection and builder-owned configuration must be represented coherently across
model, serialization, commands, validation, source capture, dependencies and presentation.

FIELD collagen/gap values must not be required, validated as active settings, captured as
numerical inputs, or included in AVBD invalidation merely because they occupy shared
legacy fields. Conversely, AVBD-specific route/material/checkpoint requirements must
not be applied to FIELD. Shared metadata is limited to genuinely shared lifecycle and
accepted-surface contracts.

Per-contributor settings follow the same ownership rule. Hiding a control is insufficient
if generic commands, persistence or invalidation still treat its value as an active input.
Inactive builder configurations can remain retained without influencing another builder.

The selected builder owns the exact source roles it requires. For example, an AVBD
construction may need a VCP base/final correspondence pair even though the finished VCP
is the physical contributor. The application resolves the declared sources from one
consistent snapshot. Unsupported combinations produce a specific capability reason.

### 6.1 Pending and applied values

After an initial accepted draft exists:

1. Editing a builder parameter changes authored pending state.
2. It does not automatically apply that parameter or rebuild the draft.
3. Automatic anatomy-driven work uses the applied builder configuration.
4. An explicit draft rebuild captures the pending configuration for that request.
5. A successful build promotes that captured configuration with its accepted draft.
6. Failure preserves the prior accepted draft and applied configuration; edited values
   remain pending.

Later edits made while an explicit rebuild is running remain distinguishable from
the configuration captured by that request. They cannot be silently included in its
accepted result.

For the first automatic construction, the request captures the selected builder and
current parameters as its initial configuration. No preliminary manual build is needed.
The same owned-snapshot and successful-publication rules apply.

A mode switch or an automatic prerequisite repair is not an explicit application of
pending builder parameters. Builder-selection compatibility and retained producer
provenance must likewise remain explicit.

### Diagram 14 — Configuration application (state diagram)

~~~mermaid
stateDiagram-v2
    [*] --> Initial: No accepted draft configuration
    Initial --> InitialBuild: First eligible automatic request
    InitialBuild --> Applied: Success with no later edits
    InitialBuild --> Pending: Success with later edits pending
    InitialBuild --> InitialFailed: Failure
    InitialFailed --> InitialBuild: Changed effective inputs or explicit Retry
    Applied --> Pending: Edit builder parameters
    Pending --> Pending: Automatic anatomy update uses applied values
    Pending --> Applying: Explicit draft rebuild
    Applying --> Applied: Success with no later edits
    Applying --> Pending: Success with later edits pending
    Applying --> Pending: Failure retains prior applied values
    note right of Applying
        Later authored edits remain pending.
        Promotion concerns the captured request only.
    end note
~~~

### 6.2 Incremental construction

Shared automatic updating does not imply a shared numerical incremental algorithm.

- FIELD can perform the construction strategy its contract supports.
- AVBD owns checkpoint compatibility and ordered construction reuse.
- Reuse must account for effective source inputs, source/mirror identity, traversal order,
  relevant base/final correspondence, applied settings, builder/solver revision and
  retained numerical state.
- A checkpoint must never be accepted merely because it exists or shares a source name.
- Existing AVBD agreement permits only a matching complete prefix, not unqualified
  independent branch reuse. Earlier incompatible changes invalidate the affected suffix.
- Appending a VCP can reuse the combined prefix only when the full prior input prefix
  remains compatible. Other changes require the appropriate skeletal/VCP replay.
- Geometry, diagnostics and supported acceptance semantics must match the qualified
  builder contract. No approximation, new remeshing policy or solver replacement is
  authorized by the orchestration feature alone.

Native checkpoint capability within a single worker run is distinct from application
checkpoint retention and selection across automatic requests. Both must be qualified
before cross-request reuse is claimed.

## 7. State, provenance and persistence

The model must distinguish:

- saved requested mode;
- authored pending builder configuration;
- applied builder configuration;
- accepted draft, topology, reference and final artifacts;
- input/provenance records describing how each artifact was produced;
- transient jobs and operation phases;
- builder-owned reusable checkpoints;
- view-local presentation and independent fitted snapshots.

### Diagram 15 — Logical data ownership (entity relationship diagram)

~~~mermaid
erDiagram
    PROJECT ||--|| MODE_SELECTION : stores
    PROJECT ||--o{ BUILDER_CONFIGURATION : owns
    BUILDER_CONFIGURATION ||--o| APPLIED_SNAPSHOT : promotes
    PROJECT ||--o{ ACCEPTED_ARTIFACT : retains
    APPLIED_SNAPSHOT ||--o{ ACCEPTED_ARTIFACT : identifies_configuration
    ACCEPTED_ARTIFACT ||--|| PROVENANCE : records
    PROVENANCE }o--o{ SOURCE_REVISION : observes
    PROJECT ||--o{ RUNTIME_JOB : temporarily_owns
    RUNTIME_JOB }o--|| MODE_SELECTION : validates_intent
    RUNTIME_JOB }o--o| APPLIED_SNAPSHOT : captures_when_available
    BUILDER_CONFIGURATION ||--o{ BUILDER_CHECKPOINT : scopes
    BUILDER_CHECKPOINT }o--o{ SOURCE_REVISION : validates
    PROJECT ||--o{ FIT_SNAPSHOT : retains
    FIT_SNAPSHOT }o--|| ACCEPTED_ARTIFACT : references_generation
~~~

This is a logical model, not a prescribed database schema or a claim that every artifact
is serialized. An explicit apply/initial-build job can capture a candidate configuration;
it does not mutate the applied snapshot before acceptance.

Persist mode and configuration distinctions with accepted resources through the existing
project lifecycle. Keep ordinary project data, computation checkpoints and transient
jobs distinct. The implementation maps these records to schema 10, with ordinary
`.anthroforge` and extended `.anthroforgex` archives as documented in the
[storage workflow](skin_workflow.md).

Migration must preserve legacy builder settings and accepted assets, default absent mode
to Draft, and avoid computation on open. Implementation must specify and test how legacy
archives without an explicit applied-configuration record are represented. It must not
invent historical producer provenance or discard pending authored values to fill that gap.

Existing save/checkpoint, blocked-save, recovery and extended-checkpoint contracts remain
applicable. An implementation must record the concrete schema mapping and compatibility
tests before it changes persistence.

## 8. Lifecycle, cancellation, failure and publication

Automatic draft work is not user-cancelable. This applies to all user-facing paths,
including generic job controls and headless commands; removing one Cancel button alone
does not satisfy the requirement. There is no separate automatic-draft Pause/Disable
control while Draft mode is selected.

Internal lifecycle control remains necessary: input supersession, undo, mode changes,
context disposal, project replacement and shutdown must prevent obsolete publication
and release resources. Preserve existing behavior for explicitly requested, otherwise
cancelable operations; do not globally disable cancellation for unrelated jobs.

Publication eligibility must cover the captured document/context, relevant input revisions,
applied configuration or explicit candidate configuration, selected/requested-mode intent,
and artifact ownership. A mode-only change cannot leave an old final job free to publish.

Accepted results stay available during work and after failure. Preserve valid intermediates
and the existing pending-topology/reference retry policy where compatible. Replacement
reference/final publication remains coherent; a partial failure cannot overwrite the last
usable final with an incomplete replacement.

Retries follow these rules:

| Cause | Required response |
| --- | --- |
| New effective input or mode invalidates work | Reassess the current requested target; reject obsolete output. |
| Stage explicitly needs a producer | Request that producer through the planner and coordinator. |
| Numerical/execution failure | Report failure and retain accepted output. |
| Same failed effective inputs, no Retry | Do not automatically loop. |
| Explicit Retry | Reassess against current allowed target/configuration. |
| Unsupported capability | Explain the limitation; do not substitute another builder or weaken validation silently. |

Automatic completions must not create independent user undo steps for every accepted
background result. Existing authored-edit grouping, cancel-edit, undo and redo contracts
continue to apply. Undo cannot be undone by a late worker publication.

## 9. Presentation and downstream consumers

AUTO display uses requested mode:

- Draft mode prefers the accepted draft.
- Final mode prefers the usable accepted final.
- During required Final-mode repair, the previous completed final stays visible.
- When no requested result has ever completed, present readiness/progress honestly.
  Any shown intermediate must be identifiable as an intermediate.
- Explicit stage selection, hidden skin and independent fit previews retain precedence.
- Deleting the last physical contributor hides the current draft and shows
  **No contributing anatomy**. Resources needed for undo remain retained.

Status must distinguish requested mode from the actual stage running. For example,
“Final mode — rebuilding required draft” is truthful; flipping the checkbox to Draft
during repair would not be. Labels are illustrative, not mandated UI strings.

Read-only status inspection and notifications cannot become computation triggers.
The shared application operation or an accepted input/lifecycle event requests work.

Existing fits remain independent saved snapshots. Compatible updates preserve final
topology identity. Required replacement construction can change identity; affected fits
become outdated without deleting their snapshots or silently refitting them.

Export remains final-only and tied to its explicitly captured revision. Automatic
background work cannot substitute a later result into an already frozen export request.
The mode switch does not turn a draft-only document into an exportable final.

## 10. Acceptance scenarios and traceability

The tests below are required behavior checks for implementation. Execution evidence is
recorded in [implementation qualification](skin_pipeline_validation.md). Use deterministic scheduling controls
for interleavings and representative numerical fixtures for geometry/reuse qualification.

| Case | Scenario and observable result | Requirements |
| --- | --- | --- |
| AC-01 | Create a project; mode is Draft. First usable source produces draft without a preliminary manual build. | SKP-01–04 |
| AC-02 | Open a legacy/current project; saved output remains and no blanket rebuild starts. The next eligible edit catches up. | SKP-02,05 |
| AC-03 | Commit source add/update/remove operations; draft waits for required geometry and reaches the current accepted inputs. | SKP-03,23 |
| AC-04 | Try user cancellation through desktop and shared commands; automatic draft cannot be cancelled or paused. | SKP-06,28 |
| AC-05 | Select Final while draft is pending; downstream work waits for a coherent matching draft. | SKP-09,23 |
| AC-06 | Move a compatible source in Final mode; positions change while draft/reference/topology identities remain stable. | SKP-07,13 |
| AC-07 | Repeat under Live, On Release and Manual; final scheduling follows the established timing and source-readiness rules. | SKP-08 |
| AC-08 | Switch to Draft during final execution; late final output is rejected and draft catches up. | SKP-10,23 |
| AC-09 | Final assessment requires draft/topology/reference work; it runs automatically without a manual mode cycle. | SKP-11–13 |
| AC-10 | Required repair is running; mode remains Final and old final remains visible until accepted replacement. | SKP-12,20 |
| AC-11 | Numerical solve fails without a prerequisite requirement; retain accepted output and do not launch an arbitrary full rebuild. | SKP-14,19 |
| AC-12 | Add/remove a contributor or change source correspondence; assessment identifies specific valid required work or unsupported capability. | SKP-11,14,23 |
| AC-13 | Apply required topology replacement; old fits remain retained and become outdated. | SKP-13,25 |
| AC-14 | Select AVBD; inactive FIELD collagen/gap edits do not enter its validation, capture or invalidation footprint. | SKP-15,16 |
| AC-15 | Select FIELD; AVBD-only settings and checkpoint validation do not become FIELD requirements. | SKP-15,16 |
| AC-16 | Edit active builder parameters, then edit anatomy; automatic work uses applied values and preserves pending edits. | SKP-17 |
| AC-17 | Explicit parameter rebuild succeeds; captured values and accepted draft promote together. Later edits remain pending. | SKP-18,23 |
| AC-18 | Explicit parameter rebuild fails; previous applied values and draft remain, and edited values stay pending. | SKP-18,19 |
| AC-19 | First construction snapshots current selected-builder values without requiring a manual initialization step. | SKP-04 |
| AC-20 | Keep failed effective inputs unchanged; no repeated failure loop. Change effective inputs or use Retry to reassess. | SKP-19 |
| AC-21 | Use AUTO, explicit stage, hidden skin and fit preview; each follows its specified precedence. | SKP-20 |
| AC-22 | Remove the last contributor, then undo; empty state is clear and recoverable accepted resources are preserved. | SKP-21,24 |
| AC-23 | Undo/redo an edit with queued/running work; automatic publication cannot restore an undone branch or add unrelated undo steps. | SKP-23,24 |
| AC-24 | Save under supported wait/checkpoint/pending policies, reopen and replace projects during work; accepted state remains coherent. | SKP-05,24 |
| AC-25 | Start frozen final export, then edit/change mode; the export keeps its requested revision. Draft alone remains non-exportable. | SKP-25 |
| AC-26 | Compare eligible AVBD prefix reuse with fresh construction; reject incompatible source/order/configuration/version checkpoints. | SKP-26 |
| AC-27 | Poll status and attach UI observers; no job, authored mutation or history step is created by reading. | SKP-27 |
| AC-28 | Submit equivalent requests through desktop and headless operations; mode, settings and publication behavior match. | SKP-22,28 |
| AC-29 | A declared prerequisite has no submitted provider; planner requests it, and shared coordinator owns execution. | SKP-11,22 |
| AC-30 | Modes/inputs change during required repair; reassessment follows current intent and preserves accepted resources. | SKP-12,23,24 |

### Diagram 16 — Requirement verification (requirements diagram)

~~~mermaid
requirementDiagram
    requirement ModeContract {
        id: SKP_01_to_14
        text: "Exclusive target modes and explicit prerequisite repair"
        verifymethod: test
    }
    requirement BuilderBoundary {
        id: SKP_15_18
        text: "Builder-owned settings and successful application"
        verifymethod: test
    }
    requirement LifecycleContract {
        id: SKP_19_28
        text: "Retained results and coordinated publication"
        verifymethod: test
    }
    element ModeScenarios {
        type: "AC-01 through AC-13"
    }
    element ConfigurationScenarios {
        type: "AC-14 through AC-19"
    }
    element LifecycleScenarios {
        type: "AC-20 through AC-30"
    }
    ModeScenarios - verifies -> ModeContract
    ConfigurationScenarios - verifies -> BuilderBoundary
    LifecycleScenarios - verifies -> LifecycleContract
~~~

Diagram groupings are an overview; the acceptance table provides the exact requirement
mapping. Geometry equality, runtime cost, UI behavior and archive compatibility need
their own evidence. Passing schema/diagram checks does not establish feature correctness.

## 11. Existing implementation and integration gaps

The initial refinement inspected the main checkout at d3e1b948. Subsequent interview
fact-finding also inspected the separate **codex/avbd-envelope-cpu** worktree at
b3b92969, including substantial uncommitted integration. Its working files cannot be
reconstructed from that commit alone.

The following records the pre-implementation inspection baseline. The completed changes
and verification of these gaps are documented in [qualification](skin_pipeline_validation.md):

| Observed mechanism | Gap relevant to this feature |
| --- | --- |
| Shared coordinator owns jobs, reservations, revisions, cancellation and publication. | Prerequisite ports wait on submitted jobs; domain code still has to request missing producers. |
| Separate envelope, topology, reference and deformation operations exist. | No existing exclusive target-mode planner or combined downstream-only target policy was found. |
| Fixed-topology deformation handles correspondence-preserving changes. | Membership and correspondence changes require typed assessment and qualified producer work. |
| A reference build can use stored topology. | This is not a general automatic rebind of the currently deformed final shape. |
| Newer worktree registers FIELD and AVBD. | Legacy settings remain coupled through parts of the shared model, commands, capture and invalidation. |
| Newer UI hides some FIELD controls for AVBD. | UI hiding does not establish architectural parameter isolation. |
| AVBD worker checkpoints support consecutive stages within a run. | Application-level retained-prefix selection/catch-up across requests remains distinct work. |
| Accepted output and partial-build retention exist. | Requested-mode and applied/pending-configuration publication guards need integration. |
| Current AUTO prefers available final before topology/draft. | This does not implement the requested mode-driven display behavior. |

Useful existing entry points include
[stage policies](../src/anthroforge/application/skin_stages.py),
[skin jobs](../src/anthroforge/application/skin_jobs.py),
[final updates](../src/anthroforge/application/skin_update_tasks.py),
[compatibility/status](../src/anthroforge/application/skin_status.py),
[source contracts](../src/anthroforge/application/skin_inputs.py),
[task coordinator](../src/anthroforge/application/coordinator.py) and
[tissue phase planning](../src/anthroforge/application/tissue_tasks.py).

Qualification must establish the exact stage-specific compatibility rules, safe repair
paths, migration mapping and checkpoint equivalence. These engineering obligations do
not reopen the confirmed user-visible mode or parameter rules. No implementation should
claim a capability merely because a generic “requires rebuild” outcome can be represented.

## 12. Superseded interview interpretations

| Earlier interpretation | Confirmed replacement |
| --- | --- |
| Draft updates in real time during dragging. | Draft construction catches up after committed edits; no real-time draft requirement. |
| Checking the control adds final updates while draft continues updating normally. | Exclusive requested modes. Draft is ordinarily fixed in Final; explicit prerequisite repair is the exception. |
| Automatic draft runs regardless of requested mode. | Always enabled in Draft mode; requested only when necessary in Final mode. |
| The user can cancel automatic draft and restart on another edit. | Automatic draft builds are not user-cancelable. |
| Invalid final correspondence requires a manual Draft → Final cycle. | The Final pipeline requests required upstream work automatically. |
| Topology can never change after initial construction. | Compatible updates preserve it; explicit compatibility requirements can trigger automatic replacement. |
| Collagen/gap parameters are generic draft parameters. | They belong to FIELD. Each builder owns its own configuration and dependency contract. |

The accepted principles above replace the superseded answers. Earlier examples must not
be used to reintroduce additive updating, user cancellation of automatic draft work or a
mandatory manual recovery cycle.

## 13. Delivery and implementation boundary

The original specification delivery created requirements and diagrams only. The subsequent
implementation adds the shared planner, isolated builder configuration and schema-10
ordinary/extended archive mapping. [Qualification](skin_pipeline_validation.md) records the
implemented acceptance cases, actual desktop/portable checks and numerical limits.

Before implementation is reported complete, qualification must cover the acceptance matrix,
representative resource use, current and legacy archive behavior, actual desktop interaction,
headless parity and relevant packaging boundaries. Use the existing repository checks
appropriate to those changes. A successful diagram render is documentation validation only.

The eight diagram families used here are mind map, C4 context, state, data-flow/component/
activity flowchart, sequence, UML class/specialization, entity relationship and requirement
verification. Mermaid source is embedded beside the governing text so it can be reviewed
and maintained with the specification. Syntax references:
[Mermaid diagram reference](https://mermaid.js.org/intro/syntax-reference),
[class realization/specialization](https://mermaid.js.org/syntax/classDiagram.html),
[state diagrams](https://mermaid.js.org/syntax/stateDiagram.html),
[requirement diagrams](https://mermaid.js.org/syntax/requirementDiagram.html) and the
[official renderer](https://github.com/mermaid-js/mermaid-cli).
