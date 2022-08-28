# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'statsui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_StatsWindow(object):
    def setupUi(self, StatsWindow):
        if not StatsWindow.objectName():
            StatsWindow.setObjectName("StatsWindow")
        StatsWindow.resize(660, 545)
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        StatsWindow.setFont(font)
        self.centralwidget = QWidget(StatsWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.statsTextBrowser = QTextBrowser(self.centralwidget)
        self.statsTextBrowser.setObjectName("statsTextBrowser")
        self.statsTextBrowser.setGeometry(QRect(10, 10, 640, 480))
        font1 = QFont()
        font1.setFamily("Consolas")
        font1.setPointSize(14)
        font1.setBold(True)
        font1.setWeight(75)
        self.statsTextBrowser.setFont(font1)
        self.statsTextBrowser.setAcceptDrops(False)
        self.statsTextBrowser.setOpenExternalLinks(True)
        StatsWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(StatsWindow)
        self.statusbar.setObjectName("statusbar")
        StatsWindow.setStatusBar(self.statusbar)

        self.retranslateUi(StatsWindow)

        QMetaObject.connectSlotsByName(StatsWindow)

    # setupUi

    def retranslateUi(self, StatsWindow):
        StatsWindow.setWindowTitle(
            QCoreApplication.translate("StatsWindow", "Stats Output Window", None)
        )

    # retranslateUi
