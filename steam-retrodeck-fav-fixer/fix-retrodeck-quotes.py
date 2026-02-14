import os
import shutil
import time
import argparse
import vdf

SHORTCUTS_VDF = os.path.expanduser(
    "~/.var/app/com.valvesoftware.Steam/.local/share/Steam/userdata/32998554/config/shortcuts.vdf"
)

FIX_TO = "flatpak-spawn --host"

def backup(path: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    b = f"{path}.bak.{ts}"
    shutil.copy2(path, b)
    return b

def strip_outer_quotes(s: str) -> str:
    if isinstance(s, str) and len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s

def get_target(sc: dict):
    """Return (key, value) for the Steam 'TARGET' field."""
    for k in ("exe", "Exe"):
        if k in sc:
            return k, sc.get(k, "")
    # Sometimes weird entries exist; treat as missing
    return "exe", ""

def set_target(sc: dict, value: str):
    """Set Steam 'TARGET' field using the key Steam actually uses in this file."""
    key, _ = get_target(sc)
    sc[key] = value

def looks_like_retrodeck(sc: dict) -> bool:
    lo = (sc.get("LaunchOptions") or sc.get("launchoptions") or "").lower()
    # This is the most reliable discriminator for RetroDECK-generated shortcuts
    return "net.retrodeck.retrodeck" in lo or "retrodeck" in lo

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write changes (default dry-run)")
    ap.add_argument("--debug-one", action="store_true", help="Print keys/values for first RetroDECK shortcut and exit")
    args = ap.parse_args()

    if not os.path.isfile(SHORTCUTS_VDF):
        raise FileNotFoundError(f"shortcuts.vdf not found: {SHORTCUTS_VDF}")

    with open(SHORTCUTS_VDF, "rb") as f:
        data = vdf.binary_load(f)

    shortcuts = data.get("shortcuts", {})
    total = len(shortcuts)

    changed = 0
    matched = 0

    # Optional: show what keys are actually present
    if args.debug_one:
        for sc in shortcuts.values():
            if isinstance(sc, dict) and looks_like_retrodeck(sc):
                key, val = get_target(sc)
                print("First RetroDECK shortcut debug:")
                print("  AppName:", sc.get("AppName") or sc.get("appname"))
                print("  TARGET key:", key)
                print("  TARGET value:", repr(val))
                print("  LaunchOptions:", sc.get("LaunchOptions") or sc.get("launchoptions"))
                print("  All keys:", sorted(sc.keys()))
                return
        print("No RetroDECK shortcuts found for debug.")
        return

    for sc in shortcuts.values():
        if not isinstance(sc, dict):
            continue
        if not looks_like_retrodeck(sc):
            continue

        matched += 1

        key, target = get_target(sc)

        # Fix case 1: TARGET is quoted like "\"flatpak-spawn --host\"" or "\"...\""
        new_target = strip_outer_quotes(target)

        # Fix case 2: TARGET is empty (some syncs create empties)
        if (new_target or "").strip() == "":
            new_target = FIX_TO

        # Fix case 3: TARGET equals flatpak-spawn but is quoted; strip already handled above.
        # Ensure final value is exactly what you want (no surrounding quotes)
        if new_target != target:
            print(f"[FIX] {sc.get('AppName') or sc.get('appname') or '<unknown>'}")
            print(f"  TARGET ({key}): {target!r} -> {new_target!r}")
            set_target(sc, new_target)
            changed += 1

    print(f"\nFile: {SHORTCUTS_VDF}")
    print(f"Shortcuts total: {total}")
    print(f"RetroDECK matched: {matched}")
    print(f"RetroDECK TARGETs changed: {changed}")

    if args.apply and changed > 0:
        b = backup(SHORTCUTS_VDF)
        with open(SHORTCUTS_VDF, "wb") as f:
            vdf.binary_dump(data, f)
        print(f"\n[WRITE] Updated shortcuts.vdf")
        print(f"Backup: {b}")
    else:
        print("\n[DRY-RUN] No file written. Use --apply to save changes.")

if __name__ == "__main__":
    main()

