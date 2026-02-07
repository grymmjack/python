#!/usr/bin/env python3
"""
Kinhank to RetroDeck ROM Mapper
Maps Kinhank 12TB drive (RetroBat structure) to RetroDeck via symlinks.
Intelligently detects real ROM folders vs media/artwork folders.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict

# ================= CONFIGURATION =================
# Input: Your directory map (generated via: find /path/to/drive -type d > kinhank-dirs.txt)
LIST_FILE = os.path.expanduser("~/kinhank-dirs.txt")

# Alternative: Direct path to Kinhank drive if mounted
KINHANK_DRIVE = "/media/grymmjack/Super Game HDD/CORE - TYPE R"

# Output: RetroDeck paths
RD_ROMS = os.path.expanduser("~/retrodeck/roms")
RD_MEDIA = os.path.expanduser("~/retrodeck/ES-DE/downloaded_media")

# DRY RUN: Set to True to see what would happen without making changes
DRY_RUN = True

# KNOWN SYSTEMS TO HUNT FOR (RetroDeck name: [possible folder names])
TARGETS = {
    # Nintendo Consoles
    "snes": ["snes", "supernintendo", "super nintendo", "super nintendo entertainment system"],
    "nes": ["nes", "nintendo entertainment system", "famicom"],
    "n64": ["n64", "nintendo 64"],
    "gc": ["gc", "gamecube", "ngc"],
    "wii": ["wii"],
    "wiiu": ["wiiu", "wii u"],
    "switch": ["switch"],
    "gb": ["gb", "gameboy"],
    "gbc": ["gbc", "gameboy color"],
    "gba": ["gba", "gameboy advance"],
    "nds": ["nds", "nintendo ds"],
    "3ds": ["3ds", "nintendo 3ds"],
    
    # Sega Consoles
    "megadrive": ["megadrive", "genesis", "sega genesis", "mega drive"],
    "mastersystem": ["mastersystem", "master system", "sms"],
    "gamegear": ["gamegear", "game gear"],
    "dreamcast": ["dreamcast", "dc"],
    "saturn": ["saturn", "sega saturn"],
    "segacd": ["segacd", "sega cd", "mega cd"],
    "sega32x": ["32x", "sega 32x"],
    
    # Sony Consoles
    "psx": ["psx", "ps1", "playstation", "playstation 1"],
    "ps2": ["ps2", "playstation 2"],
    "ps3": ["ps3", "playstation 3"],
    "psp": ["psp", "playstation portable"],
    "psvita": ["psvita", "ps vita", "vita"],
    
    # Microsoft
    "xbox": ["xbox"],
    "xbox360": ["xbox360", "xbox 360"],
    
    # Arcade
    "mame": ["mame", "arcade"],
    "neogeo": ["neogeo", "neo geo"],
    "fbneo": ["fbneo", "fba", "finalburn", "final burn alpha"],
    "cps1": ["cps1", "cp system"],
    "cps2": ["cps2", "cp system ii"],
    "cps3": ["cps3", "cp system iii"],
    "naomi": ["naomi"],
    
    # Computers
    "amiga": ["amiga"],
    "c64": ["c64", "commodore 64"],
    "dos": ["dos", "pc"],
    "msx": ["msx"],
    "msx2": ["msx2"],
    "amigacd32": ["amigacd32", "cd32"],
    "atari800": ["atari800", "atari 800"],
    "atarist": ["atarist", "atari st"],
    "x68000": ["x68000"],
    
    # Other
    "n3ds": ["3ds", "n3ds"],
    "atari2600": ["atari2600", "2600"],
    "atari5200": ["atari5200", "5200"],
    "atari7800": ["atari7800", "7800"],
    "atarijaguar": ["jaguar", "atari jaguar"],
    "atarilynx": ["lynx", "atari lynx"],
    "colecovision": ["colecovision", "coleco"],
    "intellivision": ["intellivision"],
    "ngp": ["ngp", "neo geo pocket"],
    "ngpc": ["ngpc", "neo geo pocket color"],
    "pcengine": ["pcengine", "pc engine", "turbografx", "turbografx-16", "tg16"],
    "pcenginecd": ["pcenginecd", "turbografx cd"],
    "wonderswan": ["wonderswan"],
    "wonderswancolor": ["wonderswancolor", "wonderswan color"],
    "vectrex": ["vectrex"],
    "virtualboy": ["virtualboy", "virtual boy"],
    "zxspectrum": ["zxspectrum", "zx spectrum", "spectrum"],
}

# ROM/GAME FILE EXTENSIONS (proof it's a game folder)
GAME_EXTENSIONS = [
    ".zip", ".7z", ".rar",  # Archives
    ".iso", ".cue", ".bin", ".img", ".chd",  # Disc images
    ".nds", ".3ds", ".cia",  # Nintendo DS/3DS
    ".gba", ".gbc", ".gb",  # Game Boy
    ".sfc", ".smc", ".fig",  # SNES
    ".nes", ".fds", ".unf",  # NES
    ".n64", ".z64", ".v64",  # N64
    ".gcm", ".gcz",  # GameCube
    ".wbfs", ".wad",  # Wii
    ".nsp", ".xci",  # Switch
    ".md", ".gen", ".smd",  # Genesis/Mega Drive
    ".sms", ".gg",  # Master System / Game Gear
    ".32x",  # Sega 32X
    ".cdi", ".gdi",  # Dreamcast
    ".d64", ".t64", ".prg",  # C64
    ".adf", ".dms", ".adz",  # Amiga
    ".rom", ".mx1", ".mx2",  # MSX
    ".a26",  # Atari 2600
    ".a52", ".a78",  # Atari 5200/7800
    ".j64",  # Jaguar
    ".lnx",  # Lynx
    ".col",  # ColecoVision
    ".pce",  # PC Engine
    ".ws", ".wsc",  # WonderSwan
    ".ngp", ".ngc",  # Neo Geo Pocket
    ".vec",  # Vectrex
    ".vb",  # Virtual Boy
    ".tap", ".tzx", ".z80", ".sna",  # ZX Spectrum
]

# MEDIA/ARTWORK INDICATORS (proof it's NOT a game folder)
# Note: "roms" is intentionally NOT in this list - it's often a valid subfolder name
BAD_KEYWORDS = [
    "artwork", "bezel", "bezels", "wheel", "logo", 
    "fanart", "boxart", "screenshot", "snap", "video", "manual",
    "marquee", "flyer", "cabinet", "banner", "title", "cart",
    "pcb", "gameover", "select", "story", "3d", "front",
    "attract", "theme", "overlay", "image", "emulator", "save",
]

BAD_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".xml", ".cfg", ".ini", ".txt"]

# MEDIA FOLDER MAPPING (RetroBat -> RetroDeck)
MEDIA_MAP = {
    "boxart": "covers",
    "box": "covers",
    "screenshot": "screenshots",
    "screenshots": "screenshots",
    "wheel": "marquees",
    "wheelcarbon": "marquees",
    "video": "videos",
    "snap": "videos",
    "fanart": "fanart",
}
# =================================================

class Stats:
    """Track statistics for reporting"""
    def __init__(self):
        self.found = 0
        self.linked = 0
        self.media_linked = 0
        self.skipped = 0
        self.errors = []


def load_directory_map() -> List[str]:
    """Load directory paths from kinhank-dirs.txt or scan drive directly"""
    if os.path.exists(LIST_FILE):
        print(f"📂 Loading directory map from: {LIST_FILE}")
        with open(LIST_FILE, 'r') as f:
            paths = [line.strip() for line in f if line.strip()]
        print(f"   Loaded {len(paths)} directories")
        return paths
    elif os.path.exists(KINHANK_DRIVE):
        print(f"📂 Scanning drive directly: {KINHANK_DRIVE}")
        print("   (This may take a while...)")
        paths = []
        for root, dirs, _ in os.walk(KINHANK_DRIVE):
            paths.append(root)
            # Filter out obviously bad directories to speed up walking
            dirs[:] = [d for d in dirs if d.lower() not in BAD_KEYWORDS]
        print(f"   Found {len(paths)} directories")
        return paths
    else:
        print(f"❌ ERROR: Neither {LIST_FILE} nor {KINHANK_DRIVE} found!")
        sys.exit(1)


def has_bad_keywords(path: str) -> bool:
    """Check if path contains keywords that indicate it's NOT a ROM folder"""
    path_lower = path.lower()
    return any(keyword in path_lower for keyword in BAD_KEYWORDS)


