# Runtime and source notices

AnthroForge authored sources are GPL-3.0-or-later; see LICENSE. The Blender attachment
kernel is preserved in native/migration/attachment_wave_reference.hpp. Its origin and
qualification are recorded in docs/development_status.md. No Blender executable is
required or bundled.

Blender 5.0.1 primitive/deformer algorithms are adapted in the native library.
Their original NaN Holding BV and Blender Authors attribution, source paths and hashes
are recorded in [primitive provenance](../native/migration/BLENDER_PRIMITIVES.md).
Upstream GPL-2.0-or-later algorithms are distributed here under GPL-3.0-or-later;
both license texts and corresponding adapted sources accompany the release.

| Component | Version/source | License and source |
| --- | --- | --- |
| CPython | 3.12.12 | PSF and bundled notices in CPython-LICENSE.txt; https://www.python.org/downloads/release/python-31212/ |
| NumPy | 1.26.4 | BSD and bundled dependency notices copied from its installed distribution; https://github.com/numpy/numpy/releases/tag/v1.26.4 |
| PySide6/Shiboken | 6.12.0 | LGPL-3.0 / GPL alternatives recorded in wheel metadata; https://download.qt.io/official_releases/QtForPython/ |
| Qt | 6.12.0 | GPL/LGPL and component-specific notices; https://doc.qt.io/qt-6/licensing.html |
| Eigen/libigl | Vendored addon snapshots | MPL-2.0 and original header notices; source is included under native/vendor |
| happly | Snapshot hash in native/vendor/PROVENANCE.md | MIT; included source and license |
| earcut.hpp | 2.2.4 | ISC; included source and license |
| Nuitka | 4.1.1 build/runtime support | Apache-2.0; https://nuitka.net/pages/overview.html |

Qt source archives for the pinned SDK are available at
https://download.qt.io/online/qtsdkrepository/all_os/qt/qt6_6120_windows_line_endings_src/qt.qt6.6120/.
Qt for Python component notices: https://doc.qt.io/qtforpython-6/licenses.html.
The release keeps Qt libraries dynamically replaceable and includes the matching SDK
SBOM files when available. Upstream commercial-license text included in a wheel is
retained as upstream metadata; this application uses the open-source license alternatives.

The companion source archive includes application/native sources, pinned dependency
lockfile, tests, build scripts and unchanged vendored headers. The portable runtime
contains Windows redistributable runtime DLLs selected by Nuitka. These components
retain their original licenses; the application license does not replace them.
