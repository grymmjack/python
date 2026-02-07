# Kinhank to RetroDeck ROM Mapper

Intelligent mapper for migrating Kinhank 12TB drive (RetroBat structure) to RetroDeck on Linux via symlinks.

## The Problem

The Kinhank drive has a complex structure with:
- Multiple folders with the same names (e.g., `snes`, `mame`)
- Real ROM folders contain `.zip`/`.iso` game files
- Fake folders contain artwork, bezels, and media files
- Windows-style naming that needs translation for Linux

This script intelligently detects which folders contain actual games and creates proper symlinks for RetroDeck.

## Features

- ✅ **Smart Detection**: Scores folders based on content (game files vs media files)
- ✅ **Comprehensive Systems**: Supports 60+ gaming systems
- ✅ **Media Linking**: Automatically links artwork, screenshots, videos
- ✅ **Dry Run Mode**: Preview changes before applying
- ✅ **Safe Operations**: Won't overwrite non-empty directories
- ✅ **Detailed Reporting**: Shows exactly what it found and linked

## Prerequisites

1. **Kinhank Drive Mounted**:
   ```bash
   # Verify your drive is mounted at:
   ls "/media/grymmjack/Super Game HDD/CORE - TYPE R"
   ```

2. **RetroDeck Installed** (via Flatpak):
   ```bash
   flatpak list | grep RetroDeck
   ```

3. **Python 3.8+**:
   ```bash
   python3 --version
   ```

## Setup

### Step 1: Generate Directory Map (Recommended)

This speeds up the process significantly:

```bash
cd ~/git/python/kinhank-to-retrodeck
find "/media/grymmjack/Super Game HDD/CORE - TYPE R" -type d > ~/kinhank-dirs.txt
```

This creates a text file with all directory paths on the drive.

### Step 2: Configure the Script

Edit `kinhank-to-retrodeck.py` and verify these paths:

```python
# Line 19-20: Your directory map
LIST_FILE = os.path.expanduser("~/kinhank-dirs.txt")

# Line 23: Direct path (if not using map file)
KINHANK_DRIVE = "/media/grymmjack/Super Game HDD/CORE - TYPE R"

# Line 26-27: RetroDeck paths (should be correct by default)
RD_ROMS = os.path.expanduser("~/retrodeck/roms")
RD_MEDIA = os.path.expanduser("~/retrodeck/ES-DE/downloaded_media")
```

## Usage

### Dry Run (Recommended First)

See what would happen without making changes:

```bash
cd ~/git/python/kinhank-to-retrodeck
python3 kinhank-to-retrodeck.py
```

**By default, the script runs in DRY RUN mode** (line 30: `DRY_RUN = True`)

Review the output carefully. It will show:
- Which folders it found for each system
- How many game files vs media files each contains
- Which folder it selected as the "real" ROM folder

### Apply Changes

If the dry run looks good, edit the script:

```python
# Line 30: Change this to False
DRY_RUN = False
```

Then run again:

```bash
python3 kinhank-to-retrodeck.py
```

### Restart RetroDeck

After linking:

```bash
flatpak run net.retrodeck.retrodeck
```

Or restart from the application menu.

## Configuration Options

### Add More Systems

Edit the `TARGETS` dictionary (starting at line 33):

```python
TARGETS = {
    "snes": ["snes", "supernintendo", "super nintendo"],
    # Add your custom systems:
    "custom": ["custom", "other names"],
}
```

### Adjust Detection Sensitivity

Edit the `score_folder()` function (line 220) to tune:
- How game files are weighted
- Media file penalties
- Minimum game thresholds

### Add More File Extensions

Edit `GAME_EXTENSIONS` (line 118) to recognize additional formats:

```python
GAME_EXTENSIONS = [
    ".zip", ".7z", ".rar",
    ".custom",  # Add your formats
]
```

## How It Works

