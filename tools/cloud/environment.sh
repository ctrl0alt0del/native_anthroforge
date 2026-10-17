#!/usr/bin/env bash
# Source this file in each new cloud shell. It does not change global shell profiles.
AF_REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
export AF_REPO_ROOT
export PATH="$AF_REPO_ROOT/.tools/bootstrap/uv:$AF_REPO_ROOT/.venv/bin:$PATH"
export UV_PYTHON_INSTALL_DIR="$AF_REPO_ROOT/.tools/python"
export UV_PROJECT_ENVIRONMENT="$AF_REPO_ROOT/.venv"
export UV_CACHE_DIR="$AF_REPO_ROOT/.tools/uv-cache"
export ANTHROFORGE_NATIVE_LIBRARY="$AF_REPO_ROOT/build/core/bin/libaf_native.so"
export CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-2}"
export QT_QPA_PLATFORM=offscreen
