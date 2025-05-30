from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QMessageBox,
    QLineEdit,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys
import winreg
import requests
import ctypes
import traceback


def enableDpiAwareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Windows 8.1+
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # Windows Vista/7 fallback
        except Exception:
            pass


def showErrorPopup(title="Error", message="An error occurred."):
    enableDpiAwareness()
    if len(message) > 2000:
        message = message[:2000] + "\n\n[...traceback truncated]"
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x10 | 0x0)


def globalExceptionHandler(exctype, value, tb):
    errorMessage = "".join(traceback.format_exception(exctype, value, tb))
    print("Unhandled Exception:", errorMessage)
    showErrorPopup("Fatal Error", errorMessage)


# Set global exception hook before QApplication is created
sys.excepthook = globalExceptionHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        uiFile = QFile("window.ui")
        uiFile.open(QFile.ReadOnly)
        self.ui = loader.load(uiFile, self)
        uiFile.close()

        self.setCentralWidget(self.ui)
        self.resize(568, 288)
        self.setFixedSize(self.size())
        self.setWindowTitle("ExplorerPatcher Compatibility Checker")

        self.checkCompatibilityButton = self.ui.findChild(
            QPushButton, "checkCompatibility"
        )
        self.autoDetectButton = self.ui.findChild(QPushButton, "autoDetect")
        self.versionInput = self.ui.findChild(QLineEdit, "versionInput")

        if self.checkCompatibilityButton:
            self.checkCompatibilityButton.clicked.connect(self.checkCompatibility)

        if self.autoDetectButton:
            self.autoDetectButton.clicked.connect(self.autoDetect)

    def checkCompatibility(self): ...

    def autoDetect(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
            )
            version = winreg.QueryValueEx(key, "CurrentBuild")[0]
            ubr = winreg.QueryValueEx(key, "UBR")[0]
            winreg.CloseKey(key)
            print(f"Detected build version: {version}, UBR: {ubr}")
            self.versionInput.setText(f"{version}.{ubr}")
        except Exception as e:
            showErrorPopup(message=f"Failed to get version info:\n{e}")


if __name__ == "__main__":
    enableDpiAwareness()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
