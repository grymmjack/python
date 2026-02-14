#!/usr/bin/env python3
import os
import re

paths = [
    os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/userdata/32998554/config/localconfig.vdf"),
    os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/userdata/32998554/7/remote/sharedconfig.vdf"),
]

needles = [
    "srm-UmV0cm9ERUNL",  # your RetroDECK collection id
    "srm-",
    "collection",
    "collections",
    "user-collections",
    "UserCollections",
    "RETRODECK",
    "RetroDECK",
]

rx = re.compile("|".join(re.escape(n) for n in needles), re.IGNORECASE)

for p in paths:
    print(f"\n=== {p} ===")
    if not os.path.isfile(p):
        print("MISSING")
        continue
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            if rx.search(line):
                print(f"{i}: {line.rstrip()}")
