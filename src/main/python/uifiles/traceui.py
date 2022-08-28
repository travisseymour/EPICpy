# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'traceui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from cachedplaintextedit import CachedPlainTextEdit


class Ui_TraceWindow(object):
    def setupUi(self, TraceWindow):
        if not TraceWindow.objectName():
            TraceWindow.setObjectName("TraceWindow")
        TraceWindow.resize(636, 635)
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        TraceWindow.setFont(font)
        self.centralwidget = QWidget(TraceWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.plainTextEditOutput = CachedPlainTextEdit(self.centralwidget)
        self.plainTextEditOutput.setObjectName("plainTextEditOutput")
        self.plainTextEditOutput.setGeometry(QRect(10, 10, 116, 101))
        self.plainTextEditOutput.setFont(font)
        self.plainTextEditOutput.setReadOnly(True)
        self.plainTextEditOutput.setCenterOnScroll(False)
        TraceWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(TraceWindow)
        self.statusbar.setObjectName("statusbar")
        TraceWindow.setStatusBar(self.statusbar)

        self.retranslateUi(TraceWindow)

        QMetaObject.connectSlotsByName(TraceWindow)

    # setupUi

    def retranslateUi(self, TraceWindow):
        TraceWindow.setWindowTitle(
            QCoreApplication.translate("TraceWindow", "Trace Output Window", None)
        )
        self.plainTextEditOutput.setDocumentTitle("")
        self.plainTextEditOutput.setPlainText(
            QCoreApplication.translate("TraceWindow", "Ready.", None)
        )

    # retranslateUi
