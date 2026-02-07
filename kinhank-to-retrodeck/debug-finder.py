#!/usr/bin/env python3
"""
Debug tool to see what folders are being found and why they're rejected
"""

import os
import sys

# Configuration
LIST_FILE = os.path.expanduser("~/kinhank-dirs.txt")
KINHANK_BASE = "/media/grymmjack/Super Game HDD/CORE - TYPE R/collections/COMPUTERS/roms"

GAME_EXTENSIONS = [
    ".zip", ".7z", ".rar", ".iso", ".cue", ".bin", ".chd",
    ".sfc", ".smc", ".n64", ".z64", ".nes", ".gba", ".nds",
]

BAD_KEYWORDS = [
    "media", "artwork", "bezel", "bezels", "wheel", "logo", 
    "fanart", "boxart", "screenshot", "snap", "video", "manual",
]

def analyze_folder(path):
    """Analyze what's in a folder"""
    if not os.path.exists(path):
        return None
    
    try:
        entries = os.listdir(path)
    except:
        return None
    
    games = []
    media = []
    subdirs = []
    
    for entry in entries:
        entry_path = os.path.join(path, entry)
        entry_lower = entry.lower()
        
        if os.path.isdir(entry_path):
            subdirs.append(entry)
        elif any(entry_lower.endswith(ext) for ext in GAME_EXTENSIONS):
            games.append(entry)
        elif entry_lower.endswith(('.png', '.jpg', '.xml')):
            media.append(entry)
    
    return {
        'games': games,
        'media': media,
        'subdirs': subdirs,
        'total': len(entries)
    }

# Load paths
print("Loading directory map...")
if os.path.exists(LIST_FILE):
    with open(LIST_FILE, 'r') as f:
        all_paths = [line.strip() for line in f if line.strip()]
else:
    print(f"❌ Not found: {LIST_FILE}")
    sys.exit(1)

# Find SNES folders
system = "snes"
print(f"\n🔍 Searching for '{system}' folders...\n")

candidates = [p for p in all_paths if os.path.basename(p).lower() == system]
print(f"Found {len(candidates)} folders named '{system}':\n")

# Analyze each
for i, path in enumerate(candidates, 1):
    info = analyze_folder(path)
    
    if info is None:
        status = "❌ CANNOT ACCESS"
    elif len(info['games']) > 0:
        status = f"✅ HAS {len(info['games'])} GAMES"
    elif len(info['subdirs']) > 0:
        status = f"📁 {len(info['subdirs'])} SUBDIRS"
    else:
        status = f"⚠️  EMPTY (only {len(info['media'])} media files)"
    
    # Check for bad keywords
    has_bad = any(kw in path.lower() for kw in BAD_KEYWORDS)
    if has_bad:
        status += " [BAD KEYWORD]"
    
    print(f"{i}. {status}")
    print(f"   {path}")
    
    if info and len(info['games']) > 0:
        print(f"   Games: {info['games'][:3]}{'...' if len(info['games']) > 3 else ''}")
    if info and len(info['subdirs']) > 0:
        print(f"   Subdirs: {', '.join(info['subdirs'][:5])}{'...' if len(info['subdirs']) > 5 else ''}")
        
        # Check if there's a "roms" subdirectory with games
        if 'roms' in info['subdirs']:
            roms_subdir = os.path.join(path, 'roms')
            roms_info = analyze_folder(roms_subdir)
            if roms_info and len(roms_info['games']) > 0:
                print(f"   🎮 FOUND {len(roms_info['games'])} GAMES IN 'roms' SUBDIR!")
                print(f"      Sample: {', '.join(roms_info['games'][:3])}")
    print()

# Check the RetroBat path specifically
print("\n" + "="*60)
print("🎯 Checking RetroBat path specifically...")
print("="*60)

retrobat_snes = os.path.join(KINHANK_BASE, "RetroBat", "snes")
if os.path.exists(retrobat_snes):
    info = analyze_folder(retrobat_snes)
    print(f"✅ EXISTS: {retrobat_snes}")
    print(f"   Total items: {info['total'] if info else 0}")
    print(f"   Game files: {len(info['games']) if info else 0}")
    print(f"   Subdirs: {len(info['subdirs']) if info else 0}")
    
    if info and len(info['games']) > 0:
        print(f"   Sample games: {', '.join(info['games'][:5])}")
    elif info and len(info['subdirs']) > 0:
        # Check one level deeper
        subdir_path = os.path.join(retrobat_snes, info['subdirs'][0])
        sub_info = analyze_folder(subdir_path)
        print(f"\n   Checking subdir: {info['subdirs'][0]}")
        if sub_info and len(sub_info['games']) > 0:
            print(f"   ✅ Found {len(sub_info['games'])} games in subdir!")
            print(f"   Sample: {', '.join(sub_info['games'][:3])}")
else:
    print(f"❌ NOT FOUND: {retrobat_snes}")
    
    # Check if RetroBat folder exists
    retrobat_base = os.path.join(KINHANK_BASE, "RetroBat")
    if os.path.exists(retrobat_base):
        print(f"\n✅ RetroBat folder exists: {retrobat_base}")
        subdirs = [d for d in os.listdir(retrobat_base) if os.path.isdir(os.path.join(retrobat_base, d))]
        print(f"   Subdirectories: {', '.join(subdirs[:10])}")
    else:
        print(f"❌ RetroBat folder not found: {retrobat_base}")

print("\n💡 Tip: The path with ✅ HAS X GAMES is your real ROM folder!")
