#!/usr/bin/env python3
import os
import re
import time
import json
import base64
import shutil
import argparse
import zlib
import vdf

STEAM_BASE = os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam")
USERDATA_DIR = os.path.join(STEAM_BASE, "userdata")

RETRODECK_TOKEN = "net.retrodeck.retrodeck"
SYSTEM_RE = re.compile(r"(?:^|\s)-s\s+([A-Za-z0-9_+-]+)(?:\s|$)")
ALREADY_TAGGED_RE = re.compile(r"\[[A-Za-z0-9_+-]+\]\s*$")

TARGET_FIXED = "flatpak-spawn --host"

def backup_file(path: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    b = f"{path}.bak.{ts}"
    shutil.copy2(path, b)
    return b

def strip_outer_quotes(s: str) -> str:
    if isinstance(s, str) and len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s

def get_field(sc: dict, key_variants):
    for k in key_variants:
        if k in sc:
            return k, sc.get(k, "")
    return key_variants[0], ""

def set_field(sc: dict, key_variants, value: str):
    for k in key_variants:
        if k in sc:
            sc[k] = value
            return
    sc[key_variants[0]] = value

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

def extract_system(sc: dict) -> str:
    lo = (sc.get("LaunchOptions") or sc.get("launchoptions") or "")
    m = SYSTEM_RE.search(lo)
    return m.group(1).lower() if m else "unknown"

def compute_shortcut_appid(exe: str, appname: str) -> int:
    """
    Steam shortcut appid: (CRC32(exe + appname) | 0x80000000), unsigned 32-bit.
    """
    s = (exe + appname).encode("utf-8", errors="ignore")
    crc = zlib.crc32(s) & 0xFFFFFFFF
    return (crc | 0x80000000) & 0xFFFFFFFF

def collection_id_srm(name: str) -> str:
    """
    Your Steam uses collection ids like: srm-UmV0cm9ERUNL
    which is base64 (no padding) of the name, prefixed with srm-.
    """
    b = base64.b64encode(name.encode("utf-8")).decode("ascii")
    b = b.rstrip("=")
    return f"srm-{b}"

def find_key_path_containing(d, target_key: str):
    """
    Returns list of (parent_dict, key) where parent_dict[key] exists and key == target_key.
    """
    hits = []
    if isinstance(d, dict):
        for k, v in d.items():
            if k == target_key:
                hits.append((d, k))
            hits.extend(find_key_path_containing(v, target_key))
    return hits

def load_text_vdf(path: str) -> dict:
    raw = open(path, "rb").read()
    txt = raw.decode("utf-8", errors="ignore").lstrip("\ufeff")
    return vdf.loads(txt)

def dump_text_vdf(data: dict, path: str):
    # vdf.dump expects a file object
    with open(path, "w", encoding="utf-8") as f:
        vdf.dump(data, f, pretty=True)

def update_user_collections_json(localcfg: dict, system_to_appids: dict[str, list[int]], master_name: str):
    """
    Update the JSON string at key 'user-collections' (and 'user-collections-v2' if present).
    Keeps existing collections; adds/updates:
      - master collection (all RetroDECK appids)
      - per-system collections
    """
    keys_to_update = ["user-collections", "user-collections-v2"]
    hits = []
    for k in keys_to_update:
        hits.extend([(parent, key) for (parent, key) in find_key_path_containing(localcfg, k)])

    if not hits:
        return False, "Did not find 'user-collections' key in localconfig.vdf."

    # build desired membership
    all_ids = sorted({aid for ids in system_to_appids.values() for aid in ids})
    desired = {}
    desired[collection_id_srm(master_name)] = all_ids
    for sys, ids in system_to_appids.items():
        desired[collection_id_srm(f"{master_name} - {sys}")] = sorted(set(ids))

    updated_any = False

    for parent, key in hits:
        raw = parent.get(key, "")
        if not isinstance(raw, str) or raw.strip() == "":
            # create fresh JSON object
            collections = {}
        else:
            try:
                collections = json.loads(raw)
                if not isinstance(collections, dict):
                    collections = {}
            except Exception:
                # if Steam stored something non-json here, bail on this key
                continue

        # collections format (from your file):
        # {
        #   "hidden": {"id":"hidden","added":[...],"removed":[]},
        #   "srm-...": {"id":"srm-...","added":[...],"removed":[]},
        # }
        for cid, appids in desired.items():
            entry = collections.get(cid)
            if not isinstance(entry, dict):
                entry = {"id": cid, "added": [], "removed": []}
                collections[cid] = entry

            # Merge: keep existing + ensure our ids present
            added = entry.get("added", [])
            if not isinstance(added, list):
                added = []
            added_set = {int(x) for x in added if isinstance(x, (int, str)) and str(x).isdigit()}
            for aid in appids:
                added_set.add(int(aid))

            entry["id"] = cid
            entry["added"] = sorted(added_set)
            entry["removed"] = []  # simplest: don't maintain removals here

        parent[key] = json.dumps(collections, separators=(",", ":"))
        updated_any = True

    if not updated_any:
        return False, "Found collection keys but could not parse JSON values."
    return True, f"Updated {len(desired)} collections in '{', '.join(sorted(set(k for _, k in hits)))}'."

def main():
    ap = argparse.ArgumentParser(description="RetroDECK Steam organizer (Steam Flatpak): fix TARGET, rename, create collections.")
    ap.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    ap.add_argument("--no-rename", action="store_true", help="Do not append [system] to names")
    ap.add_argument("--master", default="RETRODECK", help="Master collection name (default: RETRODECK)")
    ap.add_argument("--no-collections", action="store_true", help="Skip collections update")
    args = ap.parse_args()

    steamid3 = detect_steamid3()
    shortcuts_path = shortcuts_vdf_path(steamid3)
    localconfig_path = localconfig_vdf_path(steamid3)

    if not os.path.isfile(shortcuts_path):
        raise FileNotFoundError(f"shortcuts.vdf not found: {shortcuts_path}")
    if not os.path.isfile(localconfig_path):
        raise FileNotFoundError(f"localconfig.vdf not found: {localconfig_path}")

    # --- Load shortcuts (binary VDF) ---
    with open(shortcuts_path, "rb") as f:
        shortcuts_data = vdf.binary_load(f)

    shortcuts = shortcuts_data.get("shortcuts", {})
    total = len(shortcuts)

    changed_shortcuts = 0
    retro_count = 0
    system_to_appids: dict[str, list[int]] = {}

    # IMPORTANT: appid depends on exe+appname, so we must compute after our modifications
    for sc in shortcuts.values():
        if not isinstance(sc, dict):
            continue
        if not is_retrodeck(sc):
            continue

        retro_count += 1
        sys = extract_system(sc)

        # Fix TARGET field (Steam UI "TARGET") stored as exe/Exe
        _, target = get_field(sc, ("exe", "Exe"))
        target2 = strip_outer_quotes(target)
        if (target2 or "").strip() == "":
            target2 = TARGET_FIXED
        if target2 != target:
            set_field(sc, ("exe", "Exe"), target2)
            changed_shortcuts += 1

        # Rename AppName to include [system]
        if not args.no_rename:
            _, name = get_field(sc, ("AppName", "appname"))
            if isinstance(name, str) and name:
                if not ALREADY_TAGGED_RE.search(name):
                    name2 = f"{name} [{sys}]"
                    set_field(sc, ("AppName", "appname"), name2)
                    changed_shortcuts += 1

        # Compute appid for collections using the FINAL exe+name in this record
        exe_final = (sc.get("exe") or sc.get("Exe") or "")
        name_final = (sc.get("AppName") or sc.get("appname") or "")
        appid = compute_shortcut_appid(exe_final, name_final)
        system_to_appids.setdefault(sys, []).append(appid)

    systems = ", ".join(sorted(system_to_appids.keys()))

    print(f"\nDetected SteamID3: {steamid3}")
    print(f"shortcuts.vdf: {shortcuts_path}")
    print(f"localconfig.vdf: {localconfig_path}")
    print(f"Total shortcuts: {total}")
    print(f"RetroDECK matched: {retro_count}")
    print(f"Planned shortcut changes (TARGET/name): {changed_shortcuts}")
    print(f"Systems found ({len(system_to_appids)}): {systems}")

    # --- Write shortcuts.vdf ---
    if args.apply and changed_shortcuts > 0:
        b = backup_file(shortcuts_path)
        with open(shortcuts_path, "wb") as f:
            vdf.binary_dump(shortcuts_data, f)
        print(f"\n[WRITE] Updated shortcuts.vdf (backup: {b})")
    else:
        print("\n[DRY-RUN] shortcuts.vdf not written (use --apply).")

    # --- Collections update via localconfig.vdf JSON ---
    if args.no_collections:
        print("\n[COLLECTIONS] Skipped (--no-collections).")
        return

    # Load localconfig (text VDF)
    localcfg = load_text_vdf(localconfig_path)
    ok, msg = update_user_collections_json(localcfg, system_to_appids, args.master)
    print(f"\n[COLLECTIONS] {msg}")

    if args.apply and ok:
        b = backup_file(localconfig_path)
        dump_text_vdf(localcfg, localconfig_path)
        print(f"[WRITE] Updated localconfig.vdf (backup: {b})")
    else:
        print("[DRY-RUN] localconfig.vdf not written (use --apply).")

if __name__ == "__main__":
    main()