1. **Load Directory Structure**: Reads `kinhank-dirs.txt` or scans drive
2. **Filter by Name**: Finds folders matching system aliases (e.g., "snes")
3. **Score Candidates**: Analyzes folder contents:
   - Counts game files (`.zip`, `.iso`, etc.)
   - Counts media files (`.png`, `.jpg`)
   - Checks for bad keywords ("bezel", "artwork")
   - Assigns a score (higher = more likely to be real ROM folder)
4. **Select Winner**: Picks the highest-scored folder
5. **Create Symlinks**: Links to `~/retrodeck/roms/[system]`
6. **Link Media**: Links artwork subfolders to `~/retrodeck/ES-DE/downloaded_media`

## Troubleshooting

### "No folders found matching"

The drive doesn't have that system, or it's named differently.

**Solution**: Add the actual folder name to the system's alias list in `TARGETS`.

### "No valid ROM folder found"

Multiple folders exist but none contain game files.

**Solution**: 
1. Check the candidates listed in output
2. Verify one contains `.zip` or game files
3. Adjust `GAME_EXTENSIONS` if needed

### "WARNING: path exists and is not empty"

The destination already has files.

**Solution**:
```bash
# Backup first!
mv ~/retrodeck/roms/snes ~/retrodeck/roms/snes.backup
# Then re-run the script
```

### Symlinks not showing in RetroDeck

Flatpak might not have permission to follow symlinks.

**Solution**:
```bash
flatpak override --user --filesystem=/media/grymmjack net.retrodeck.retrodeck
```

This grants RetroDeck access to your mounted drive.

### Drive gets mounted elsewhere

If your drive mounts at a different path:

**Solution**: Update `KINHANK_DRIVE` in the script or regenerate `kinhank-dirs.txt`.

## Output Examples

### Dry Run Output

```
🎮 KINHANK TO RETRODECK ROM MAPPER
⚠️  DRY RUN MODE - No changes will be made

📂 Loading directory map from: /home/grymmjack/kinhank-dirs.txt
   Loaded 15743 directories

🔎 Hunting for: snes
   Found 4 candidate folder(s)
   🎯 Selected: /media/.../CORE - TYPE R/collections/CONSOLES/roms/snes
   📊 Contains: 1247 game files, 0 media files
   [DRY RUN] Would link: /media/.../snes -> /home/grymmjack/retrodeck/roms/snes
   [DRY RUN] Would link media: boxart -> covers
   [DRY RUN] Would link media: screenshot -> screenshots

📊 SUMMARY
✅ Systems found: 45
🔗 Systems linked: 45
📁 Media types linked: 180
⏭️  Systems skipped: 15

💡 Set DRY_RUN = False to apply changes.
```

## Supported Systems

The script hunts for 60+ systems including:

**Nintendo**: NES, SNES, N64, GameCube, Wii, Wii U, Switch, GB, GBC, GBA, DS, 3DS  
**Sega**: Genesis, Master System, Saturn, Dreamcast, Game Gear, CD, 32X  
**Sony**: PS1, PS2, PS3, PSP, Vita  
**Microsoft**: Xbox, Xbox 360  
**Arcade**: MAME, Neo Geo, FBNeo, CPS1/2/3, NAOMI  
**Computers**: Amiga, C64, DOS, MSX, Atari ST, X68000  
**Other**: Atari 2600/5200/7800/Jaguar/Lynx, ColecoVision, Intellivision, PC Engine, WonderSwan, Vectrex, Virtual Boy, ZX Spectrum, Neo Geo Pocket

See `TARGETS` in the script for the complete list.

## Uninstalling/Reverting

To remove all symlinks:

```bash
# Remove ROM links
rm -rf ~/retrodeck/roms/*

# Remove media links
rm -rf ~/retrodeck/ES-DE/downloaded_media/*
```

The original files on your Kinhank drive remain untouched (read-only).

## Contributing

Found a system that's not detected? Edit `TARGETS` and `GAME_EXTENSIONS` and submit a PR!

## License

MIT License - Do whatever you want with it.

## Credits

Created for migrating Kinhank "Type R" drives to RetroDeck on Linux.

Based on research from the RetroDeck and Kinhank communities.
