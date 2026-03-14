#!/usr/bin/env python3
"""Remove all (or filtered) non-Steam game shortcuts from Steam."""

import os
import re
import sys
import time
import json
import shutil
import argparse
import vdf

STEAM_BASE = os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam")
USERDATA_DIR = os.path.join(STEAM_BASE, "userdata")

RETRODECK_TOKEN = "net.retrodeck.retrodeck"


def backup_file(path: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    b = f"{path}.bak.{ts}"
    shutil.copy2(path, b)
    return b


def detect_steamid3() -> str:
    if not os.path.isdir(USERDATA_DIR):
        raise FileNotFoundError(f"Steam userdata dir not found: {USERDATA_DIR}")

    ids = [
        d for d in os.listdir(USERDATA_DIR)
        if d.isdigit() and os.path.isdir(os.path.join(USERDATA_DIR, d))
    ]
    if not ids:
        raise RuntimeError(f"No Steam userdata folders found in: {USERDATA_DIR}")

    if len(ids) > 1:
        ids.sort(key=lambda d: os.path.getmtime(os.path.join(USERDATA_DIR, d)), reverse=True)

    return ids[0]


def shortcuts_vdf_path(steamid3: str) -> str:
    return os.path.join(USERDATA_DIR, steamid3, "config", "shortcuts.vdf")


def localconfig_vdf_path(steamid3: str) -> str:
    return os.path.join(USERDATA_DIR, steamid3, "config", "localconfig.vdf")


def is_retrodeck(sc: dict) -> bool:
    lo = (sc.get("LaunchOptions") or sc.get("launchoptions") or "")
    return RETRODECK_TOKEN in lo


def get_name(sc: dict) -> str:
    return sc.get("AppName") or sc.get("appname") or "(unnamed)"


def get_exe(sc: dict) -> str:
    return sc.get("exe") or sc.get("Exe") or ""


def load_text_vdf(path: str) -> dict:
    raw = open(path, "rb").read()
    txt = raw.decode("utf-8", errors="ignore").lstrip("\ufeff")
    return vdf.loads(txt)


def dump_text_vdf(data: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        vdf.dump(data, f, pretty=True)


def find_key_path_containing(d, target_key: str):
    hits = []
    if isinstance(d, dict):
        for k, v in d.items():
            if k == target_key:
                hits.append((d, k))
            hits.extend(find_key_path_containing(v, target_key))
    return hits


def clean_collections(localcfg: dict) -> tuple[bool, int]:
    """Remove non-Steam game appids (high-bit set) from user-collections JSON."""
    keys_to_check = ["user-collections", "user-collections-v2"]
    hits = []
    for k in keys_to_check:
        hits.extend(find_key_path_containing(localcfg, k))

    if not hits:
        return False, 0

    total_removed = 0
    for parent, key in hits:
        raw = parent.get(key, "")
        if not isinstance(raw, str) or raw.strip() == "":
            continue
        try:
            collections = json.loads(raw)
            if not isinstance(collections, dict):
                continue
        except Exception:
            continue

        cids_to_delete = []
        for cid, entry in collections.items():
            if not isinstance(entry, dict):
                continue
            added = entry.get("added", [])
            if not isinstance(added, list):
                continue
            # Non-Steam shortcut appids have the high bit set (0x80000000)
            original_len = len(added)
            filtered = [a for a in added if isinstance(a, int) and not (a & 0x80000000)]
            entry["added"] = filtered
            total_removed += original_len - len(filtered)

            # If collection is now empty and looks like a SRM/shortcut collection, mark for removal
            if not filtered and cid.startswith("srm-"):
                cids_to_delete.append(cid)

        for cid in cids_to_delete:
            del collections[cid]
            total_removed += 1  # count the collection itself

        parent[key] = json.dumps(collections, separators=(",", ":"))

    return True, total_removed


def main():
    ap = argparse.ArgumentParser(
        description="Remove non-Steam game shortcuts from Steam (Flatpak)."
    )
    ap.add_argument("--apply", action="store_true",
                    help="Write changes (default: dry-run)")
    ap.add_argument("--retrodeck-only", action="store_true",
                    help="Only remove RetroDECK shortcuts (keep other non-Steam games)")
    ap.add_argument("--filter", type=str, default=None,
                    help="Only remove shortcuts whose name matches this regex")
    ap.add_argument("--no-clean-collections", action="store_true",
                    help="Skip cleaning collection references from localconfig.vdf")
    ap.add_argument("--yes", "-y", action="store_true",
                    help="Skip confirmation prompt (use with --apply)")
    args = ap.parse_args()

    steamid3 = detect_steamid3()
    shortcuts_path = shortcuts_vdf_path(steamid3)
    localconfig_path = localconfig_vdf_path(steamid3)

    if not os.path.isfile(shortcuts_path):
        print(f"shortcuts.vdf not found: {shortcuts_path}")
        sys.exit(1)

    # --- Load shortcuts (binary VDF) ---
    with open(shortcuts_path, "rb") as f:
        shortcuts_data = vdf.binary_load(f)

    shortcuts = shortcuts_data.get("shortcuts", {})
    total = len(shortcuts)

    # Build a filter function
    name_re = re.compile(args.filter, re.IGNORECASE) if args.filter else None

    def should_remove(sc: dict) -> bool:
        if not isinstance(sc, dict):
            return False
        if args.retrodeck_only and not is_retrodeck(sc):
            return False
        if name_re and not name_re.search(get_name(sc)):
            return False
        return True

    # Identify shortcuts to remove
    to_remove = []
    to_keep = {}
    for idx, sc in shortcuts.items():
        if should_remove(sc):
            to_remove.append((idx, sc))
        else:
            to_keep[idx] = sc

    # --- Report ---
    label = "ALL non-Steam games"
    if args.retrodeck_only:
        label = "RetroDECK non-Steam games"
    if args.filter:
        label += f" matching /{args.filter}/"

    print(f"\nDetected SteamID3: {steamid3}")
    print(f"shortcuts.vdf: {shortcuts_path}")
    print(f"Total non-Steam shortcuts: {total}")
    print(f"Removing ({label}): {len(to_remove)}")
    print(f"Keeping: {len(to_keep)}")

    if to_remove:
        print(f"\nShortcuts to remove:")
        for idx, sc in to_remove:
            name = get_name(sc)
            exe = get_exe(sc)
            retro = " [RetroDECK]" if is_retrodeck(sc) else ""
            print(f"  [{idx}] {name}{retro}")
            if exe:
                print(f"       exe: {exe}")
    else:
        print("\nNo shortcuts match the removal criteria.")
        return

    # --- Confirmation ---
    if args.apply and not args.yes:
        answer = input(f"\nRemove {len(to_remove)} shortcut(s)? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    # --- Write shortcuts.vdf ---
    if args.apply:
        # Re-index kept shortcuts with sequential keys
        new_shortcuts = {}
        for new_idx, (_, sc) in enumerate(sorted(to_keep.items(), key=lambda x: int(x[0]))):
            new_shortcuts[str(new_idx)] = sc

        shortcuts_data["shortcuts"] = new_shortcuts

        b = backup_file(shortcuts_path)
        with open(shortcuts_path, "wb") as f:
            vdf.binary_dump(shortcuts_data, f)
        print(f"\n[WRITE] Removed {len(to_remove)} shortcut(s) from shortcuts.vdf")
        print(f"        Backup: {b}")
    else:
        print(f"\n[DRY-RUN] shortcuts.vdf not written (use --apply).")

    # --- Clean collections ---
    if args.no_clean_collections:
        print("[COLLECTIONS] Skipped (--no-clean-collections).")
        return

    if not os.path.isfile(localconfig_path):
        print(f"[COLLECTIONS] localconfig.vdf not found, skipping: {localconfig_path}")
        return

    localcfg = load_text_vdf(localconfig_path)
    ok, removed_count = clean_collections(localcfg)

    if ok and removed_count > 0:
        print(f"[COLLECTIONS] {removed_count} collection reference(s) to clean.")
        if args.apply:
            b = backup_file(localconfig_path)
            dump_text_vdf(localcfg, localconfig_path)
            print(f"[WRITE] Cleaned localconfig.vdf")
            print(f"        Backup: {b}")
        else:
            print("[DRY-RUN] localconfig.vdf not written (use --apply).")
    else:
        print("[COLLECTIONS] No collection references to clean.")


if __name__ == "__main__":
    main()
