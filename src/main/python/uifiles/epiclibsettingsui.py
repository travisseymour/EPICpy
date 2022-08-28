# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'epiclibsettingsui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_DialogEPICLibSettings(object):
    def setupUi(self, DialogEPICLibSettings):
        if not DialogEPICLibSettings.objectName():
            DialogEPICLibSettings.setObjectName("DialogEPICLibSettings")
        DialogEPICLibSettings.setWindowModality(Qt.ApplicationModal)
        DialogEPICLibSettings.resize(482, 352)
        DialogEPICLibSettings.setMinimumSize(QSize(482, 352))
        DialogEPICLibSettings.setMaximumSize(QSize(3000, 3000))
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(12)
        DialogEPICLibSettings.setFont(font)
        DialogEPICLibSettings.setModal(True)
        self.layoutWidget = QWidget(DialogEPICLibSettings)
        self.layoutWidget.setObjectName("layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 461, 331))
        self.layoutWidget.setFont(font)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.labelInfo = QLabel(self.layoutWidget)
        self.labelInfo.setObjectName("labelInfo")
        font1 = QFont()
        font1.setFamily("Consolas")
        font1.setPointSize(14)
        self.labelInfo.setFont(font1)
        self.labelInfo.setWordWrap(True)

        self.verticalLayout.addWidget(self.labelInfo)

        self.listWidgetOptions = QListWidget(self.layoutWidget)
        self.listWidgetOptions.setObjectName("listWidgetOptions")
        self.listWidgetOptions.setFont(font1)

        self.verticalLayout.addWidget(self.listWidgetOptions)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(
            368, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButtonCancel = QPushButton(self.layoutWidget)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        font2 = QFont()
        font2.setFamily("Consolas")
        font2.setPointSize(14)
        font2.setBold(True)
        font2.setWeight(75)
        self.pushButtonCancel.setFont(font2)

        self.horizontalLayout.addWidget(self.pushButtonCancel)

        self.pushButtonOK = QPushButton(self.layoutWidget)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.pushButtonOK.setFont(font2)

        self.horizontalLayout.addWidget(self.pushButtonOK)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(DialogEPICLibSettings)

        self.pushButtonOK.setDefault(True)

        QMetaObject.connectSlotsByName(DialogEPICLibSettings)

    # setupUi

    def retranslateUi(self, DialogEPICLibSettings):
        DialogEPICLibSettings.setWindowTitle(
            QCoreApplication.translate(
                "DialogEPICLibSettings", "EPICLib Settings", None
            )
        )
        self.labelInfo.setText(
            QCoreApplication.translate(
                "DialogEPICLibSettings",
                "Which EPICLib Version Should Be Used (Requires App Restart)",
                None,
            )
        )
        self.pushButtonCancel.setText(
            QCoreApplication.translate("DialogEPICLibSettings", "Cancel", None)
        )
        self.pushButtonOK.setText(
            QCoreApplication.translate("DialogEPICLibSettings", "OK", None)
        )

    # retranslateUi
