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
            DialogSearch.setObjectName(u"DialogSearch")
        DialogSearch.setWindowModality(Qt.ApplicationModal)
        DialogSearch.resize(702, 245)
        DialogSearch.setMinimumSize(QSize(702, 242))
        DialogSearch.setMaximumSize(QSize(3000, 3000))
        font = QFont()
        font.setFamily(u"Consolas")
        font.setPointSize(14)
        DialogSearch.setFont(font)
        DialogSearch.setModal(True)
        self.gridLayout = QGridLayout(DialogSearch)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(DialogSearch)
        self.label.setObjectName(u"label")
        font1 = QFont()
        font1.setFamily(u"Consolas")
        font1.setPointSize(14)
        font1.setBold(True)
        font1.setWeight(75)
        self.label.setFont(font1)

        self.verticalLayout.addWidget(self.label)

        self.lineEditSearchText = QLineEdit(DialogSearch)
        self.lineEditSearchText.setObjectName(u"lineEditSearchText")
        self.lineEditSearchText.setClearButtonEnabled(True)

        self.verticalLayout.addWidget(self.lineEditSearchText)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.checkBoxRegEx = QCheckBox(DialogSearch)
        self.checkBoxRegEx.setObjectName(u"checkBoxRegEx")
        self.checkBoxRegEx.setFont(font1)

        self.verticalLayout_2.addWidget(self.checkBoxRegEx)

        self.checkBoxIgnoreCase = QCheckBox(DialogSearch)
        self.checkBoxIgnoreCase.setObjectName(u"checkBoxIgnoreCase")
        self.checkBoxIgnoreCase.setFont(font1)

        self.verticalLayout_2.addWidget(self.checkBoxIgnoreCase)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(388, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButtonCancel = QPushButton(DialogSearch)
        self.pushButtonCancel.setObjectName(u"pushButtonCancel")
        self.pushButtonCancel.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButtonCancel)

        self.pushButtonSearchBackward = QPushButton(DialogSearch)
        self.pushButtonSearchBackward.setObjectName(u"pushButtonSearchBackward")
        self.pushButtonSearchBackward.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButtonSearchBackward)

        self.pushButtonSearchForward = QPushButton(DialogSearch)
        self.pushButtonSearchForward.setObjectName(u"pushButtonSearchForward")
        self.pushButtonSearchForward.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButtonSearchForward)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)


        self.retranslateUi(DialogSearch)

        self.pushButtonSearchBackward.setDefault(False)
        self.pushButtonSearchForward.setDefault(True)


        QMetaObject.connectSlotsByName(DialogSearch)
    # setupUi

    def retranslateUi(self, DialogSearch):
        DialogSearch.setWindowTitle(QCoreApplication.translate("DialogSearch", u"Specify Which Text To Search For", None))
        self.label.setText(QCoreApplication.translate("DialogSearch", u"Search For:", None))
        self.checkBoxRegEx.setText(QCoreApplication.translate("DialogSearch", u"Treat as Regular Expression?", None))
        self.checkBoxIgnoreCase.setText(QCoreApplication.translate("DialogSearch", u"Ignore Case?", None))
        self.pushButtonCancel.setText(QCoreApplication.translate("DialogSearch", u"Cancel", None))
        self.pushButtonSearchBackward.setText(QCoreApplication.translate("DialogSearch", u"Search\n"
"Backward", None))
        self.pushButtonSearchForward.setText(QCoreApplication.translate("DialogSearch", u"Search\n"
"Forward", None))
    # retranslateUi

