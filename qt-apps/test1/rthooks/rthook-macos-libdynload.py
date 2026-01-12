import sys
from pathlib import Path

# Ensure Python can import stdlib extension modules (e.g. _struct, _ssl, _hashlib)
# inside PyInstaller macOS .app bundles.
if sys.platform == "darwin" and getattr(sys, "frozen", False):
    exe = Path(sys.executable).resolve()
    # .../test1.app/Contents/MacOS/test1  -> Contents
    contents = exe.parents[1]
    frameworks = contents / "Frameworks"
    if frameworks.exists():
        # PyInstaller uses python3__dot__12; keep it flexible in case of minor changes
        for libdyn in sorted(frameworks.glob("python3__dot__*/lib-dynload")):
            sys.path.insert(0, str(libdyn))

