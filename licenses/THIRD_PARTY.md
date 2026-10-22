# Runtime and source notices

AnthroForge authored sources are GPL-3.0-or-later; see LICENSE. The Blender attachment
kernel is preserved in native/migration/attachment_wave_reference.hpp. Its origin and
qualification are recorded in docs/development_status.md. No Blender executable is
required or bundled.

Release 0.2.1 adds authored immutable-scene ownership/cache adapters around the existing
routing kernel. No upstream routing numerical source was replaced and no dependency was
added. Existing source hashes and attribution in `native/migration/routing/sources.json`
remain applicable; corresponding adapters are included in the 0.2.1 source archive.

Blender 5.0.1 primitive/deformer algorithms are adapted in the native library.
Their original NaN Holding BV and Blender Authors attribution, source paths and hashes
are recorded in [primitive provenance](../native/migration/BLENDER_PRIMITIVES.md).
Upstream GPL-2.0-or-later algorithms are distributed here under GPL-3.0-or-later;
both license texts and corresponding adapted sources accompany the release.
Initial generated-quad tessellation also adapts Blender 5.0.1's degenerate-diagonal
test in `mesh_tessellate.cc` / `math_geom.cc`, attributed to NaN Holding BV and
Blender Authors under GPL-2.0-or-later; the adaptation is GPL-3.0-or-later.

| Component | Version/source | License and source |
| --- | --- | --- |
| CPython | 3.12.12 | PSF and bundled notices in CPython-LICENSE.txt; https://www.python.org/downloads/release/python-31212/ |
| NumPy | 1.26.4 | BSD and bundled dependency notices copied from its installed distribution; https://github.com/numpy/numpy/releases/tag/v1.26.4 |
| Pillow | 12.3.0 | MIT-CMU and bundled codec notices copied from its installed distribution; https://github.com/python-pillow/Pillow |
| PySide6/Shiboken | 6.12.0 | LGPL-3.0 / GPL alternatives recorded in wheel metadata; https://download.qt.io/official_releases/QtForPython/ |
| Qt | 6.12.0 | GPL/LGPL and component-specific notices; https://doc.qt.io/qt-6/licensing.html |
| Eigen/libigl | Vendored addon snapshots | MPL-2.0 and original header notices; source is included under native/vendor |
| CGAL | 6.1.1 | GPL-3.0-or-later/LGPL-3.0-or-later per-header notices; exact arrangement adapter under native/boolean; pinned source and hashes in its CMakeLists.txt |
| Boost | 1.89.0 | Boost Software License 1.0; header-only exact arithmetic, pinned source and hashes in native/boolean/CMakeLists.txt |
| happly | Snapshot hash in native/vendor/PROVENANCE.md | MIT; included source and license |
| earcut.hpp | 2.2.4 | ISC; included source and license |
| curve_fit_nd | Blender 5.0.1, unchanged sources | BSD-3-Clause, DWANGO Co., Ltd.; full notice in native/vendor/curve_fit_nd/curve_fit_nd.h and CURVE-FIT-LICENSE.txt |
| Radial unit icospheres | Blender 5.0.1 bmesh output | Generated unit templates under native/migration/tissue; capture/version/hash recorded in unit_spheres.json; AnthroForge GPL-3.0-or-later adapter |
| PCG64 and bounded integer distribution | NumPy 1.26.4 | MIT, Melissa O'Neill, Robert Kern and NumPy Developers; native/vendor/numpy_random/pcg64.h and LICENSE.txt; adapter provenance in native/vendor/numpy_random/PROVENANCE.md |
| Nuitka | 4.1.1 build/runtime support | Apache-2.0; https://nuitka.net/pages/overview.html |

Qt source archives for the pinned SDK are available at
https://download.qt.io/online/qtsdkrepository/all_os/qt/qt6_6120_windows_line_endings_src/qt.qt6.6120/.
Qt for Python component notices: https://doc.qt.io/qtforpython-6/licenses.html.
The release keeps Qt shared libraries dynamically replaceable and includes the matching SDK
SBOM files when available. Upstream commercial-license text included in a wheel is
retained as upstream metadata; this application uses the open-source license alternatives.

The 0.1.4 `af_profiler` adapter links Qt 6.12.0's private QmlDebug and PacketProtocol
client support statically; the surrounding Qt runtime remains shared. This is an
isolated, version-pinned integration under the GPL-compatible Qt licensing terms.
Matching Qt source is available from the pinned SDK source location above, including
`qtdeclarative/src/qmldebug` and `qtdeclarative/src/plugins/qmltooling`. The authored
adapter source/build instructions are included in the companion source archive.
It enables profiling services only; debugger and inspector services are excluded.

The companion source archive includes application/native sources, pinned dependency
lockfile, tests, build scripts and unchanged vendored headers. The portable runtime
contains Windows redistributable runtime DLLs selected by Nuitka. These components
retain their original licenses; the application license does not replace them.

PIQP 0.6.4 (PREDICT-EPFL, BSD-2-Clause) supplies native constrained tissue field solves
and the optional sparse ROUTED quadratic-subproblem backend.
See `PIQP-LICENSE`, `PIQP-LDL-LICENSE` and native/vendor/PROVENANCE.md. Complete pinned
headers, addon numerical adapters and their provenance ship in the companion source archive.
