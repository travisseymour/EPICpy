# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fontsizeui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from cachedplaintextedit import CachedPlainTextEdit


class Ui_DialogFontSize(object):
    def setupUi(self, DialogFontSize):
        if not DialogFontSize.objectName():
            DialogFontSize.setObjectName("DialogFontSize")
        DialogFontSize.setWindowModality(Qt.WindowModal)
        DialogFontSize.resize(800, 600)
        DialogFontSize.setMinimumSize(QSize(640, 480))
        DialogFontSize.setMaximumSize(QSize(2000, 2000))
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        DialogFontSize.setFont(font)
        DialogFontSize.setSizeGripEnabled(True)
        self.layoutWidget = QWidget(DialogFontSize)
        self.layoutWidget.setObjectName("layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 791, 581))
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName("label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")

        self.horizontalLayout_3.addWidget(self.label_4)

        self.spinBoxFontSize = QSpinBox(self.layoutWidget)
        self.spinBoxFontSize.setObjectName("spinBoxFontSize")
        font1 = QFont()
        font1.setFamily("Consolas")
        font1.setPointSize(20)
        font1.setBold(True)
        font1.setWeight(75)
        self.spinBoxFontSize.setFont(font1)

        self.horizontalLayout_3.addWidget(self.spinBoxFontSize)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.plainTextEditFontSample = CachedPlainTextEdit(self.layoutWidget)
        self.plainTextEditFontSample.setObjectName("plainTextEditFontSample")
        font2 = QFont()
        font2.setFamily("Consolas")
        font2.setPointSize(14)
        font2.setBold(True)
        font2.setWeight(75)
        self.plainTextEditFontSample.setFont(font2)
        self.plainTextEditFontSample.setReadOnly(True)
        self.plainTextEditFontSample.setCenterOnScroll(False)

        self.verticalLayout.addWidget(self.plainTextEditFontSample)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButtonCancel = QPushButton(self.layoutWidget)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.pushButtonCancel.setMinimumSize(QSize(100, 50))
        self.pushButtonCancel.setFont(font2)

        self.horizontalLayout_4.addWidget(self.pushButtonCancel)

        self.horizontalSpacer = QSpacerItem(
            308, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.pushButtonOK = QPushButton(self.layoutWidget)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.pushButtonOK.setMinimumSize(QSize(100, 50))
        self.pushButtonOK.setFont(font2)

        self.horizontalLayout_4.addWidget(self.pushButtonOK)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.retranslateUi(DialogFontSize)

        QMetaObject.connectSlotsByName(DialogFontSize)

    # setupUi

    def retranslateUi(self, DialogFontSize):
        DialogFontSize.setWindowTitle(
            QCoreApplication.translate("DialogFontSize", "Font Size Dialog", None)
        )
        self.label_3.setText(
            QCoreApplication.translate(
                "DialogFontSize",
                '<html><head/><body><p><span style=" font-size:20pt; font-weight:600;">Application Font Name: Consolas</span></p></body></html>',
                None,
            )
        )
        self.label_4.setText(
            QCoreApplication.translate(
                "DialogFontSize",
                '<html><head/><body><p><span style=" font-size:20pt; font-weight:600;">Application Font Size:</span></p></body></html>',
                None,
            )
        )
        self.plainTextEditFontSample.setDocumentTitle("")
        self.plainTextEditFontSample.setPlainText(
            QCoreApplication.translate(
                "DialogFontSize",
                "\u2139 loading device code from choice_device.py...\n"
                "\u2139 found EpicDevice class, creating new device instance based on this class.\n"
                "\n"
                "\u2611 Choice_Device_v2021.10.24 device was created successfully.\n"
                "\u2611 Model successfully initialized.\n"
                "\n"
                "\u250f\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2513\n"
                "\u2503 RULE FILE: choicetask_rules_VM.prs \u2503\n"
                "\u2517\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u251b\n"
                "",
                None,
            )
        )
        self.pushButtonCancel.setText(
            QCoreApplication.translate("DialogFontSize", "Cancel", None)
        )
        self.pushButtonOK.setText(
            QCoreApplication.translate("DialogFontSize", "OK", None)
        )

    # retranslateUi
