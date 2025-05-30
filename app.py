from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        ui_file = QFile("window.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setCentralWidget(self.ui)
        self.resize(568, 288)
        self.setFixedSize(self.size())
        self.setWindowTitle("Explorerpatcher compatibility checker")

        self.checkCompatibility = self.ui.findChild(QPushButton, "checkCompatibility")
        self.autoDetect = self.ui.findChild(QPushButton, "autoDetect")

        if self.checkCompatibility:
            self.checkCompatibility.clicked.connect(self.checkCompat)

        if self.autoDetect:
            self.autoDetect.clicked.connect(self.autoDetecting)

    def checkCompat(self):
        print("Checking compatibility...")
        
    def autoDetecting(self):
        print("Auto-detecting...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
