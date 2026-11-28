# Numerical source delta

`native-contact-release.patch` is the task-only change against the qualified local AVBD
runtime used by portable 0.4.3. Its base is the exact runtime source in the preceding
release's `avbd-sources.zip`, plus any explicitly recorded local runtime changes. The
seven changed preimages and SHA-256 receipt are retained under the main project's
`build/avbd-release-20261128/native-before`. This patch does not represent or replace the
runtime checkout's extensive pre-existing uncommitted changes.

`key_test.cpp` and `policy_test.cpp` compile as C++17 programs with the numerical source
directory on the include path. They check canonical stable key ordering, bounded candidate
allocation, invalid budget inputs and separate root/local/fixed-radius initialization.
Actual CUDA replay also compares positions, connectivity, velocity and contact checkpoint
bytes and runs the native geometry audit. All skin vertices remain active.

Full exact source recovery uses the completed release's `avbd-sources.zip` and manifest.
Local compilation, replay and resource evidence are in `build/avbd-release-20261128`.
The [task record](../avbd-contact-release.md) distinguishes completed and pending checks.
