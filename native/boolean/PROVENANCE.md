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

Cancellation is checked between arrangement stages and during output construction.
A running exact intersection-remeshing call completes before observing cancellation.
The query mesh is transient, cached with bounded retained-resource accounting, and
never replaces authored, displayed, serialized or material-reference geometry.
