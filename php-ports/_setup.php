<?php
$base_dir = getcwd();
$warnings = 0;
$warning_format = "\033[1;31m";
$notice_format = "\033[1;33m";
$success_format = "\033[1;32m";
$plain_format = "\033[0m";

$dirs = [
    'INSPIRATION' => 'L:\INSPIRATION',
    'MP3' => 'L:\MP3s',
    'SESSIONS' => 'L:\Sessions',
    'RENDERS' => 'L:\Renders',
    'SOUNDCLOUD' => 'L:\Soundcloud',
    'X - GJ SAMPLES' => 'L:\!Samples\!Grymmjack',
    'X - GJ LOOPS' => 'L:\!Loops\!GJ',
    'X - LOOPS' => 'L:\!Loops',
    'X - SAMPLES' => 'L:\!Samples',
    'X - DRUMS' => 'L:\!Drums',
    'X - FX' => 'L:\!FX',
    'X - MIDI' => 'L:\MIDI',
    'X - SOUNDFONTS' => 'L:\Soundfonts',
    'X - SFZ' => 'L:\SFZ',
    'X - IMPULSE RESPONSES' => 'L:\IRs',
    'X - WAVEFORMS' => 'L:\!Samples\!Waveforms',
    'X - WAVETABLES' => 'L:\!Wavetables',
    'GJ - KORG microSTATION Drums' => 'L:\!Drums\GJ - KORG microSTATION Drums',
    'GJ - MOTU BPM' => 'L:\!Drums\GJ - MOTU BPM v1.5',
    'GJ - YAMAHA DX200' => 'L:\!Drums\GJ - Yamaha DX200',
    'GJ - ROLAND XP-60' => 'L:\!Drums\GJ - Roland XP-60 Kits',
    'GJ - EPHONIC DRUMATIC' => 'L:\!Drums\EP - ephonic Drumatic Sampled Kits',
    'KORG - Gadget Samples' => 'X:\Gadget\factory samples',
    'KO - LOFI CINEMATIC GROOVES' => 'L:\!Loops\WAV\KO - LO-FI Cinematic Grooves',
    'UK - THE PRICE IS RIGHT' => 'L:\!Loops\WAV\UK - The Price is Right',
    'OP - OPTIGAN ARCHIVES VOL 1' => 'L:\!Samples\OP - Optigan Archives Vol. 1',
    'OP - OPTIGAN+ORCHESTRON+TM' => 'L:\!Samples\OP - Optigan-Orchestron-Talentmaker',
    'NS - ESSENTIAL DANCE DRUMS' => 'L:\!Drums\NS - Essential Dance',
    'NS - ESSENTIAL DANCE LOOPS' => 'L:\!Loops\WAV\NS - Essential Dance',
    'ZG - NOSTALGIA' => 'L:\!Samples\ZG - Nostalgia',
    'ZG - WORLD CLASS BREAKS' => 'L:\!Loops\WAV\ZG - World Class Breaks',
    'ZG - ELECTRO HOUSE' => 'L:\!Loops\WAV\ZG - Electro House',
    'ZG - PLANET BLISS' => 'L:\!Loops\WAV\ZG - Planet Bliss',
    'PH - REBIRTH MODS' => 'L:\!Samples\PH - Rebirth Mod Samples Sorted',
    'PH - REASON XCLUSIVE DRUMS' => 'L:\!Drums\!Reason xclusive drums',
    'BW - BITWIG FACTORY' => 'z:\Library\Bitwig Packages\Installed Bitwig Packs\1.0\samples',
    'BW - BITWIG DRUMS' => 'L:\!Drums\!Bitwig Drum Machines',
    'IL - FLSTUDIO' => 'L:\!Drums\FL - Factory',
    'IL - GROOVEMACHINE' => 'L:\!Drums\!Groovemachine Samples',
    'IL - SUPERDRUMS 8000' => 'L:\!Drums\SF - SuperDrums 8000',
    'IL - KILLER TWEAKS' => 'L:\!Drums\SF - Killer Tweaks Drums',
    'MGX - DRUMNBASS' => 'L:\!Loops\WAV\MGX - MusicMaker DrumNBass Drum Loops',
    'MGX - BEATBOX KiTS' => 'L:\!Drums\GJ - MGX - Magix BeatBox Kits',
    'MGX - ROBOTA' => 'L:\!Drums\GJ - MGX - Robota Samples',
    'APL - LOGIC DRUMS' => 'L:\Logic Drum Samples',
    'APL - ULTRABEAT' => 'L:\Ultrabeat Samples',
    'CM - SAMPLE LIBRARY' => 'M:\CM Sample Library',
    'FXP - GURU CM' => 'L:\!Drums\FX - GURU CM Factory',
    'NI - ABSYNTH' => 'C:\Program Files\Common Files\Native Instruments\Absynth 5\Samples',
    'NI - BATTERY4' => 'X:\Library\Battery 4 Factory Library\Samples',
    'NI - REAKTOR POLYPLEX' => 'L:\!Drums\!Polyplex',
    'NI - REAKTOR MASSIVE' => 'L:\!Drums\!Massive',
    'NI - REAKTOR LIMELITE' => 'L:\!Drums\!Limelite',
    'NI - REAKTOR SPLITTER' => 'L:\!Loops\WAV\NI - Reaktor Splitter Loops',
    'NI - REAKTOR RETROBEAT MK2' => 'L:\!Drums\!Retro Beat MK2',
    'SB - EGOIST' => 'Z:\Library\Egoist Library',
    'GM - CATARACT' => 'Z:\Library\GM_CATARACT\CATARACT_SAMPLES',
    'GM - POLYGON' => 'Z:\Library\GM_POLYGON\POLYGON_SAMPLES',
    'GM - CYBERNETICS (HITECH)' => 'L:\!Samples\GM - CYBERNETICS - High-Tech Sounds',
    'GM - EXPHORA (MUTATED)' => 'L:\!Samples\GM - EXOPHORA - Mutated Sounds',
    'GM - PROXIMITY (MODULAR)' => 'L:\!Samples\GM - PROXIMITY - Modular Synth Sounds',
    'GM - SEISM (IMPACTS)' => 'L:\!Samples\GM - SEISM - Hybrid Impacts',
    'GM - SHADOWS (HORROR)' => 'L:\!Samples\GM - SHADOWS - Horror Sounds',
    'GM - SPORE (SCIFI)' => 'L:\!Samples\GM - SPORE - SCI-FI Sounds',
    'GM - TERATOMA (TRANSITIONAL)' => 'L:\!Samples\GM - TERATOMA - Transitional Sounds',
    'HHR - AW1 (WHITE NOISE)' => 'L:\!Samples\HHR - Ambient Worlds Part 1 - White Noise',
    'HHR - AW2 (SOUNDSCAPE)' => 'L:\!Samples\HHR - Ambient Worlds Part 2 - Soundscape',
    'HHR - AW3 (ANOTHER WORLD)' => 'L:\!Samples\HHR - Ambient Worlds Part 3 - Another World',
    'HHR - EC1 (CIRCUIT BENDOMG)' => 'L:\!Samples\HHR - Electronic Critters 1 - Circuit Bending',
    'HHR - EC2 (AIRWAVES)' => 'L:\!Samples\HHR - Electronic Critters 2 - Airwaves',
    'HHR - EC3 (CREATURE WORKS)' => 'L:\!Samples\HHR - Electronic Critters 3 - Creaturephonic Workshop',
    'SC - TREMORS' => 'L:\!Loops\WAV\SC - Tremors vol. 1',
    'SC - ABSTRAKT BREAKS 1' => 'L:\!Loops\WAV\SC - Abstrakt Breaks 1',
    'SC - ABSTRAKT BREAKS 2' => 'L:\!Loops\WAV\SC - Abstrakt Breaks 2',
    'WA - DRUMTOOLS 01' => 'L:\!Drums\WA - Complete Drums\wa_drum_tools_01_deluxe',
    'WA - DRUMTOOLS 02' => 'L:\!Drums\WA - Complete Drums\wa_drum_tools_02',
    'WA - DRUM MACHINES' => 'L:\!Drums\WA - Complete Drums\wa_drum_machine_collection',
    'WA - 2 KEYBOARDS OF KICKS' => 'L:\!Drums\WA - Complete Drums\wa_2_keyboards_worth_of_kicks',
    'WA - CLAPS + STACKS' => 'L:\!Drums\WA - Complete Drums\wa_claps_and_stacks',
    'WA - DEEP HOUSE + GARAGE' => 'L:\!Drums\WA - Complete Drums\wa_deep_house_garage_drums',
    'WA - DEEP TECH + PROGRESSIVE' => 'L:\!Drums\WA - Complete Drums\wa_deep_tech_and_progressive_drums',
    'WA - FUTURE HOUSE' => 'L:\!Drums\WA - Complete Drums\wa_future_house_drums',
    'WA - PAPERSKIN SNARE TOOLKIT' => 'L:\!Drums\WA - Complete Drums\wa_paperskins_snare_toolkit',
    'WA - SYNCUSSION DRUMS' => 'L:\!Drums\WA - Complete Drums\wa_syncussion_drums',
    'WA - SYNTH DRUMS' => 'L:\!Drums\WA - Complete Drums\wa_synth_drums',
    'WA - TECH HOUSE + MINIMAL' => 'L:\!Drums\WA - Complete Drums\wa_tech_house_and_minimal_drums',
    'WA - ELECTROHOUSE PROG DRM' => 'L:\!Drums\WA - Electro House Progresions',
    'WA - ELECTROHOUSE PROG LPS' => 'L:\!Loops\REX\WA - Electro House Progressions',
    'WA - ELECTROHOUSE UNDER DRM' => 'L:\!Drums\WA - Electro House Underground',
    'WA - ELECTROHOUSE UNDER LPS' => 'L:\!Loops\REX\WA - Electro House Underground',
    'VG - DIRTY ELECTRO KICKS' => 'L:\!Drums\VG - Dirty Electro vol. 1 - Kicks',
    'KB6 - DRUM SYNTHS' => 'L:\!Drums\KB6 - Drum Synths'
];

$i = 1;
foreach ($dirs as $shortcut_name => $path) {
    $num = sprintf('%02d', $i);
    $check_exists = "{$base_dir}\\{$num} {$shortcut_name}";
    echo "Checking: {$check_exists}";
    if (file_exists("{$check_exists}")) {
        echo ": {$notice_format}EXISTS - skipping...{$plain_format}\n";
    } else {
        if (file_exists($path)) {
            $cmd = "mklink /D \"{$num} {$shortcut_name}\" \"{$path}\"";
            echo "{$success_format}{$cmd}{$plain_format}\n";
            system($cmd);
        } else {
            echo ": {$warning_format}WARNING: {$path} does not exist.{$plain_format}\n";
            $warnings++;
        }
    }
    $i++;
}
if ($warnings > 0) {
    echo "\n{$warning_format}WARNINGS: {$warnings}! {$plain_format}\n";
}
