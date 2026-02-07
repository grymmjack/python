# Quick Start Guide

## TL;DR

```bash
# 1. Run dry-run mode (preview only)
cd ~/git/python/kinhank-to-retrodeck
python3 kinhank-simple.py

# 2. If output looks good, apply for real
python3 kinhank-simple.py --apply

# 3. Restart RetroDeck
flatpak run net.retrodeck.retrodeck
```

That's it! The script will automatically:
- ✅ Find all your ROM folders
- ✅ Create symlinks to RetroDeck
- ✅ Grant Flatpak permissions
- ✅ Tell you what to do next

## What to Expect

### First Run (Dry Run)

```
🎮 KINHANK TO RETRODECK - SIMPLE MAPPER
⚠️  DRY RUN MODE - No changes will be made
💡 Run with --apply to create symlinks

📂 Checking: retrobat
   ✅ Found
   🎮 snes (517+ games) -> snes
   [DRY RUN] Would link: .../RetroBat/roms/snes/roms -> ~/retrodeck/roms/snes
   ...

📊 SUMMARY
✅ Systems linked: 67

💡 Run with --apply to create the symlinks:
   python3 kinhank-simple.py --apply
```

**Check the output for**:
- ✅ "🎮 system (XXX+ games)" - Should show game counts
- ❌ "Not found" - Path issue, check KINHANK_BASE in script

### Second Run (Apply Mode)

Same output, but at the end:

```
📊 SUMMARY
✅ Systems linked: 67

🎉 Symlinks created!

🔐 Granting Flatpak permissions...
   ✅ Granted access to /media/grymmjack

🎮 Next steps:
   1. Restart RetroDeck:
      flatpak run net.retrodeck.retrodeck
   2. Your games should now appear in RetroDeck!

💾 Note: Your Kinhank drive was not modified (read-only).
```

## Common Issues

### ❌ "Not found"

**Problem**: Drive path doesn't match

**Fix**: Edit script line 12:
```python
KINHANK_BASE = "/your/actual/mount/path/CORE - TYPE R/collections/COMPUTERS/roms"
```

### ❌ RetroDeck shows no games

**Problem**: Flatpak permissions failed (rare)

**Fix**: Run manually:
```bash
flatpak override --user --filesystem=/media/grymmjack net.retrodeck.retrodeck
```

### ⚠️ Some systems have 0 games

**Problem**: Games might be in different format or deeper nesting

**Fix**: Check the folder manually:
```bash
ls "/media/grymmjack/Super Game HDD/.../RetroBat/roms/systemname/"
```

## Advanced Usage

### Add More Collections

Edit `ROM_PARENTS` in script (line 14):

```python
ROM_PARENTS = {
    "retrobat": os.path.join(KINHANK_BASE, "RetroBat/roms"),
    "mame": os.path.join(KINHANK_BASE, "HyperSpin Attraction/collections/Mame/roms"),
    "launchbox": os.path.join(KINHANK_BASE, "LaunchBox/Games"),  # Add this
}
```

### Custom System Names

Edit `SYSTEM_RENAMES` (line 26):

```python
SYSTEM_RENAMES = {
    "supernintendo": "snes",
    "megadrive": "genesis",
    "yoursystemname": "retrodeck-name",  # Add this
}
```

## Verification

After running, check the links:

```bash
# See what was linked
ls -la ~/retrodeck/roms/

# Check a specific system
ls ~/retrodeck/roms/snes/

# Verify it's a symlink
readlink ~/retrodeck/roms/snes

# Count games
ls ~/retrodeck/roms/snes/*.zip | wc -l
```

## Cleanup

Remove all symlinks (safe - doesn't touch Kinhank):

```bash
rm ~/retrodeck/roms/*
rm -r ~/retrodeck/ES-DE/downloaded_media/*
```

Your Kinhank drive remains untouched.

## Help

- Run `python3 kinhank-simple.py --help` for usage
- Check [README.md](README.md) for detailed info
- The script is read-only on your Kinhank drive - completely safe!
