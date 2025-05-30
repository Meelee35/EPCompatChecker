from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QMessageBox,
    QLineEdit,
    QLabel,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import QThread, Signal, Qt
from window_ui import Ui_window
import sys
import winreg
import requests
import ctypes
import traceback
import re
import keyring
from time import sleep

GITHUB_TOKEN = None

def enableDpiAwareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
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
    QApplication.quit()
    sys.exit(1)

sys.excepthook = globalExceptionHandler

def validate_github_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        return response.status_code == 200
    except Exception:
        return False

class CompatibilityChecker(QThread):
    finished = Signal(list)
    error = Signal(str)
    log = Signal(str)

    def __init__(self, build, parent=None):
        super().__init__(parent)
        self.build = build
        self.owner = "valinet"
        self.repo = "ExplorerPatcher"

    def run(self):
        global GITHUB_TOKEN
        try:
            page = 1
            foundReleases = []
            foundNewest = False

            if GITHUB_TOKEN:
                self.log.emit("Using GitHub token for authentication.")
                sleep(1)

            self.log.emit("Starting compatibility check...")

            while True:
                url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases?per_page=100&page={page}"
                headers = {}
                if GITHUB_TOKEN:
                    headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

                response = requests.get(url, headers=headers)
                response.raise_for_status()
                releases = response.json()
                if not releases:
                    self.log.emit("No more releases found.")
                    break

                for release in releases:
                    name = release.get("name", "")
                    body = release.get("body", "")
                    testedBuilds = self.checkReleaseCompatibility(body)
                    buildFromName = self.getBuildFromName(name)

                    self.log.emit(f"Working on release: {name} (builds: {testedBuilds})")

                    if self.build == buildFromName or self.build in testedBuilds:
                        foundReleases.append(release)
                        foundNewest = True

                if foundNewest:
                    break

                page += 1

            self.finished.emit(foundReleases)

        except Exception:
            error_msg = traceback.format_exc()
            self.log.emit("Error occurred:\n" + error_msg)
            self.error.emit(error_msg)

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

        self.ui = Ui_window()
        self.ui.setupUi(self)

        self.setFixedSize(self.size())
        self.setWindowTitle("ExplorerPatcher Compatibility Checker")

        self.checkCompatibilityButton = self.findChild(QPushButton, "checkCompatibility")
        self.autoDetectButton = self.findChild(QPushButton, "autoDetect")
        self.versionInput = self.findChild(QLineEdit, "versionInput")
        self.latestVersionLink = self.findChild(QLabel, "latestVersionLink")
        self.setTokenButton = self.findChild(QPushButton, "setToken")
        self.useTokenLabel = self.findChild(QLabel, "usingToken")
        self.foundVersionsList = self.findChild(QListWidget, "foundVersions")
        self.clearTokenButton = self.findChild(QPushButton, "clearToken")

        if self.clearTokenButton:
            self.clearTokenButton.clicked.connect(self.clearToken)

        if self.checkCompatibilityButton:
            self.checkCompatibilityButton.clicked.connect(
                lambda: self.checkCompatibility(self.versionInput.text().strip())
            )

        if self.autoDetectButton:
            self.autoDetectButton.clicked.connect(self.autoDetect)

        if self.latestVersionLink:
            self.latestVersionLink.setOpenExternalLinks(True)

        if self.setTokenButton:
            self.setTokenButton.clicked.connect(self.askForToken)
        
        if self.foundVersionsList:
            self.foundVersionsList.itemDoubleClicked.connect(self.listLinkClicked)
            self.foundVersionsList.setCursor(Qt.CursorShape.PointingHandCursor)
            self.foundVersionsList.setStyleSheet(
                """
                QListWidget {
                    color: lightblue;
                }
                """
            )

        self.loadToken()
        self.updateTokenLabel()
        
    def clearToken(self):
        global GITHUB_TOKEN
        GITHUB_TOKEN = keyring.get_password("ExplorerPatcherChecker", "github_token")
        if GITHUB_TOKEN:
            try:
                keyring.delete_password("ExplorerPatcherChecker", "github_token")
                GITHUB_TOKEN = None
                QMessageBox.information(
                    self,
                    "Token Cleared",
                    "GitHub token cleared successfully."
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Keyring Error",
                    f"Failed to clear token from keyring: {e}"
                )
        else:
            QMessageBox.information(
                self,
                "No Token Found",
                "No GitHub token found in keyring to clear."
            )
        self.updateTokenLabel()
        
    def loadToken(self):
        global GITHUB_TOKEN
        try:
            token = keyring.get_password("ExplorerPatcherChecker", "github_token")
            if token:
                GITHUB_TOKEN = token
        except Exception as e:
            print(f"Failed to load token from keyring: {e}")

    def updateTokenLabel(self):
        if self.useTokenLabel:
            if GITHUB_TOKEN:
                self.useTokenLabel.setText("Using GitHub token.")
            else:
                self.useTokenLabel.setText("Not using GitHub token.")

    def askForToken(self):
        loadChoice = QMessageBox.question(
            self,
            "Set GitHub Token",
            "Would you like to load your saved GitHub token from the keyring?\n"
            "If you haven't saved one yet, you can set it now by clicking 'No'.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )

        global GITHUB_TOKEN

        if loadChoice == QMessageBox.StandardButton.Cancel:
            return

        if loadChoice == QMessageBox.StandardButton.Yes:
            try:
                token = keyring.get_password("ExplorerPatcherChecker", "github_token")
                if token:
                    if validate_github_token(token):
                        GITHUB_TOKEN = token
                        QMessageBox.information(
                            self,
                            "Token Loaded",
                            "GitHub token loaded successfully from keyring and validated."
                        )
                        self.updateTokenLabel()
                        return
                    else:
                        QMessageBox.warning(
                            self,
                            "Invalid Token",
                            "The saved token in keyring is invalid. Please enter a new token."
                        )
                else:
                    QMessageBox.warning(
                        self,
                        "No Token Found",
                        "No GitHub token found in keyring. Please set a new token."
                    )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Keyring Error",
                    f"Failed to load token from keyring: {e}"
                )

        token, ok = QInputDialog.getText(
            self,
            "GitHub Token",
            "You can set a Github token if you want to avoid rate limits.\nThis is optional.",
            echo=QLineEdit.EchoMode.Password
        )
        if not ok or not token.strip():
            QMessageBox.warning(
                self,
                "Invalid Token",
                "You entered an empty token or cancelled. Please enter a valid GitHub token."
            )
            return

        if not validate_github_token(token.strip()):
            QMessageBox.warning(
                self,
                "Invalid Token",
                "The token you entered is invalid. Please try again."
            )
            return

        reply = QMessageBox.question(
            self,
            "Save Token",
            "Do you want to save this token for future use?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                keyring.set_password("ExplorerPatcherChecker", "github_token", token.strip())
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Keyring Error",
                    f"Failed to save token to keyring: {e}"
                )

        GITHUB_TOKEN = token.strip()
        self.updateTokenLabel()
        
    def listLinkClicked(self,item):
        print("List item clicked:", item.text())
        if item and item.toolTip():
            url = item.toolTip()
            if url.startswith("http"):
                import webbrowser
                webbrowser.open(url)
            else:
                QMessageBox.warning(self, "Invalid Link", "The link is not valid.")

    def logMessage(self, message):
        if self.latestVersionLink:
            self.latestVersionLink.setText(message)

    def checkCompatibility(self, build=None):
        if not build or not build.strip():
            QMessageBox.warning(
                self, "Input Required", "Please enter a Windows build version."
            )
            return

        if self.checkCompatibilityButton:
            self.checkCompatibilityButton.setEnabled(False)
        if self.versionInput:
            self.versionInput.setEnabled(False)
        if self.autoDetectButton:
            self.autoDetectButton.setEnabled(False)
        if self.latestVersionLink:
            self.latestVersionLink.setText("Checking...")

        self.worker = CompatibilityChecker(build)
        self.worker.log.connect(self.logMessage)
        self.worker.finished.connect(self.onCheckFinished)
        self.worker.error.connect(self.onCheckError)
        self.worker.start()

    def onCheckFinished(self, foundReleases):
        if self.checkCompatibilityButton:
            self.checkCompatibilityButton.setEnabled(True)
        if self.versionInput:
            self.versionInput.setEnabled(True)
        if self.autoDetectButton:
            self.autoDetectButton.setEnabled(True)

        if not foundReleases:
            if self.latestVersionLink:
                self.latestVersionLink.setText(
                    '<span style="color: red;">No compatible release found.</span>'
                )
            else:
                QMessageBox.information(
                    self, "No Release Found", "No compatible release found for this build."
                )
            self.foundVersionsList.clear()

        self.foundVersionsList.clear()

        for release in foundReleases:
            name = release.get("name", "Unknown")
            url = release.get("html_url", "#")
            item = QListWidgetItem(name)
            item.setToolTip(url)
            self.foundVersionsList.addItem(f"{release.get('tag_name', 'No tag')} ")
            self.foundVersionsList.item(self.foundVersionsList.count() - 1).setToolTip(url)

        if self.foundVersionsList.count() > 0:
            self.foundVersionsList.setCurrentRow(0)

        try: 
            firstRelease = foundReleases[0]
            name = firstRelease.get("name", "Unknown")
            url = firstRelease.get("html_url", "#")
            if self.latestVersionLink:
                self.latestVersionLink.setText(
                    f'<a href="{url}">Latest Release: {name}</a>'
                )
        except IndexError:
            if self.latestVersionLink:
                self.latestVersionLink.setText(
                    '<span style="color: red;">No releases found.</span>'
                )
            else:
                QMessageBox.information(
                    self, "No Release Found", "No releases found."
                )

    def onCheckError(self, error):
        if self.checkCompatibilityButton:
            self.checkCompatibilityButton.setEnabled(True)
        if self.versionInput:
            self.versionInput.setEnabled(True)
        if self.autoDetectButton:
            self.autoDetectButton.setEnabled(True)
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

