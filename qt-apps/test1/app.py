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
from PySide6.QtGui import QIcon


def resource_path(*parts: str) -> str:
    """
    Absolute path to bundled resources.

    - Dev: relative to this file's directory
    - PyInstaller Win/Linux: sys._MEIPASS
    - PyInstaller macOS .app: Contents/Resources
    """
    if getattr(sys, "frozen", False):
        if sys.platform == "darwin":
            # sys.executable = .../test1.app/Contents/MacOS/test1
            contents = Path(sys.executable).resolve().parents[1]
            base = contents / "Resources"
        else:
            base = Path(getattr(sys, "_MEIPASS"))
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
    app.setWindowIcon(QIcon(resource_path("assets", "icon.png")))

    window = load_ui_mainwindow(resource_path("ui", "main_window.ui"))

    txt_name: QLineEdit = window.findChild(QLineEdit, "txtName")
    btn_greet: QPushButton = window.findChild(QPushButton, "btnGreet")
    lbl_result: QLabel = window.findChild(QLabel, "lblResult")

    def on_greet():
        name = (txt_name.text() or "").strip()
        lbl_result.setText("Please enter a name 🙂" if not name else f"Hello, {name}!")

    btn_greet.clicked.connect(on_greet)

    window.resize(400, 200)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