def analyze_folder_content(path: str, check_subdirs: bool = True) -> tuple[int, int, int]:
    """
    Analyze folder content and return (game_count, media_count, subdir_count)
    Returns: (# of game files, # of media files, # of subdirectories)
    
    If check_subdirs is True and no games found at this level, will check one level deeper.
    """
    if not os.path.exists(path) or not os.access(path, os.R_OK):
        return (0, 0, 0)
    
    try:
        entries = os.listdir(path)
    except (OSError, PermissionError):
        return (0, 0, 0)
    
    game_count = 0
    media_count = 0
    subdir_count = 0
    
    for entry in entries:
        entry_path = os.path.join(path, entry)
        entry_lower = entry.lower()
        
        if os.path.isdir(entry_path):
            subdir_count += 1
            continue
        
        # Check if it's a game file
        if any(entry_lower.endswith(ext) for ext in GAME_EXTENSIONS):
            game_count += 1
        # Check if it's a media file
        elif any(entry_lower.endswith(ext) for ext in BAD_EXTENSIONS):
            media_count += 1
    
    # If no games found but has subdirs, check common nested patterns
    if game_count == 0 and check_subdirs and subdir_count > 0:
        # Check for "roms" subdirectory (common RetroBat structure)
        roms_subdir = os.path.join(path, "roms")
        if os.path.exists(roms_subdir):
            nested_games, nested_media, _ = analyze_folder_content(roms_subdir, check_subdirs=False)
            if nested_games > 0:
                # Update path reference for better tracking
                game_count = nested_games
                media_count = nested_media
    
    return (game_count, media_count, subdir_count)


