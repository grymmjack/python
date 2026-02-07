#!/usr/bin/env python3
"""
Simple Kinhank to RetroDeck Mapper
Goes directly to known parent folders and links what's inside.

Usage:
    python3 kinhank-simple.py           # Dry run (preview only)
    python3 kinhank-simple.py --apply   # Actually create the links
"""

import os
import sys
import shutil
import argparse
import subprocess

# ================= CONFIGURATION =================
KINHANK_BASE = "/media/grymmjack/Super Game HDD/CORE - TYPE R/collections/COMPUTERS/roms"

# Known parent folders where ROMs live
ROM_PARENTS = {
    "retrobat": os.path.join(KINHANK_BASE, "RetroBat/roms"),
    "mame": os.path.join(KINHANK_BASE, "HyperSpin Attraction/collections/Mame/roms"),
    "teknoparrot": os.path.join(KINHANK_BASE, "Hyperspin TeknoParrot/collections/Teknoparrot/roms"),
}

# RetroDeck paths
RD_ROMS = os.path.expanduser("~/retrodeck/roms")
RD_MEDIA = os.path.expanduser("~/retrodeck/ES-DE/downloaded_media")

# System name mapping (Kinhank name -> RetroDeck name)
# If not in this map, use the folder name as-is
SYSTEM_RENAMES = {
    "supernintendo": "snes",
    "megadrive": "genesis",
    "ps1": "psx",
    "ps2": "ps2",
    "gamecube": "gc",
}

# Media folder mapping (Kinhank → RetroDeck)
# Different systems use different folder names, so we map all variations
MEDIA_MAP = {
    "boxart": "covers",       # Most RetroBat systems
    "images": "covers",       # Some systems use this instead (e.g., atari800)
    "logo": "covers",         # HyperSpin/MAME use this
    "screenshot": "screenshots", 
    "snap": "screenshots",    # HyperSpin/MAME use this
    "wheel": "marquees",
    "video": "videos",
    "videos": "videos",       # Some use plural (e.g., atari800)
}
# =================================================

def get_retrodeck_name(folder_name):
    """Convert Kinhank folder name to RetroDeck name"""
    lower_name = folder_name.lower()
    return SYSTEM_RENAMES.get(lower_name, lower_name)

def has_roms(path):
    """Check if a folder or its 'roms' subfolder contains game files
    If region folders exist, prefer USA/US region by default
    
    Detects ROMs by finding many files with the same extension (pattern-based)
    """
    # Known game extensions (high priority)
    known_game_exts = [
        ".zip", ".7z", ".rar", ".iso", ".cue", ".bin", ".chd",
        ".nds", ".3ds", ".cia", ".gba", ".gbc", ".gb", 
        ".sfc", ".smc", ".nes", ".n64", ".z64", ".md", ".gen",
    ]
    
    # Extensions to ignore (definitely not ROMs)
    ignore_exts = [".txt", ".xml", ".png", ".jpg", ".jpeg", ".gif", ".nfo", 
                   ".dat", ".ini", ".cfg", ".log", ".html", ".css", ".js"]
    
    def analyze_folder(folder_path):
        """Analyze a folder and determine if it contains ROMs
        Returns: (has_roms, extension_counts)
        """
        try:
            entries = os.listdir(folder_path)
            extension_counts = {}
            
            for entry in entries:
                if os.path.isfile(os.path.join(folder_path, entry)):
                    ext = os.path.splitext(entry.lower())[1]
                    if ext and ext not in ignore_exts:
                        extension_counts[ext] = extension_counts.get(ext, 0) + 1
            
            # Check for known game extensions first
            for ext in known_game_exts:
                if extension_counts.get(ext, 0) > 0:
                    return True, extension_counts
            
            # Check for pattern: if any extension appears 5+ times, likely ROMs
            for ext, count in extension_counts.items():
                if count >= 5:
                    return True, extension_counts
            
            return False, extension_counts
        except (OSError, PermissionError):
            return False, {}
    
    # Check the folder itself
    has_games, _ = analyze_folder(path)
    if has_games:
        # If this is a 'roms' folder, media is in parent
        if os.path.basename(path).lower() == 'roms':
            return True, path, os.path.dirname(path)
        else:
            return True, path, path
    
    # Check 'roms' subdirectory (RetroBat structure)
    roms_subdir = os.path.join(path, "roms")
    if os.path.isdir(roms_subdir):
        try:
            sub_entries = os.listdir(roms_subdir)
            
            # Check for direct ROM files in roms/
            has_games, _ = analyze_folder(roms_subdir)
            if has_games:
                # ROMs are flat - link to roms subfolder, parent for media
                return True, roms_subdir, path
            
            # Check for region folders (Europe, Japan, USA, etc.)
            region_folders = []
            for sub in sub_entries:
                sub_path = os.path.join(roms_subdir, sub)
                if os.path.isdir(sub_path):
                    has_games_in_region, ext_counts = analyze_folder(sub_path)
                    if has_games_in_region:
                        region_folders.append((sub, sub_path, sum(ext_counts.values())))
            
            if region_folders:
                # Prefer USA/US region
                usa_folder = None
                for name, folder_path, count in region_folders:
                    if name.upper() in ['USA', 'US']:
                        usa_folder = folder_path
                        break
                
                # Use USA if found, otherwise first region
                chosen_folder = usa_folder if usa_folder else region_folders[0][1]
                # Return: has_roms, rom_path, media_parent_path
                return True, chosen_folder, path
                
        except (OSError, PermissionError):
            pass
    
    return False, None, None

