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
parameters; the application will translate those to stable authored-point identities.
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
