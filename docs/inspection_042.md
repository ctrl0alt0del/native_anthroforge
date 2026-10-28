# 0.4.2 — operation status and spatial inspection

Implements selected audit items **R01, R02, R03 and R06**. Geometry generation,
attachment capture/deformation, routing, inflation and skin algorithms are unchanged.
All new checks are advisory. No new project schema or automatic repair is introduced.

## Using the tools

- **Inspect → Inspect neighborhood** temporarily shows the selection, upstream construction
  and supports, and direct attachment children. **Restore previous view** restores the earlier
  presentation/camera. Workspace membership, edit permissions and task priorities stay unchanged.
  Relationship changes refresh included objects; deleting the selection restores the prior view.
- **Size & section** displays overall world X/Y/Z extents. Enable **Cross-section** for
  continuous U/V spans along the visibly labeled plane axes. Measurements use accepted surfaces
  and canonical metres, formatted in workspace units. Scale & topology explains edge lengths,
  triangle quality, winding and transform condition.
- **Check geometry** checks SCP/construction surfaces; tissue checks retain existing stages.
  **Skin → Skin diagnostics → Locate geometry findings** checks accepted skin. Issues can locate
  a stage/revision-specific witness. Checks are on demand; changes stale previous findings.
- **Inside another surface** compares at most 512 deterministic source vertices with a qualified
  closed exterior volume. It reports inside/boundary/outside counts and the deepest inside sample.
  Open, intersecting, nested or invalid volumes return an unavailable reason. Samples do not prove
  whole-surface containment, and distances do not measure a minimum separating translation.
- **Placement & support → Explain placement at a surface** compares production preview and
  confirmed queries at a click. It shows requested/hit/accepted positions, displacement, material
  face IDs, surface role/revision and approach relative to the face normal. Select a bound point
  to inspect its existing support and offset without recapturing it. This is a current query,
  not reconstruction of the original gesture. Local normal evidence does not guarantee a global
  exit direction through folded geometry. Locate the support, review existing Fiber pin repairs,
  inspect ROUTED evidence and follow loft consumers through Relationships & attachments.
- **Export inspection report** freezes findings, measurements, section clipping, placement/volume
  witnesses and neighborhood camera/filter with the source revision. Refresh stale evidence first.
  The image and JSON share frozen inputs while the live document can continue changing.

Replace imported mesh and Change tissue source use the same readiness assessment in desktop
actions and application guards, including candidate application. Existing topology/transform/
workspace policies remain authoritative; presentation-only visibility gains no parallel manager.

## Ownership and limits

`operation_status` supplies immutable eligibility; replacement producers retain compatibility
and review. `inspection_surfaces` describes accepted geometry/frame/roles/revision without dummy
SCPs. `spatial_evidence` validates witnesses. Query strategies plug into the existing read-only
inspection jobs, coordinator, dispatch capture, cancellation and publication guards. No second
scheduler or idle polling timer was added. Enabled measurements debounce changes and cache stable
projections. Placement and volume checks require explicit actions.

C++ owns metric loops, triangle/plane queries, placement and volume classification. Volume checks
reuse native Boolean suitability predicates and pinned CGAL 6.1.1 `Side_of_triangle_mesh`; they
never replace anatomy with a cleaned mesh. CGAL bulk qualification has cancellation checkpoints
around stages; per-sample queries check cancellation. Immediate interruption of each CGAL call is
not guaranteed. [CGAL documents the closed-volume assumptions](https://doc.cgal.org/6.1/Polygon_mesh_processing/index.html).

Crossing checks retain exclusions for touching/coplanar contact and stop at 512 findings. Section
contours stop at 32,768 points and label truncated spans. No clean report certifies anatomy,
physical contact, global containment or skin quality. Existing provider names and the
`tissue.inspect.cancel` adapter remain compatible with the shared inspection service.

## Qualification

See the [task record](tasks/inspection-workflows-042.md). Reproducible tools are
`tools/check_inspection_042.py`, `tools/profile_inspection_042.py` and
`tools/spatial_inspection_portable.py`; artifacts belong under `build/inspection-042`.

The 58-SCP/96-tissue assembly was inspected with its document and bindings unchanged. One profiled
run with other checks active measured 0.23–0.35 ms per native dimension query, 0.18–0.23 ms per
section query, 0.11–0.20 ms per placement pass and 6.15 ms for sampled volume classification.
Whole requests took 9–34 ms including orchestration. These are single observations, not statistical
benchmarks or physical input/display latency claims. GUI checks are background/offscreen and do
not establish interactive desktop acceptance.
