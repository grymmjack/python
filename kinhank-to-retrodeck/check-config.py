#!/usr/bin/env python3
"""
Configuration Checker for Kinhank to RetroDeck Mapper
Validates your setup before running the main script.
"""

import os
import sys

def check_mark(condition):
    return "✅" if condition else "❌"

def main():
    print("=" * 60)
    print("🔧 CONFIGURATION CHECKER")
    print("=" * 60)
    print()
    
    all_good = True
    
    # 1. Check for directory map file
    map_file = os.path.expanduser("~/kinhank-dirs.txt")
    map_exists = os.path.exists(map_file)
    print(f"{check_mark(map_exists)} Directory map file: {map_file}")
    if map_exists:
        with open(map_file, 'r') as f:
            line_count = sum(1 for _ in f)
        print(f"   📊 Contains {line_count:,} directories")
    else:
        print("   💡 Generate with:")
        print('   find "/media/grymmjack/Super Game HDD/CORE - TYPE R" -type d > ~/kinhank-dirs.txt')
        all_good = False
    print()
    
    # 2. Check for Kinhank drive
    kinhank_drive = "/media/grymmjack/Super Game HDD/CORE - TYPE R"
    drive_exists = os.path.exists(kinhank_drive)
    print(f"{check_mark(drive_exists)} Kinhank drive mounted: {kinhank_drive}")
    if not drive_exists:
        print("   ⚠️  Drive not found. Is it mounted?")
        print("   💡 Check with: ls -la /media/grymmjack/")
        all_good = False
    print()
    
    # 3. Check RetroDeck directories
    rd_roms = os.path.expanduser("~/retrodeck/roms")
    rd_roms_exists = os.path.exists(rd_roms)
    print(f"{check_mark(rd_roms_exists)} RetroDeck ROMs folder: {rd_roms}")
    if not rd_roms_exists:
        print("   ⚠️  Folder doesn't exist. Is RetroDeck installed?")
        print("   💡 It will be created automatically if RetroDeck is installed")
    
    rd_media = os.path.expanduser("~/retrodeck/ES-DE/downloaded_media")
    rd_media_exists = os.path.exists(rd_media)
    print(f"{check_mark(rd_media_exists)} RetroDeck media folder: {rd_media}")
    if not rd_media_exists:
        print("   💡 Will be created automatically")
    print()
    
    # 4. Check Python version
    py_version = sys.version_info
    py_ok = py_version >= (3, 8)
    print(f"{check_mark(py_ok)} Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    if not py_ok:
        print("   ⚠️  Python 3.8+ required")
        all_good = False
    print()
    
    # 5. Check for main script
    main_script = os.path.join(os.path.dirname(__file__), "kinhank-to-retrodeck.py")
    script_exists = os.path.exists(main_script)
    print(f"{check_mark(script_exists)} Main script: {main_script}")
    if not script_exists:
        print("   ❌ Script not found!")
        all_good = False
    print()
    
    # 6. Check Flatpak
    flatpak_check = os.system("flatpak list 2>/dev/null | grep -iq retrodeck") == 0
    print(f"{check_mark(flatpak_check)} RetroDeck Flatpak installed")
    if not flatpak_check:
        print("   ⚠️  RetroDeck not detected via Flatpak")
        print("   💡 Install with: flatpak install flathub net.retrodeck.retrodeck")
    print()
    
    # Summary
    print("=" * 60)
    if all_good and (map_exists or drive_exists):
        print("✅ READY TO GO!")
        print()
        print("Next steps:")
        if not map_exists and drive_exists:
            print("   1. Generate directory map (recommended):")
            print('      find "/media/grymmjack/Super Game HDD/CORE - TYPE R" -type d > ~/kinhank-dirs.txt')
            print("   2. Run the script:")
        else:
            print("   1. Run the script in dry-run mode:")
        print("      python3 kinhank-to-retrodeck.py")
        if not rd_roms_exists:
            print()
            print("⚠️  Note: RetroDeck folders don't exist yet.")
            print("   Run RetroDeck at least once to initialize them.")
    else:
        print("⚠️  SOME ISSUES NEED ATTENTION")
        print()
        print("Fix the items marked with ❌ above, then run this checker again.")
    print("=" * 60)

if __name__ == "__main__":
    main()
