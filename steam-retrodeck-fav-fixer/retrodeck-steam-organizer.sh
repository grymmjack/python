#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

flatpak kill com.valvesoftware.Steam || true
"$DIR/bin/python" "$DIR/retrodeck-steam-organizer.py" --apply
flatpak run com.valvesoftware.Steam
