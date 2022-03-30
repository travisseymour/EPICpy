# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'searchui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_DialogSearch(object):
    def setupUi(self, DialogSearch):
        if not DialogSearch.objectName():
            DialogSearch.setObjectName("DialogSearch")
        DialogSearch.setWindowModality(Qt.ApplicationModal)
        DialogSearch.resize(702, 245)
        DialogSearch.setMinimumSize(QSize(702, 242))
        DialogSearch.setMaximumSize(QSize(3000, 3000))
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        DialogSearch.setFont(font)
        DialogSearch.setModal(True)
        self.gridLayout = QGridLayout(DialogSearch)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(DialogSearch)
        self.label.setObjectName("label")
        font1 = QFont()
        font1.setFamily("Consolas")
        font1.setPointSize(14)
        font1.setBold(True)
        font1.setWeight(75)
        self.label.setFont(font1)

        self.verticalLayout.addWidget(self.label)

        self.plainTextEditSearchText = QPlainTextEdit(DialogSearch)
        self.plainTextEditSearchText.setObjectName("plainTextEditSearchText")
        self.plainTextEditSearchText.setFont(font)
        self.plainTextEditSearchText.setStyleSheet("")

        self.verticalLayout.addWidget(self.plainTextEditSearchText)

        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.checkBoxRegEx = QCheckBox(DialogSearch)
        self.checkBoxRegEx.setObjectName("checkBoxRegEx")
        self.checkBoxRegEx.setFont(font1)

        self.verticalLayout_2.addWidget(self.checkBoxRegEx)

        self.checkBoxIgnoreCase = QCheckBox(DialogSearch)
        self.checkBoxIgnoreCase.setObjectName("checkBoxIgnoreCase")
        self.checkBoxIgnoreCase.setFont(font1)

        self.verticalLayout_2.addWidget(self.checkBoxIgnoreCase)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(
            388, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButtonCancel = QPushButton(DialogSearch)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.pushButtonCancel.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButtonCancel)

        self.pushButtonSearch = QPushButton(DialogSearch)
        self.pushButtonSearch.setObjectName("pushButtonSearch")
        self.pushButtonSearch.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButtonSearch)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(DialogSearch)

        self.pushButtonSearch.setDefault(True)

        QMetaObject.connectSlotsByName(DialogSearch)

    # setupUi

    def retranslateUi(self, DialogSearch):
        DialogSearch.setWindowTitle(
            QCoreApplication.translate(
                "DialogSearch", "Specify Which Text To Search For", None
            )
        )
        self.label.setText(
            QCoreApplication.translate("DialogSearch", "Search For:", None)
        )
        self.checkBoxRegEx.setText(
            QCoreApplication.translate(
                "DialogSearch", "Treat as Regular Expression?", None
            )
        )
        self.checkBoxIgnoreCase.setText(
            QCoreApplication.translate("DialogSearch", "Ignore Case?", None)
        )
        self.pushButtonCancel.setText(
            QCoreApplication.translate("DialogSearch", "Cancel", None)
        )
        self.pushButtonSearch.setText(
            QCoreApplication.translate("DialogSearch", "Search", None)
        )

    # retranslateUi
