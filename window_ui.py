# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QWidget)

class Ui_window(object):
    def setupUi(self, window):
        if not window.objectName():
            window.setObjectName(u"window")
        window.setEnabled(True)
        window.resize(584, 355)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(window.sizePolicy().hasHeightForWidth())
        window.setSizePolicy(sizePolicy)
        window.setProperty(u"unifiedTitleAndToolBarOnMac", False)
        self.titel = QLabel(window)
        self.titel.setObjectName(u"titel")
        self.titel.setGeometry(QRect(50, 10, 471, 41))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(20)
        self.titel.setFont(font)
        self.titel.setTextFormat(Qt.AutoText)
        self.titel.setAlignment(Qt.AlignCenter)
        self.versionInput = QLineEdit(window)
        self.versionInput.setObjectName(u"versionInput")
        self.versionInput.setGeometry(QRect(60, 70, 351, 31))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(12)
        self.versionInput.setFont(font1)
        self.autoDetect = QPushButton(window)
        self.autoDetect.setObjectName(u"autoDetect")
        self.autoDetect.setGeometry(QRect(420, 70, 91, 31))
        self.autoDetect.setFont(font1)
        self.checkCompatibility = QPushButton(window)
        self.checkCompatibility.setObjectName(u"checkCompatibility")
        self.checkCompatibility.setGeometry(QRect(60, 110, 171, 31))
        self.checkCompatibility.setFont(font1)
        self.checkCompatibility.setAutoDefault(False)
        self.checkCompatibility.setFlat(False)
        self.latestVersionLink = QLabel(window)
        self.latestVersionLink.setObjectName(u"latestVersionLink")
        self.latestVersionLink.setGeometry(QRect(60, 180, 451, 31))
        font2 = QFont()
        font2.setPointSize(14)
        font2.setItalic(False)
        font2.setUnderline(True)
        font2.setKerning(True)
        font2.setStyleStrategy(QFont.PreferDefault)
        self.latestVersionLink.setFont(font2)
        self.latestVersionLink.setLineWidth(7)
        self.latestVersionLink.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.setToken = QPushButton(window)
        self.setToken.setObjectName(u"setToken")
        self.setToken.setGeometry(QRect(240, 110, 171, 31))
        self.setToken.setFont(font1)
        self.setToken.setAutoDefault(False)
        self.setToken.setFlat(False)
        self.usingToken = QLabel(window)
        self.usingToken.setObjectName(u"usingToken")
        self.usingToken.setGeometry(QRect(60, 150, 451, 21))
        font3 = QFont()
        font3.setPointSize(10)
        self.usingToken.setFont(font3)
        self.foundVersions = QListWidget(window)
        self.foundVersions.setObjectName(u"foundVersions")
        self.foundVersions.setGeometry(QRect(60, 210, 451, 131))
        sizePolicy.setHeightForWidth(self.foundVersions.sizePolicy().hasHeightForWidth())
        self.foundVersions.setSizePolicy(sizePolicy)
        font4 = QFont()
        font4.setPointSize(11)
        self.foundVersions.setFont(font4)
        self.foundVersions.setLineWidth(3)
        self.clearToken = QPushButton(window)
        self.clearToken.setObjectName(u"clearToken")
        self.clearToken.setGeometry(QRect(420, 110, 91, 31))
        self.clearToken.setFont(font1)
        self.clearToken.setAutoDefault(False)
        self.clearToken.setFlat(False)

        self.retranslateUi(window)

        QMetaObject.connectSlotsByName(window)
    # setupUi

    def retranslateUi(self, window):
        window.setWindowTitle(QCoreApplication.translate("window", u"Explorerpatcher compatibility checker", None))
        self.titel.setText(QCoreApplication.translate("window", u"Explorerpatcher Compatibility Checker", None))
        self.versionInput.setText("")
        self.versionInput.setPlaceholderText(QCoreApplication.translate("window", u"Type build number here", None))
        self.autoDetect.setText(QCoreApplication.translate("window", u"Auto Detect", None))
        self.checkCompatibility.setText(QCoreApplication.translate("window", u"Check Compatibility", None))
        self.latestVersionLink.setText("")
        self.setToken.setText(QCoreApplication.translate("window", u"API Token", None))
        self.usingToken.setText("")
        self.clearToken.setText(QCoreApplication.translate("window", u"Clear Token", None))
    # retranslateUi

