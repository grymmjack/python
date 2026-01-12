# Python + qt apps
These instructions explain how to setup and build python apps using qt and pyside

## Install packages
```sh
sudo apt update
sudo apt install -y \
  python3 \
  python3-venv \
  python3-pip \
  qt6-base-dev \
  qt6-tools-dev \
  qt6-tools-dev-tools \
  qt6-svg-dev

```

### Verify qt-designer is installed
`designer6`

## Create a new venv for app
```sh
mkdir -p ~/projects/myapp
cd ~/projects/myapp

python3 -m venv .venv
source .venv/bin/activate
```

## Setup venv to work with qt
```sh
pip install --upgrade pip
pip install PySide6 pyinstaller
```

### Verify venv is setup with qt
```sh
python -c "import PySide6; print(PySide6.__version__)"
```

### Confirm Designer <-> PySide compatibility
```sh
python - <<'EOF'
from PySide6.QtWidgets import QApplication, QLabel
import sys

app = QApplication(sys.argv)
label = QLabel("Qt + PySide6 is working")
label.show()
app.exec()
EOF
```

## Recommended project layout
```
myapp/
├── .venv/
├── app.py
├── ui/
│   └── main_window.ui
└── resources/
    └── icons/

```

## Create UI
```sh
designer6 ui/main_window.ui
```

### Example simple qt UI

#### `ui/main_window.ui`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="windowTitle">
   <string>My PySide6 App</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QVBoxLayout" name="verticalLayout">
    <item>
     <widget class="QLabel" name="lblTitle">
      <property name="text">
       <string>Hello from Qt Designer</string>
      </property>
      <property name="alignment">
       <set>Qt::AlignCenter</set>
      </property>
     </widget>
    </item>
    <item>
     <widget class="QLineEdit" name="txtName">
      <property name="placeholderText">
       <string>Enter your name…</string>
      </property>
     </widget>
    </item>
    <item>
     <widget class="QPushButton" name="btnGreet">
      <property name="text">
       <string>Greet Me</string>
      </property>
     </widget>
    </item>
    <item>
     <widget class="QLabel" name="lblResult">
      <property name="text">
       <string/>
      </property>
      <property name="alignment">
       <set>Qt::AlignCenter</set>
      </property>
     </widget>
    </item>
   </layout>
  </widget>
 </widget>
 <resources/>
 <connections/>
</ui>
```

### Example python app using simple qt UI

#### `app.py`

```python
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QLabel,
    QLineEdit,
    QMainWindow,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


