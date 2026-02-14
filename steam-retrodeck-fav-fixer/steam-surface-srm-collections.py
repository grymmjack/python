#!/usr/bin/env python3
import os
import json
import base64
import time
import shutil
import vdf

STEAMID3 = "32998554"
LOCALCONFIG = os.path.expanduser(
    f"~/.var/app/com.valvesoftware.Steam/.local/share/Steam/userdata/{STEAMID3}/config/localconfig.vdf"
)

MASTER = "RetroDECK"
SYSTEMS = [
    "amigacd32","amstradcpc","atari2600","atari5200","atari7800","dreamcast","gba","gc","genesis",
    "n64","nes","ps2","psx","saturn","sgb","snes","switch","unknown","vectrex","wii","wiiu","x68000","xbox","zxspectrum"
]

def backup_file(path: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    b = f"{path}.bak.{ts}"
    shutil.copy2(path, b)
    return b

def b64_nopad(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("ascii").rstrip("=")

def srm_id(name: str) -> str:
    return f"srm-{b64_nopad(name)}"

def walk(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield obj, k, v
            yield from walk(v)

def main():
    raw = open(LOCALCONFIG, "rb").read().decode("utf-8", errors="ignore").lstrip("\ufeff")
    data = vdf.loads(raw)

    # Find UIStoreLocalSteamUIState key (it’s a JSON string)
    hits = []
    for parent, k, v in walk(data):
        if k == "UIStoreLocalSteamUIState" and isinstance(v, str) and v.strip().startswith("{"):
            hits.append((parent, k))
    if not hits:
        raise SystemExit("Could not find UIStoreLocalSteamUIState in localconfig.vdf")

    parent, key = hits[0]
    state = json.loads(parent[key])

    # Ensure mapCollapsedState exists and is a list
    mcs = state.get("mapCollapsedState")
    if not isinstance(mcs, list):
        mcs = []
        state["mapCollapsedState"] = mcs

    existing_ids = set()
    for item in mcs:
        if isinstance(item, list) and item and isinstance(item[0], str):
            existing_ids.add(item[0])

    # Build desired ids
    desired = [srm_id(MASTER)] + [srm_id(f"{MASTER} - {s}") for s in SYSTEMS]

    added = 0
    for cid in desired:
        if cid not in existing_ids:
            # default collapsed = true (matches your existing pattern)
            mcs.append([cid, True])
            existing_ids.add(cid)
            added += 1

    # Write back JSON string
    parent[key] = json.dumps(state, separators=(",", ":"))

    b = backup_file(LOCALCONFIG)
    with open(LOCALCONFIG, "w", encoding="utf-8") as f:
        vdf.dump(data, f, pretty=True)

    print(f"Updated UIStoreLocalSteamUIState. Added {added} collection ids to mapCollapsedState.")
    print(f"Backup: {b}")
    print("Now start Steam.")

if __name__ == "__main__":
    main()
