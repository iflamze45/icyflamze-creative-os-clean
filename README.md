# icyflamze-creative-os

A curated collection of open-source AI tools, pre-configured and ready to build.

## Projects

| Project | Description |
|---|---|
| [LTX-2](https://github.com/Lightricks/LTX-2) | DiT-based audio-video foundation model (text/image → video) |
| [openhuman](https://github.com/tinyhumansai/openhuman) | Desktop AI assistant with 118+ integrations, local memory, voice |
| [Kronos](https://github.com/shiyu-coder/Kronos) | Foundation model for financial K-line (OHLCV) forecasting — AAAI 2026 |

## Quick start

```bash
git clone --recurse-submodules https://github.com/iflamze45/icyflamze-creative-os-clean.git
cd icyflamze-creative-os-clean
chmod +x setup.sh && ./setup.sh
```

> If you cloned without `--recurse-submodules`, run `git submodule update --init --recursive` first.

## Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| Git | 2.20+ | Clone + submodules |
| Rust (rustup) | stable | Build openhuman-core |
| uv | any | LTX-2 Python env |
| curl / openssl | any | Token generation |
| **Linux**: `build-essential`, `cmake`, `libssl-dev`, `libasound2-dev`, `libxdo-dev`, `libxtst-dev`, `libx11-dev`, `libevdev-dev`, `clang`, `mold` | — | Rust system deps |
| **macOS**: Xcode CLT + `brew install cmake pkg-config openssl mold` | — | Rust system deps |

`setup.sh` installs all of the above automatically.

## Manual steps

### Kronos

```bash
cd Kronos
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Download weights (choose a size):
python download_weights.py --model mini   # 4.1M  — fastest, CPU-friendly
python download_weights.py --model small  # 24.7M — good balance
python download_weights.py --model base   # 102M  — highest accuracy (open-source)

# Run a forecast example:
python examples/prediction_example.py
```

### LTX-2

```bash
cd LTX-2
uv sync --frozen          # create .venv and install all deps
source .venv/bin/activate

# Download model weights (choose one — large files, need GPU to run):
# See LTX-2/README.md → Required Models
```

### openhuman

```bash
cd openhuman
cargo build --release --bin openhuman-core   # ~8 min first run

# Create config
cp .env.example .env
# Edit .env and set OPENHUMAN_CORE_TOKEN=$(openssl rand -hex 32)

# Run the server
source .env
./target/release/openhuman-core run --host 0.0.0.0 --port 7788

# Verify
curl http://localhost:7788/health
```

## Hardware notes

| Component | Minimum (openhuman) | Kronos | Recommended (LTX-2) |
|---|---|---|---|
| RAM | 2 GB | 1 GB+ | 64 GB+ |
| Disk | 2 GB (binary only) | ~500 MB (mini weights) | 80 GB+ (model weights) |
| GPU | Not required | Not required (CPU works) | NVIDIA GPU with 24 GB+ VRAM |
