#!/bin/bash

# ================= CONFIGURATION =================
# We use the path that worked for COMPUTERS in your last run
KINHANK_ROOT="/media/grymmjack/Super Game HDD/CORE - TYPE R"
RD_ROMS="$HOME/retrodeck/roms"
RD_MEDIA="$HOME/retrodeck/ES-DE/downloaded_media"
# =================================================

echo "🚀 Starting Wildcard Migration..."

# 1. Loop through WHATEVER is inside the collections folder
#    (This bypasses the issue of guessing "CONSOLES" vs "Consoles")
SEARCH_ROOT="$KINHANK_ROOT/collections"

if [ ! -d "$SEARCH_ROOT" ]; then
    echo "❌ CRITICAL: Could not find 'collections' folder at: $SEARCH_ROOT"
    exit 1
fi

for COLLECTION_DIR in "$SEARCH_ROOT"/*; do
    if [ -d "$COLLECTION_DIR" ]; then
        DIR_NAME=$(basename "$COLLECTION_DIR")
        echo "-----------------------------------------------------"
        echo "📂 Inspecting Collection: '$DIR_NAME'"

        # 2. HUNT FOR THE ROMS
        # We look for a known system to identify the roms parent folder.
        ROMS_PARENT=""

        # Check A: Is this the CONSOLE collection? (Look for 'snes')
        # We search up to 6 levels deep to find where 'snes' is hiding.
        FOUND_SNES=$(find "$COLLECTION_DIR" -maxdepth 6 -type d -name "snes" -print -quit)
        
        # Check B: Is this the ARCADE collection? (Look for 'mame' or 'neogeo')
        FOUND_ARCADE=$(find "$COLLECTION_DIR" -maxdepth 6 -type d -name "mame" -print -quit)
        
        # Check C: Is this the COMPUTERS collection? (Look for 'amiga')
        FOUND_AMIGA=$(find "$COLLECTION_DIR" -maxdepth 6 -type d -name "amiga" -print -quit)

        # Logic to set the parent folder
        if [ -n "$FOUND_SNES" ]; then
            echo "   ✅ Identified as CONSOLES (Found snes)"
            ROMS_PARENT=$(dirname "$FOUND_SNES")
        elif [ -n "$FOUND_ARCADE" ]; then
            echo "   ✅ Identified as ARCADE (Found mame)"
            ROMS_PARENT=$(dirname "$FOUND_ARCADE")
        elif [ -n "$FOUND_AMIGA" ]; then
            echo "   ✅ Identified as COMPUTERS (Found amiga)"
            ROMS_PARENT=$(dirname "$FOUND_AMIGA")
        fi

        # 3. PERFORM THE LINKING
        if [ -n "$ROMS_PARENT" ]; then
            echo "   📍 Linking systems from: $ROMS_PARENT"
            
            for SYSTEM_PATH in "$ROMS_PARENT"/*; do
                if [ -d "$SYSTEM_PATH" ]; then
                    SYSTEM_NAME=$(basename "$SYSTEM_PATH")
                    
                    # Filter out non-game folders
                    [[ "$SYSTEM_NAME" =~ ^(bios|retrobat|hyperspin|emulators|collections)$ ]] && continue

                    # A. Link ROMs
                    ln -sfn "$SYSTEM_PATH" "$RD_ROMS/$SYSTEM_NAME"
                    
                    # B. Link Media
                    TARGET_MEDIA="$RD_MEDIA/$SYSTEM_NAME"
                    mkdir -p "$TARGET_MEDIA"

                    # Standard RetroBat names
                    [ -d "$SYSTEM_PATH/boxart" ] && ln -sfn "$SYSTEM_PATH/boxart" "$TARGET_MEDIA/covers"
                    [ -d "$SYSTEM_PATH/screenshot" ] && ln -sfn "$SYSTEM_PATH/screenshot" "$TARGET_MEDIA/screenshots"
                    [ -d "$SYSTEM_PATH/wheel" ] && ln -sfn "$SYSTEM_PATH/wheel" "$TARGET_MEDIA/marquees"
                    [ -d "$SYSTEM_PATH/video" ] && ln -sfn "$SYSTEM_PATH/video" "$TARGET_MEDIA/videos"
                    
                    # Hyperspin names (Just in case)
                    [ -d "$SYSTEM_PATH/images/artwork4" ] && ln -sfn "$SYSTEM_PATH/images/artwork4" "$TARGET_MEDIA/covers"
                    [ -d "$SYSTEM_PATH/images/artwork3" ] && ln -sfn "$SYSTEM_PATH/images/artwork3" "$TARGET_MEDIA/marquees"
                fi
            done
        else
            echo "   ⚠️  Skipping: Could not find familiar systems (snes/mame/amiga) inside."
        fi
    fi
done

echo "-----------------------------------------------------"
echo "🎉 DONE! Restart RetroDeck."