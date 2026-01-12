# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

project_dir = Path(__file__).resolve().parent
app_name = "test1"

# Bundle your UI + a runtime icon png (for app.setWindowIcon)
datas = [
    (str(project_dir / "ui" / "main_window.ui"), "ui"),
    (str(project_dir / "assets" / "icon.png"), "assets"),
]

hiddenimports = collect_submodules("PySide6")

a = Analysis(
    ["app.py"],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if sys.platform == "darwin":
    # macOS: build into dist/test1.app
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
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
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
    # Windows: onefile dist/test1.exe with embedded .ico
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=str(project_dir / "assets" / "icon.ico"),
    )

else:
    # Linux: onefile dist/test1
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )

