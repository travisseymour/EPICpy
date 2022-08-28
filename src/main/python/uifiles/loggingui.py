# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'loggingui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_DialogLoggingSettings(object):
    def setupUi(self, DialogLoggingSettings):
        if not DialogLoggingSettings.objectName():
            DialogLoggingSettings.setObjectName("DialogLoggingSettings")
        DialogLoggingSettings.resize(708, 300)
        DialogLoggingSettings.setMinimumSize(QSize(708, 300))
        DialogLoggingSettings.setMaximumSize(QSize(3000, 3000))
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(12)
        DialogLoggingSettings.setFont(font)
        self.layoutWidget = QWidget(DialogLoggingSettings)
        self.layoutWidget.setObjectName("layoutWidget")
        self.layoutWidget.setGeometry(QRect(15, 16, 681, 273))
        self.layoutWidget.setFont(font)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.checkBoxLogNormalOut = QCheckBox(self.layoutWidget)
        self.checkBoxLogNormalOut.setObjectName("checkBoxLogNormalOut")
        font1 = QFont()
        font1.setFamily("Consolas")
        font1.setPointSize(12)
        font1.setBold(True)
        font1.setWeight(75)
        self.checkBoxLogNormalOut.setFont(font1)

        self.horizontalLayout_2.addWidget(self.checkBoxLogNormalOut)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.toolButtonNormalOut = QToolButton(self.layoutWidget)
        self.toolButtonNormalOut.setObjectName("toolButtonNormalOut")
        self.toolButtonNormalOut.setFont(font1)

        self.horizontalLayout_2.addWidget(self.toolButtonNormalOut)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.plainTextEditNormalOutFile = QPlainTextEdit(self.layoutWidget)
        self.plainTextEditNormalOutFile.setObjectName("plainTextEditNormalOutFile")
        self.plainTextEditNormalOutFile.setFont(font)
        self.plainTextEditNormalOutFile.setInputMethodHints(
            Qt.ImhMultiLine | Qt.ImhNoAutoUppercase
        )

        self.verticalLayout.addWidget(self.plainTextEditNormalOutFile)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.checkBoxLogTraceOut = QCheckBox(self.layoutWidget)
        self.checkBoxLogTraceOut.setObjectName("checkBoxLogTraceOut")
        self.checkBoxLogTraceOut.setFont(font1)

        self.horizontalLayout_3.addWidget(self.checkBoxLogTraceOut)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.toolButtonTraceOut = QToolButton(self.layoutWidget)
        self.toolButtonTraceOut.setObjectName("toolButtonTraceOut")
        self.toolButtonTraceOut.setFont(font1)

        self.horizontalLayout_3.addWidget(self.toolButtonTraceOut)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.plainTextEditTraceOutFile = QPlainTextEdit(self.layoutWidget)
        self.plainTextEditTraceOutFile.setObjectName("plainTextEditTraceOutFile")
        self.plainTextEditTraceOutFile.setFont(font)
        self.plainTextEditTraceOutFile.setInputMethodHints(
            Qt.ImhMultiLine | Qt.ImhNoAutoUppercase
        )

        self.verticalLayout.addWidget(self.plainTextEditTraceOutFile)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer_3 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.pushButtonCancel = QPushButton(self.layoutWidget)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.pushButtonCancel.setFont(font1)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.pushButtonCancel)

        self.pushButtonOK = QPushButton(self.layoutWidget)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.pushButtonOK.setFont(font1)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.pushButtonOK)

        self.horizontalLayout.addLayout(self.formLayout)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(DialogLoggingSettings)

        QMetaObject.connectSlotsByName(DialogLoggingSettings)

    # setupUi

    def retranslateUi(self, DialogLoggingSettings):
        DialogLoggingSettings.setWindowTitle(
            QCoreApplication.translate(
                "DialogLoggingSettings", "Output Logging Settings", None
            )
        )
        self.checkBoxLogNormalOut.setText(
            QCoreApplication.translate(
                "DialogLoggingSettings", "Log Normal Output?", None
            )
        )
        self.toolButtonNormalOut.setText(
            QCoreApplication.translate("DialogLoggingSettings", "...", None)
        )
        self.plainTextEditNormalOutFile.setPlainText("")
        self.checkBoxLogTraceOut.setText(
            QCoreApplication.translate(
                "DialogLoggingSettings", "Log Trace Output?", None
            )
        )
        self.toolButtonTraceOut.setText(
            QCoreApplication.translate("DialogLoggingSettings", "...", None)
        )
        self.plainTextEditTraceOutFile.setPlainText("")
        self.pushButtonCancel.setText(
            QCoreApplication.translate("DialogLoggingSettings", "Cancel", None)
        )
        self.pushButtonOK.setText(
            QCoreApplication.translate("DialogLoggingSettings", "OK", None)
        )

    # retranslateUi
