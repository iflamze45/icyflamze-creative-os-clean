#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────
# setup.sh — one-shot bootstrap for icyflamze-creative-os
# Installs deps and builds all subprojects (LTX-2, openhuman).
# Supports Ubuntu/Debian and macOS.
# ─────────────────────────────────────────────────────────────

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

info()  { echo -e "${CYAN}→${NC} $*"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}!${NC} $*"; }
die()   { echo -e "${RED}✗${NC} $*" >&2; exit 1; }
header(){ echo -e "\n${BOLD}${CYAN}══ $* ══${NC}"; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OS="$(uname -s)"

# ── 0. Submodules ────────────────────────────────────────────
header "Initialising git submodules"
git -C "$REPO_ROOT" submodule update --init --recursive
ok "Submodules ready"

# ── 1. Detect OS and install system deps ─────────────────────
header "System dependencies"

install_linux_deps() {
    info "Updating apt and installing build deps (requires sudo)…"
    sudo apt-get update -qq
    sudo apt-get install -y --no-install-recommends \
        build-essential cmake pkg-config \
        libssl-dev libasound2-dev libxdo-dev \
        libxtst-dev libx11-dev libevdev-dev \
        clang mold curl git
    ok "Linux system deps installed"
}

install_macos_deps() {
    if ! command -v brew &>/dev/null; then
        die "Homebrew not found. Install it first: https://brew.sh"
    fi
    info "Installing macOS build deps via Homebrew…"
    brew install cmake pkg-config openssl mold 2>/dev/null || true
    ok "macOS system deps installed"
}

case "$OS" in
    Linux)  install_linux_deps ;;
    Darwin) install_macos_deps ;;
    *)      warn "Unknown OS '$OS' — skipping system dep install. You may need to install build deps manually." ;;
esac

# ── 2. Rust toolchain ────────────────────────────────────────
header "Rust toolchain"

if ! command -v rustc &>/dev/null; then
    info "Rust not found — installing via rustup…"
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --default-toolchain stable --profile minimal
    # shellcheck source=/dev/null
    source "$HOME/.cargo/env"
    ok "Rust installed: $(rustc --version)"
else
    export PATH="$HOME/.cargo/bin:$PATH"
    ok "Rust already installed: $(rustc --version)"
fi

# The project pins 1.93.0 in rust-toolchain.toml; override to use
# the system stable toolchain so we don't need network access to rustup.
export RUSTUP_TOOLCHAIN=stable

# ── 3. uv (Python package manager for LTX-2) ─────────────────
header "uv (Python package manager)"

if ! command -v uv &>/dev/null; then
    info "uv not found — installing…"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    ok "uv installed: $(uv --version)"
else
    ok "uv already installed: $(uv --version)"
fi

# ── 4. LTX-2 ─────────────────────────────────────────────────
header "LTX-2 — Python environment"

LTX2_DIR="$REPO_ROOT/LTX-2"
if [ ! -f "$LTX2_DIR/pyproject.toml" ]; then
    die "LTX-2 submodule is empty. Run: git submodule update --init LTX-2"
fi

info "Installing LTX-2 Python dependencies (uv sync)…"
(cd "$LTX2_DIR" && uv sync --frozen)
ok "LTX-2 environment ready at LTX-2/.venv"

# ── 5. openhuman-core ────────────────────────────────────────
header "openhuman — building core binary"

OH_DIR="$REPO_ROOT/openhuman"
if [ ! -f "$OH_DIR/Cargo.toml" ]; then
    die "openhuman submodule is empty. Run: git submodule update --init openhuman"
fi

info "Compiling openhuman-core (this takes ~8 min on first run)…"
(cd "$OH_DIR" && cargo build --release --bin openhuman-core)
ok "Binary ready at openhuman/target/release/openhuman-core"

# ── 6. openhuman .env ────────────────────────────────────────
header "openhuman — environment config"

ENV_FILE="$OH_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    info "Generating .env from .env.example…"
    cp "$OH_DIR/.env.example" "$ENV_FILE"
    TOKEN="$(openssl rand -hex 32)"
    # Replace the commented-out token line with the generated value
    sed -i.bak "s/# OPENHUMAN_CORE_TOKEN=/OPENHUMAN_CORE_TOKEN=$TOKEN/" "$ENV_FILE" \
        && rm -f "$ENV_FILE.bak"
    ok ".env created with a fresh OPENHUMAN_CORE_TOKEN"
    echo -e "   ${YELLOW}Token:${NC} $TOKEN"
    echo    "   (save this — you'll need it to connect a client)"
else
    ok ".env already exists — skipping token generation"
fi

# ── 7. Summary ───────────────────────────────────────────────
header "All done"
cat <<EOF

  ${GREEN}LTX-2${NC} (video generation model):
    Activate:  source LTX-2/.venv/bin/activate
    Note:      Download model weights separately (see LTX-2/README.md)

  ${GREEN}openhuman-core${NC} (AI assistant JSON-RPC server):
    Run:       cd openhuman && source .env && \\
               ./target/release/openhuman-core run --host 0.0.0.0 --port 7788
    Health:    curl http://localhost:7788/health

EOF
