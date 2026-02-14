#!/usr/bin/env python3
import re, time
from pathlib import Path

steamid = "32998554"

localconfig = Path.home() / f".var/app/com.valvesoftware.Steam/.local/share/Steam/userdata/{steamid}/config/localconfig.vdf"
sharedconfig = Path.home() / f".var/app/com.valvesoftware.Steam/.local/share/Steam/userdata/{steamid}/7/remote/sharedconfig.vdf"

def backup(p: Path) -> Path:
    bak = p.with_suffix(p.suffix + f".bak.{time.strftime('%Y%m%d-%H%M%S')}")
    bak.write_bytes(p.read_bytes())
    return bak

def main() -> int:
    if not localconfig.exists():
        print("Missing:", localconfig)
        return 2
    if not sharedconfig.exists():
        print("Missing:", sharedconfig)
        return 3

    lc = localconfig.read_text(encoding="utf-8", errors="replace")
    sc = sharedconfig.read_text(encoding="utf-8", errors="replace")

    m = re.search(r'^\s*"user-collections"\s*"([^"]*)"\s*$', lc, flags=re.M)
    if not m:
        print('Could not find "user-collections" in localconfig.vdf')
        return 4

    user_collections_escaped_json = m.group(1)

    if re.search(r'^\s*"UserCollections"\s*"', sc, flags=re.M):
        sc2 = re.sub(
            r'^(\s*"UserCollections"\s*")([^"]*)(".*)$',
            r'\1' + user_collections_escaped_json + r'\3',
            sc,
            flags=re.M
        )
    else:
        sc2 = sc + f'\n\t\t"UserCollections"\t\t"{user_collections_escaped_json}"\n'

    bak = backup(sharedconfig)
    sharedconfig.write_text(sc2, encoding="utf-8")

    print("Updated sharedconfig.vdf UserCollections from localconfig user-collections.")
    print("Backup:", bak)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
