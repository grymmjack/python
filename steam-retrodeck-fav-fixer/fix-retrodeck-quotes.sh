#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

flatpak kill com.valvesoftware.Steam || true
"$SCRIPT_DIR/bin/python" "$SCRIPT_DIR/fix-retrodeck-quotes.py" --apply
# flatpak run com.valvesoftware.Steam

