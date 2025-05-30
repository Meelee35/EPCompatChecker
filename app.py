from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QMessageBox,
    QLineEdit,
    QLabel
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QThread, Signal
import sys
import winreg
import requests
import ctypes
import traceback
import re
import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


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


class CompatibilityChecker(QThread):
    finished = Signal(dict)  # emits found release or empty dict if none found
    error = Signal(str)

    def __init__(self, build, parent=None):
        super().__init__(parent)
        self.build = build
        self.owner = "valinet"
        self.repo = "ExplorerPatcher"

    def run(self):
        try:
            page = 1
            foundRelease = None
            while True:
                url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases?per_page=100&page={page}"
                response = requests.get(url, auth=("Meelee35", GITHUB_TOKEN))
                response.raise_for_status()
                releases = response.json()
                if not releases:
                    break

                for release in releases:
                    name = release.get("name", "")
                    body = release.get("body", "")
                    testedBuilds = self.checkReleaseCompatibility(body)
                    buildFromName = self.getBuildFromName(name)

                    print(f"Checking release: {name}, tested builds: {testedBuilds}, build from name: {buildFromName}")
                    if self.build in testedBuilds or self.build == buildFromName:
                        foundRelease = release
                        break
                if foundRelease:
                    break
                page += 1

            self.finished.emit(foundRelease if foundRelease else {})
        except Exception as e:
            self.error.emit(str(e))

    def checkReleaseCompatibility(self, text):
        match = re.search(r"builds\s+([\d.,\s]+)", text, re.IGNORECASE)
        builds = []
        if match:
            buildsStr = match.group(1)
            builds = [b.strip() for b in re.split(r"[,\s]+", buildsStr) if b.strip()]
            return builds
        return []

    def getBuildFromName(self, version_name):
        parts = version_name.split('.')
        return '.'.join(parts[:2]) if len(parts) >= 2 else version_name


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
        self.latestVersionLink = self.ui.findChild(QLabel, "latestVersionLink")

        if self.checkCompatibilityButton:
            self.checkCompatibilityButton.clicked.connect(
                lambda: self.checkCompatibility(self.versionInput.text().strip())
            )

        if self.autoDetectButton:
            self.autoDetectButton.clicked.connect(self.autoDetect)
            
        if self.latestVersionLink:
            self.latestVersionLink.setOpenExternalLinks(True)

    def checkCompatibility(self, build=None):
        if not build:
            QMessageBox.warning(
                self, "Input Required", "Please enter a Windows build version."
            )
            return

        if self.checkCompatibilityButton:
            self.checkCompatibilityButton.setEnabled(False)

        self.worker = CompatibilityChecker(build)
        self.worker.finished.connect(self.onCheckFinished)
        self.worker.error.connect(self.onCheckError)
        self.worker.start()

    def onCheckFinished(self, foundRelease):
        if self.checkCompatibilityButton:
            self.checkCompatibilityButton.setEnabled(True)

        if foundRelease:
            name = foundRelease.get("name", "Unknown")
            url = foundRelease.get("html_url", "#")
            
            if self.latestVersionLink:
                self.latestVersionLink.setText(
                    f'<a href="{url}">Latest Release: {name}</a>'
                )
            else:
                QMessageBox.information(
                    self, "Release Found", f"Found release: {name}\n{url}"
                )
    
        else:
            if self.latestVersionLink:
                self.latestVersionLink.setText(
                    '<span style="color: red;">No compatible release found.</span>'
                )
            else:
                QMessageBox.information(
                    self, "No Release Found", "No compatible release found for this build."
                )

    def onCheckError(self, error):
        if self.checkCompatibilityButton:
            self.checkCompatibilityButton.setEnabled(True)
        showErrorPopup("Error during check", error)

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
