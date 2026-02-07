#!/bin/bash
# Cleanup script - removes ALL contents of ~/retrodeck/roms/ for fresh linking
# Safe: Your Kinhank drive is never touched, only local RetroDeck folders

echo "🧹 RetroDeck ROM Folder Cleanup"
echo "========================================================================"
echo ""
echo "This will DELETE EVERYTHING in:"
echo "  • ~/retrodeck/roms/"
echo "  • ~/retrodeck/ES-DE/downloaded_media/"
echo ""
echo "⚠️  WARNING: This removes RetroDeck's default system folders too!"
echo "✅ SAFE: Your Kinhank drive is NOT touched (read-only)"
echo ""

# Show what's there
total_items=$(ls -A ~/retrodeck/roms/ 2>/dev/null | wc -l)
echo "Current items in ~/retrodeck/roms/: $total_items"
echo ""

read -p "💥 PROCEED WITH CLEANUP? [y/N] " -n 1 -r
echo
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🗑️  Removing all items from ~/retrodeck/roms/..."
    rm -rf ~/retrodeck/roms/*
    rm -rf ~/retrodeck/roms/.[!.]*  # Remove hidden files but not . and ..
    
    echo "🗑️  Cleaning media folder..."
    if [ -d ~/retrodeck/ES-DE/downloaded_media ]; then
        rm -rf ~/retrodeck/ES-DE/downloaded_media/*
    fi
    
    echo ""
    echo "✅ Cleanup complete! Folders are now empty."
    echo ""
    echo "📋 Next steps:"
    echo "   1. Run: python3 kinhank-simple.py --apply"
    echo "   2. Restart RetroDeck"
    echo ""
else
    echo "❌ Cancelled - no changes made"
fi