def safe_remove_link(path):
    """Safely remove existing symlink or directory to make way for new symlink"""
    if not os.path.exists(path) and not os.path.islink(path):
        return True
    
    try:
        if os.path.islink(path):
            os.unlink(path)
            return True
        elif os.path.isdir(path):
            # Remove directory (even if not empty) - RetroDeck creates default dirs
            shutil.rmtree(path)
            return True
        else:
            print(f"   ⚠️  {path} exists and is not a directory or symlink, skipping")
            return False
    except Exception as e:
        print(f"   ⚠️  Could not remove {path}: {e}")
        return False

def link_system(source_path, system_name, media_parent_path=None, dry_run=False):
    """Link a system folder to RetroDeck
    
    Args:
        source_path: Path to ROM files
        system_name: RetroDeck system name
        media_parent_path: Optional separate path for media files (boxart, etc.)
        dry_run: If True, only show what would be done
    """
    dest = os.path.join(RD_ROMS, system_name)
    
    if dry_run:
        print(f"   [DRY RUN] Would link: {source_path} -> {dest}")
        return True
    
    os.makedirs(RD_ROMS, exist_ok=True)
    
    if not safe_remove_link(dest):
        return False
    
    try:
        os.symlink(source_path, dest)
        print(f"   ✅ Linked: {system_name}")
        
        # Link media - use media_parent_path if provided, otherwise source_path parent
        media_source = media_parent_path if media_parent_path else os.path.dirname(source_path)
        media_dest = os.path.join(RD_MEDIA, system_name)
        os.makedirs(media_dest, exist_ok=True)
        
        for src_name, dest_name in MEDIA_MAP.items():
            src_media = os.path.join(media_source, src_name)
            if os.path.exists(src_media):
                media_link = os.path.join(media_dest, dest_name)
                safe_remove_link(media_link)
                try:
                    os.symlink(src_media, media_link)
                except:
                    pass
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def grant_flatpak_permissions():
    """Grant Flatpak permissions to access the Kinhank drive"""
    print("\n🔐 Granting Flatpak permissions...")
    
    # Get the actual mount point from KINHANK_BASE
    mount_point = "/media/grymmjack"
    
    cmd = [
        "flatpak", "override", "--user",
        f"--filesystem={mount_point}",
        "net.retrodeck.retrodeck"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"   ✅ Granted access to {mount_point}")
            return True
        else:
            print(f"   ⚠️  Could not grant permissions: {result.stderr}")
            print(f"   💡 Run manually: flatpak override --user --filesystem={mount_point} net.retrodeck.retrodeck")
            return False
    except subprocess.TimeoutExpired:
        print("   ⚠️  Command timed out")
        return False
    except FileNotFoundError:
        print("   ⚠️  Flatpak not found - is RetroDeck installed via Flatpak?")
        return False
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        return False


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Map Kinhank drive ROMs to RetroDeck via symlinks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 kinhank-simple.py           # Preview what would be linked (dry run)
  python3 kinhank-simple.py --apply   # Actually create the symlinks
        """
    )
    parser.add_argument(
        '--apply', 
        action='store_true',
        help='Apply changes (create symlinks). Without this flag, runs in dry-run mode.'
    )
    
    args = parser.parse_args()
    dry_run = not args.apply
    
    print("=" * 70)
    print("🎮 KINHANK TO RETRODECK - SIMPLE MAPPER")
    print("=" * 70)
    
    if dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made")
        print("💡 Run with --apply to create symlinks\n")
    else:
        print("🚀 APPLY MODE - Creating symlinks...\n")
    
    linked_count = 0
    
    # Process each parent folder
    for parent_name, parent_path in ROM_PARENTS.items():
        print(f"\n📂 Checking: {parent_name}")
        print(f"   Path: {parent_path}")
        
        if not os.path.exists(parent_path):
            print(f"   ❌ Not found, skipping")
            continue
        
        print(f"   ✅ Found")
        
        # Special case for MAME - link the whole folder
        if parent_name == "mame":
            has_games, actual_path, media_parent = has_roms(parent_path)
            if has_games:
                print(f"   🎯 Found MAME ROMs")
                if link_system(actual_path or parent_path, "mame", media_parent, dry_run):
                    linked_count += 1
            continue
        
        # Special case for TeknoParrot
        if parent_name == "teknoparrot":
            has_games, actual_path, media_parent = has_roms(parent_path)
            if has_games:
                print(f"   🎯 Found TeknoParrot ROMs")
                # TeknoParrot might not have a standard RetroDeck mapping
                # Just link it for now
                if link_system(actual_path or parent_path, "teknoparrot", media_parent, dry_run):
                    linked_count += 1
            continue
        
        # For RetroBat and others: list subdirectories
        try:
            subdirs = [d for d in os.listdir(parent_path) 
                      if os.path.isdir(os.path.join(parent_path, d))]
            
            # Filter out junk folders
            subdirs = [d for d in subdirs 
                      if d.lower() not in ["bios", "saves", "screenshots", "bezels_project", 
                                          "decorations", "cheats", "emulators", 
                                          "emulationstation", "library", "records"]]
            
            print(f"   Found {len(subdirs)} system folders")
            
            for subdir in sorted(subdirs):
                full_path = os.path.join(parent_path, subdir)
                
                # Check if it has ROMs
                has_games, actual_path, media_parent = has_roms(full_path)
                
                if has_games:
                    rd_name = get_retrodeck_name(subdir)
                    
                    # Count games quickly
                    try:
                        rom_path = actual_path or full_path
                        # Count all files, excluding common non-game extensions
                        game_count = 0
                        ignore_exts = {'.txt', '.xml', '.png', '.jpg', '.jpeg', '.gif', 
                                      '.nfo', '.dat', '.ini', '.cfg', '.log'}
                        
                        for root, dirs, files in os.walk(rom_path):
                            for f in files:
                                ext = os.path.splitext(f.lower())[1]
                                if ext and ext not in ignore_exts:
                                    game_count += 1
                            if game_count > 100:  # Stop counting at 100
                                break
                        
                        # Show region if linking to subfolder
                        if actual_path != full_path:
                            region = os.path.basename(actual_path)
                            print(f"   🎮 {subdir} ({game_count}+ games, {region} region) -> {rd_name}")
                        else:
                            print(f"   🎮 {subdir} ({game_count}+ games) -> {rd_name}")
                        
                        if link_system(actual_path or full_path, rd_name, media_parent, dry_run):
                            linked_count += 1
                    except:
                        print(f"   🎮 {subdir} -> {rd_name}")
                        if link_system(actual_path or full_path, rd_name, media_parent, dry_run):
                            linked_count += 1
                            
        except Exception as e:
            print(f"   ❌ Error reading folder: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"✅ Systems linked: {linked_count}")
    
    if dry_run:
        print("\n💡 Run with --apply to create the symlinks:")
        print("   python3 kinhank-simple.py --apply")
    else:
        print("\n🎉 Symlinks created!")
        
        # Grant Flatpak permissions
        grant_flatpak_permissions()
        
        print("\n🎮 Next steps:")
        print("   1. Restart RetroDeck:")
        print("      flatpak run net.retrodeck.retrodeck")
        print("   2. Your games should now appear in RetroDeck!")
        print("\n💾 Note: Your Kinhank drive was not modified (read-only).")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
