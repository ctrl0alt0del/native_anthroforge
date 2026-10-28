# Exterior query adapter

The adapter stages libigl's `copyleft/cgal/outer_hull.cpp` algorithm (Alec Jacobson,
2015, MPL-2.0; source included in the existing vendor snapshot). Exact intersection
remeshing and cell extraction precede conversion back to double precision. Only
faces bordering the ambient cell survive. Per-face source indices remain available;
closure-only faces are filtered by the application-owned query adapter.

CGAL 6.1.1 and Boost 1.89.0 are pinned by URL and SHA256 in CMakeLists.txt. CGAL
uses its Boost exact arithmetic backend; GMP and runtime Blender are not dependencies.
Both packages' original header notices apply. No competing worker pool is enabled.
The libigl `assign_scalar` GMPXX overload guards additionally require CGAL_USE_GMPXX
so the no-GMP configuration works on non-Windows platforms too.

Compiler compatibility corrections (2026-10-22): vendored libigl CGAL headers use
`AABB_traits_3` and `AABB_triangle_primitive_3` and their corresponding headers.
CGAL 6.1.1 defines the old names as aliases of these exact types; geometry behavior
is unchanged. See [CGAL's migration notes](https://www.cgal.org/2024/09/27/cgal60/).
Three unreachable `return false` statements after unconditional throws or a fully
returning/throwing switch were removed from `closest_facet.cpp` and
`extract_cells_single_component.cpp`. Exception and orientation semantics are
unchanged. These corrections retain GCC/MSVC warnings-as-errors; no warning
suppression or numerical algorithm change is introduced.

Cancellation is checked between arrangement stages and during output construction.
A running exact intersection-remeshing call completes before observing cancellation.
The query mesh is transient, cached with bounded retained-resource accounting, and
never replaces authored, displayed, serialized or material-reference geometry.

0.4.2 adds `inspection.cpp`: an AnthroForge-owned, read-only adapter over the pinned
CGAL `Side_of_triangle_mesh` API. Existing suitability checks reject ambiguous volume
inputs before point classification. No new package, Boolean algorithm, production
placement rule or geometry rewrite is introduced. Samples are not whole-mesh containment
certificates. [API assumptions](https://doc.cgal.org/6.1/Polygon_mesh_processing/index.html).