def score_folder(path: str) -> int:
    """
    Score a folder based on how likely it is to be a real ROM folder.
    Higher score = more likely to be the real deal.
    Returns -1 for definitely bad folders.
    """
    # Immediate disqualification
    if has_bad_keywords(path):
        return -1
    
    game_count, media_count, subdir_count = analyze_folder_content(path)
    
    # No games = not a ROM folder
    if game_count == 0:
        return -1
    
    score = 0
    
    # More games = better
    score += game_count * 10
    
    # Penalize if mostly media files
    if media_count > game_count * 5:
        score -= 50
    
    # Bonus if it has a reasonable amount of games
    if game_count > 10:
        score += 20
    if game_count > 50:
        score += 30
    if game_count > 100:
        score += 50
    
    # Slight penalty for having many subdirectories (might be organized media)
    if subdir_count > 5 and game_count < 5:
        score -= 20
    
    return score


def find_best_rom_folder(candidates: List[str]) -> Optional[str]:
    """
    Given multiple candidate paths, find the one most likely to be the ROM folder.
    Returns the actual path containing games (may be a subdirectory of the candidate).
    """
    if not candidates:
        return None
    
    scored = []
    for path in candidates:
        if not os.path.exists(path):
            continue
        
        score = score_folder(path)
        if score >= 0:  # Only consider non-disqualified folders
            game_count, media_count, _ = analyze_folder_content(path)
            
            # Track the actual path with games
            actual_path = path
            
            # If games are in a "roms" subdirectory, update the path
            if game_count > 0:
                roms_subdir = os.path.join(path, "roms")
                if os.path.exists(roms_subdir):
                    # Check if the games are actually in the subdir
                    sub_games, _, _ = analyze_folder_content(roms_subdir, check_subdirs=False)
                    if sub_games > 0:
                        actual_path = roms_subdir
                        game_count = sub_games
            
            scored.append((score, game_count, actual_path))
    
    if not scored:
        return None
    
    # Sort by score (descending), then by game count (descending)
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    
    return scored[0][2]


def safe_remove_link(path: str) -> bool:
    """Safely remove existing symlink or empty directory"""
    if not os.path.exists(path) and not os.path.islink(path):
        return True
    
    try:
        if os.path.islink(path):
            os.unlink(path)
            return True
        elif os.path.isdir(path):
            # Only remove if empty
            if not os.listdir(path):
                os.rmdir(path)
                return True
            else:
                print(f"   ⚠️  WARNING: {path} exists and is not empty. Skipping.")
                return False
        elif os.path.isfile(path):
            print(f"   ⚠️  WARNING: {path} is a file. Skipping.")
            return False
    except (OSError, PermissionError) as e:
        print(f"   ⚠️  WARNING: Could not remove {path}: {e}")
        return False
    
    return True


