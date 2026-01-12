# -*- mode: python ; coding: utf-8 -*-

import sys
import sysconfig
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None
project_dir = Path.cwd()
app_name = "test1"

datas = [
    (str(project_dir / "ui" / "main_window.ui"), "ui"),
    (str(project_dir / "assets" / "icon.png"), "assets"),
]

hiddenimports = collect_submodules("PySide6")

# --- Force-include Python stdlib extension modules on macOS ---
# Key: place them at top-level (".") so they are importable during earliest bootstrap.
extra_binaries = []
if sys.platform == "darwin":
    stdlib = Path(sysconfig.get_path("stdlib"))
    lib_dynload = stdlib / "lib-dynload"
    if lib_dynload.exists():
        for p in lib_dynload.glob("*.so"):
            extra_binaries.append((str(p), "."))  # <-- IMPORTANT (not "lib-dynload")

a = Analysis(
    ["app.py"],
    pathex=[str(project_dir)],
    binaries=extra_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],  # <-- remove runtime hook; too late for this failure
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if sys.platform == "darwin":
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=True,
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        name=app_name,
    )

    app = BUNDLE(
        coll,
        name=f"{app_name}.app",
        icon=str(project_dir / "assets" / "icon.icns"),
    )

elif sys.platform.startswith("win"):
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        icon=str(project_dir / "assets" / "icon.ico"),
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        name=app_name,
    )

else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        name=app_name,
    )

