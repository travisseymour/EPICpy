# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'devicesettingsui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_DialogDeviceOptions(object):
    def setupUi(self, DialogDeviceOptions):
        if not DialogDeviceOptions.objectName():
            DialogDeviceOptions.setObjectName("DialogDeviceOptions")
        DialogDeviceOptions.setWindowModality(Qt.ApplicationModal)
        DialogDeviceOptions.resize(482, 505)
        DialogDeviceOptions.setMinimumSize(QSize(482, 505))
        DialogDeviceOptions.setMaximumSize(QSize(3000, 3000))
        font = QFont()
        font.setPointSize(12)
        DialogDeviceOptions.setFont(font)
        DialogDeviceOptions.setModal(True)
        self.gridLayout = QGridLayout(DialogDeviceOptions)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelDeviceNameAndInfo = QLabel(DialogDeviceOptions)
        self.labelDeviceNameAndInfo.setObjectName("labelDeviceNameAndInfo")
        font1 = QFont()
        font1.setFamily("Consolas")
        font1.setPointSize(14)
        font1.setBold(True)
        font1.setWeight(75)
        self.labelDeviceNameAndInfo.setFont(font1)
        self.labelDeviceNameAndInfo.setWordWrap(True)

        self.verticalLayout.addWidget(self.labelDeviceNameAndInfo)

        self.listWidgetOptions = QListWidget(DialogDeviceOptions)
        self.listWidgetOptions.setObjectName("listWidgetOptions")
        font2 = QFont()
        font2.setFamily("Consolas")
        font2.setPointSize(14)
        self.listWidgetOptions.setFont(font2)

        self.verticalLayout.addWidget(self.listWidgetOptions)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(
            368, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButtonCancel = QPushButton(DialogDeviceOptions)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.pushButtonCancel.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButtonCancel)

        self.pushButtonOK = QPushButton(DialogDeviceOptions)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.pushButtonOK.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButtonOK)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(DialogDeviceOptions)

        self.pushButtonOK.setDefault(True)

        QMetaObject.connectSlotsByName(DialogDeviceOptions)

    # setupUi

    def retranslateUi(self, DialogDeviceOptions):
        DialogDeviceOptions.setWindowTitle(
            QCoreApplication.translate("DialogDeviceOptions", "Device Options", None)
        )
        self.labelDeviceNameAndInfo.setText(
            QCoreApplication.translate(
                "DialogDeviceOptions",
                "Device Options - There are No Options Exposed Here",
                None,
            )
        )
        self.pushButtonCancel.setText(
            QCoreApplication.translate("DialogDeviceOptions", "Cancel", None)
        )
        self.pushButtonOK.setText(
            QCoreApplication.translate("DialogDeviceOptions", "OK", None)
        )

    # retranslateUi
