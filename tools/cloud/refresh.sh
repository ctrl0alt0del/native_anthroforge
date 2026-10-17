#!/usr/bin/env bash
# Refresh dependencies and native outputs after changing branches or uv.lock.
set -euo pipefail
# shellcheck source=tools/cloud/environment.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/environment.sh"
cd -- "$AF_REPO_ROOT"
uv sync --locked --extra desktop --group cloud
uv run --no-sync cmake --preset portable-core
uv run --no-sync cmake --build --preset portable-core
uv run --no-sync anthroforge doctor --require-native
