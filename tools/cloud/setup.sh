#!/usr/bin/env bash
# Codex Cloud install script and clean Ubuntu CI setup; run from any directory.
set -euo pipefail
# shellcheck source=tools/cloud/environment.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/environment.sh"
cd -- "$AF_REPO_ROOT"

install_system_packages() {
    local elevate=()
    if [[ "$EUID" -ne 0 ]]; then elevate=(sudo -n); fi
    "${elevate[@]}" apt-get update
    "${elevate[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential ca-certificates curl git clang-tidy shellcheck \
        libegl1 libgl1 libopengl0 libxkbcommon0 libdbus-1-3
}

install_uv() {
    local target="$AF_REPO_ROOT/.tools/uv"
    if [[ -x "$target/uv" ]] && [[ "$("$target/uv" --version)" == "uv 0.9.29"* ]]; then return; fi
    mkdir -p -- "$target"
    curl --fail --show-error --silent --location --retry 3 \
        https://astral.sh/uv/0.9.29/install.sh -o "$target/install.sh"
    UV_UNMANAGED_INSTALL="$target" sh "$target/install.sh"
}

if [[ "$(uname -s)" != Linux ]] || ! command -v apt-get >/dev/null; then
    echo 'Cloud setup requires Ubuntu/Debian Linux with root or passwordless sudo.' >&2
    exit 1
fi
install_system_packages
install_uv
uv python install "$(cat .python-version)"
uv sync --locked --extra desktop
shellcheck tools/cloud/*.sh
uv run --no-sync python tools/check_core.py --native-style