def resource_path(*parts: str) -> str:
    """
    Get absolute path to a resource for dev and for PyInstaller onefile/onedir.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # PyInstaller temp dir
    else:
        base = Path(__file__).resolve().parent
    return str(base.joinpath(*parts))


def load_ui_mainwindow(path: str) -> QMainWindow:
    f = QFile(path)
    if not f.open(QFile.ReadOnly):
        raise RuntimeError(f"Could not open UI file: {path}")

    ui = QUiLoader().load(f, None)
    f.close()

    if ui is None:
        raise RuntimeError(f"Failed to load UI file: {path}")

    return ui


def main():
    app = QApplication(sys.argv)

    window = load_ui_mainwindow(resource_path("ui", "main_window.ui"))

    txt_name: QLineEdit = window.findChild(QLineEdit, "txtName")
    btn_greet: QPushButton = window.findChild(QPushButton, "btnGreet")
    lbl_result: QLabel = window.findChild(QLabel, "lblResult")

    def on_greet():
        name = (txt_name.text() or "").strip()
        lbl_result.setText(
            "Please enter a name 🙂" if not name else f"Hello, {name}!"
        )

    btn_greet.clicked.connect(on_greet)

    window.resize(400, 200)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### How to run example

From within sourced venv:

```sh
python app.py
```
i

## How to build PyInstaller executable
```sh
pyinstaller --noconfirm --clean \
  --windowed \
  --onefile \
  --name MyApp \
  --add-data "ui/main_window.ui:ui" \
  app.py
```

### How to make build repeatable for PyInstaller
```sh
pyinstaller \
  --name MyApp \
  --windowed \
  --add-data "ui/main_window.ui:ui" \
  app.py
```

This creates MyApp.spec. Then rebuild anytime with:

```sh
pyinstaller --noconfirm --clean MyApp.spec
```

## Create icons

Create a icon.png file and put it in `assets`

```
assets/
  icon.png      (at least 256x256)
  icon.ico      (Windows)
  icon.icns     (macOS)
```

```sh
sudo apt update
sudo apt install -y imagemagick icnsutils
```

### Create macOS icon
```sh
mkdir -p /tmp/icon.iconset
convert assets/icon.png -resize 16x16   /tmp/icon.iconset/icon_16x16.png
convert assets/icon.png -resize 32x32   /tmp/icon.iconset/icon_16x16@2x.png
convert assets/icon.png -resize 32x32   /tmp/icon.iconset/icon_32x32.png
convert assets/icon.png -resize 64x64   /tmp/icon.iconset/icon_32x32@2x.png
convert assets/icon.png -resize 128x128 /tmp/icon.iconset/icon_128x128.png
convert assets/icon.png -resize 256x256 /tmp/icon.iconset/icon_128x128@2x.png
convert assets/icon.png -resize 256x256 /tmp/icon.iconset/icon_256x256.png
convert assets/icon.png -resize 512x512 /tmp/icon.iconset/icon_256x256@2x.png
convert assets/icon.png -resize 512x512 /tmp/icon.iconset/icon_512x512.png
convert assets/icon.png -resize 1024x1024 /tmp/icon.iconset/icon_512x512@2x.png

iconutil -c icns /tmp/icon.iconset -o assets/icon.icns
```

### Create Windows .ico file
```sh
convert assets/icon.png -define icon:auto-resize=256,128,64,48,32,16 assets/icon.ico
```

## GitHub Workflow (`.github/workflows/release.yml`
```yaml
name: Release (PyInstaller)

on:
  push:
    tags:
      - "v*"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    name: Build ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.12"]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install PySide6 pyinstaller

      - name: Clean build output
        shell: bash
        run: |
          rm -rf build dist

      - name: Build (spec)
        run: |
          pyinstaller --noconfirm --clean test1.spec

      - name: Package release asset
        shell: bash
        run: |
          python - <<'PY'
          import os, re, zipfile, pathlib, platform

          APP = "test1"
          tag = os.environ.get("GITHUB_REF_NAME", "v0.0.0")

          m = re.match(r"^v(\d+\.\d+\.\d+.*)$", tag)
          ver = m.group(1) if m else tag

          runner_os = os.environ.get("RUNNER_OS", "").lower()
          if runner_os.startswith("windows"):
              os_name = "windows"
          elif runner_os.startswith("mac"):
              os_name = "macos"
          else:
              os_name = "linux"

          arch = platform.machine().lower()
          if arch in ("x86_64", "amd64"):
              arch = "x64"
          elif arch in ("aarch64", "arm64"):
              arch = "arm64"

          dist = pathlib.Path("dist")
          if not dist.exists():
              raise SystemExit("dist/ does not exist; build likely failed.")

          out_name = f"{APP}_{ver}_{os_name}_{arch}.zip"
          out_path = pathlib.Path(out_name)

          def add_path(zf: zipfile.ZipFile, p: pathlib.Path, arcbase: str):
              if p.is_dir():
                  for f in p.rglob("*"):
                      if f.is_file():
                          zf.write(f, f"{arcbase}/{f.relative_to(p)}")
              else:
                  zf.write(p, f"{arcbase}/{p.name}")

          targets = []
          app_bundle = dist / f"{APP}.app"
          if app_bundle.exists():
              targets = [app_bundle]
          else:
              exe = dist / (APP + (".exe" if os_name == "windows" else ""))
              targets = [exe] if exe.exists() else list(dist.iterdir())

          with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
              for t in targets:
                  add_path(zf, t, "dist")

          print(f"Created {out_path}")
          PY

      - name: Upload build artifact (for Release job)
        uses: actions/upload-artifact@v4
        with:
          name: release-${{ runner.os }}
          path: test1_*.zip

  release:
    name: Create GitHub Release + upload assets
    needs: build
    runs-on: ubuntu-latest

    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts

      - name: Publish Release
        uses: softprops/action-gh-release@v2
        with:
          files: |
            artifacts/**/test1_*.zip
          generate_release_notes: true

```

## Create release
```sh
git add test1.spec app.py assets .github/workflows/release.yml
git commit -m "Release workflow + platform builds"
git tag v0.1.0
git push origin main --tags
```