def link_roms(source: str, dest_name: str, dry_run: bool = False) -> bool:
    """Create ROM symlink"""
    dest = os.path.join(RD_ROMS, dest_name)
    
    if dry_run:
        print(f"   [DRY RUN] Would link: {source} -> {dest}")
        return True
    
    # Ensure parent directory exists
    os.makedirs(RD_ROMS, exist_ok=True)
    
    # Remove existing link/dir
    if not safe_remove_link(dest):
        return False
    
    try:
        os.symlink(source, dest)
        print(f"   ✅ Linked ROMs: {dest_name}")
        return True
    except (OSError, PermissionError) as e:
        print(f"   ❌ ERROR linking ROMs: {e}")
        return False


def link_media(source: str, dest_name: str, dry_run: bool = False) -> int:
    """Link media subfolders. Returns count of linked media types."""
    media_dest = os.path.join(RD_MEDIA, dest_name)
    
    if dry_run:
        print(f"   [DRY RUN] Would create media folder: {media_dest}")
    else:
        os.makedirs(media_dest, exist_ok=True)
    
    linked_count = 0
    
    # Look for media folders in source
    for src_name, dest_subname in MEDIA_MAP.items():
        src_full = os.path.join(source, src_name)
        
        if not os.path.exists(src_full):
            continue
        
        target = os.path.join(media_dest, dest_subname)
        
        if dry_run:
            print(f"   [DRY RUN] Would link media: {src_name} -> {dest_subname}")
            linked_count += 1
            continue
        
        if not safe_remove_link(target):
            continue
        
        try:
            os.symlink(src_full, target)
            linked_count += 1
        except (OSError, PermissionError) as e:
            print(f"   ⚠️  Could not link {src_name}: {e}")
    
    if linked_count > 0:
        print(f"   📁 Linked {linked_count} media folder(s)")
    
    return linked_count


def main():
    """Main execution"""
    print("=" * 60)
    print("🎮 KINHANK TO RETRODECK ROM MAPPER")
    print("=" * 60)
    
    if DRY_RUN:
        print("⚠️  DRY RUN MODE - No changes will be made")
        print()
    
    # Load directory structure
    all_paths = load_directory_map()
    print()
    
    # Group paths by basename for faster lookup
    path_groups = defaultdict(list)
    for path in all_paths:
        basename = os.path.basename(path).lower()
        path_groups[basename].append(path)
    
    stats = Stats()
    
    # Hunt for each system
    for rd_name, aliases in TARGETS.items():
        print(f"🔎 Hunting for: {rd_name}")
        
        # Find all candidate folders matching aliases
        candidates = []
        for alias in aliases:
            alias_lower = alias.lower()
            if alias_lower in path_groups:
                candidates.extend(path_groups[alias_lower])
        
        if not candidates:
            print(f"   ❌ No folders found matching: {aliases}")
            stats.skipped += 1
            continue
        
        print(f"   Found {len(candidates)} candidate folder(s)")
        
        # Find the best match
        winner = find_best_rom_folder(candidates)
        
        if winner:
            game_count, media_count, _ = analyze_folder_content(winner)
            print(f"   🎯 Selected: {winner}")
            print(f"   📊 Contains: {game_count} game files, {media_count} media files")
            
            # Link it
            if link_roms(winner, rd_name, DRY_RUN):
                stats.linked += 1
                stats.found += 1
                
                # Link media
                media_count = link_media(winner, rd_name, DRY_RUN)
                stats.media_linked += media_count
            else:
                stats.errors.append(f"{rd_name}: Failed to link")
        else:
            print(f"   ❌ No valid ROM folder found")
            stats.skipped += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Systems found: {stats.found}")
    print(f"🔗 Systems linked: {stats.linked}")
    print(f"📁 Media types linked: {stats.media_linked}")
    print(f"⏭️  Systems skipped: {stats.skipped}")
    
    if stats.errors:
        print(f"\n⚠️  ERRORS ({len(stats.errors)}):")
        for error in stats.errors:
            print(f"   - {error}")
    
    print()
    if not DRY_RUN:
        print("🎉 Done! Restart RetroDeck to see your games.")
    else:
        print("💡 Set DRY_RUN = False to apply changes.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)