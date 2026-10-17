#!/usr/bin/env bash
# Codex Cloud install script and clean Ubuntu CI setup; run from any directory.
set -euo pipefail
# shellcheck source=tools/cloud/environment.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/environment.sh"
cd -- "$AF_REPO_ROOT"

install_system_packages() {
    local elevate=()
    if [[ "$EUID" -ne 0 ]]; then
        if command -v sudo >/dev/null && sudo -n true 2>/dev/null; then
            elevate=(sudo -n)
        else
            echo 'Using existing compiler/runtime libraries; host checks still required.'
            return
        fi
    fi
    "${elevate[@]}" apt-get update
    "${elevate[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential ca-certificates git python3-pip \
        libegl1 libgl1 libopengl0 libxkbcommon0 libdbus-1-3
}

install_uv() {
    local target="$AF_REPO_ROOT/.tools/bootstrap"
    if [[ -x "$target/bin/uv" ]] && [[ "$("$target/bin/uv" --version)" == "uv 0.9.29"* ]]; then return; fi
    mkdir -p -- "$target"
    if command -v uv >/dev/null; then
        uv pip install --no-deps --only-binary=:all: --upgrade --target "$target" uv==0.9.29
    else
        python3 -m pip install --disable-pip-version-check --no-cache-dir --no-deps \
            --only-binary=:all: --upgrade --target "$target" uv==0.9.29
    fi
}

if [[ "$(uname -s)" != Linux ]] || ! command -v apt-get >/dev/null; then
    echo 'Cloud setup requires Ubuntu/Debian Linux with Python/pip and a C++ toolchain.' >&2
    exit 1
fi
install_system_packages
install_uv
uv python install --no-bin "$(cat .python-version)"
uv sync --locked --extra desktop --group cloud
uv run --no-sync python tools/check_cloud_host.py
shellcheck tools/cloud/*.sh
uv run --no-sync python tools/check_core.py --native-style
