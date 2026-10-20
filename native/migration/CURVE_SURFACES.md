# Curve surface numerical migration

Captured on 2026-10-19 from the original AnthroForge addon, without changing its files.
`tests/fixtures/surfaces/addon.json` records source paths, SHA-256 hashes and actual
outputs; regenerate using `tools/capture_surface_reference.py ADDON_PATH`.

The C++ adapters port the following production Python calculations:

- `fiber_surface.py`: arclength sampling, row density, closed direction/start alignment,
  loft connectivity, Newell/covariance patch projection, projected intersection checks,
  deterministic ear clipping, shared-edge subdivision, four constrained fairing passes,
  and boundary-last indexing.
- `free_surface.py`: union sampling that retains evaluated path corners and the closed
  alignment score, with bounded station/vertex/triangle counts.
- `free_path.py`: normalized cumulative arclength, used by the captured reference.

All repeated numerical work is C++. Python packs owned path inputs and consumer settings.
The existing primitive loft and new curve loft share native grid connectivity. Native
outputs are drafts, finalized through the existing canonical-topology/render/BVH boundary.
There is no Blender runtime dependency and no production Python fallback.

The adapter uses the boundary-preserving patch variant (inclusive ear containment),
also for uniformly sampled inputs. It stores closed correspondence as authored path
parameters; the application translates those to stable authored-point identities.
Automatic direction/start selection belongs only to creation and explicit Realign.
Automatic transverse density is returned separately for persistence. The addon commonly
recomputed these during evaluation; retaining them is the confirmed product change.
Consumer ranges use normalized arclength. Uniform loft density takes the largest requested
source sample count so rows share a compatible longitudinal grid.

Six captured cases cover uniform/exact open lofts, regular and irregular closed alignment,
and a concave nonplanar patch. Native vertex positions match to absolute 1e-10 and polygon
connectivity matches exactly. Separate checks cover ranges, reversal, cancellation,
budget errors, normal flipping and retained correspondence across deformation.
This evidence does not establish anatomical scene, desktop, branch or release acceptance.

Existing-library research included CGAL's official polygon-mesh hole filling APIs
(`https://doc.cgal.org/latest/Polygon_mesh_processing/index.html`). Those algorithms
do not establish equivalence to the required addon patch; the existing kernel was ported
and checked directly instead of changing the surface construction silently.

## Displayed surface picking

Texture-only D3D11 acceptance exposed two shared query defects: parallel rays on a BVH
slab boundary produced NaNs in the existing libigl box test, and deformed shared edges
could be missed by its ray-triangle test. `src/ray_queries.cpp` keeps the existing
cached libigl tree, handles parallel slabs explicitly, and evaluates triangles with
shared ray-space edge functions following Woop/Benthin/Wald (2013),
https://jcgt.org/published/0002/01/05/ and the PBRT triangle discussion:
https://www.pbr-book.org/4ed/Shapes/Triangle_Meshes . This adapter is independently written;
vendored libigl is unchanged. It does not scan every triangle or perturb the query ray.

Regression fixtures test both ray directions on all three axis planes, before and after
deformation, including sampled boundary vertices. The same native entry point serves
scene picking and surface snapping/projection. Invisible rendering verifies a complete
old mesh and its picking revision remain active until the replacement is displayed.

## Explicit open branches

`surface_branch_inputs.cpp`, `surface_branch_sampling.cpp` and `surface_branches.cpp`
port the addon `core/vcp/branched_surface.py` base surface assembly. The compact fixture
`tests/fixtures/surfaces/branches.json` pins the donor SHA-256 and eight directly captured
outputs (both outer boundaries, both windings, straight/curved root paths). Native
positions agree to 1e-10 and face indices agree exactly, including reused main seam IDs.
No proximity welding, Blender access or Python numerical preparation is involved.

Uniform sampling is an explicit extension: authored junction stations remain included
in the main grid. Cancellation and bounded source/station/mesh sizes remain enforced.
Connector width/fullness are used by later muscle inflation, not this base assembly;
0.2.0 therefore does not expose inert inflation controls. Closed and nested branches
remain unsupported. CGAL's explicit border-stitching API was reviewed as a comparison
(https://doc.cgal.org/5.6/Polygon_mesh_processing/group__PMP__combinatorial__repair__grp.html);
reusing known seam IDs directly preserves the addon construction without a repair pass.

The adaptive-routing repair coalesces station differences below `1e-12` of normalized
length. Two curved boundary-1 donor fixtures therefore lose two duplicate vertices and
their zero-width strips. Original donor captures remain unchanged; tests verify their
canonical nondegenerate geometry and shared seam connectivity. Ordinary exact lofts
retain the union's normalized axes for material attachments. Patch harmonic material
coordinates are additional metadata and do not change the captured patch geometry.
