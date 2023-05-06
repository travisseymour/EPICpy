# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tracesettingsui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_DialogTraceSettings(object):
    def setupUi(self, DialogTraceSettings):
        if not DialogTraceSettings.objectName():
            DialogTraceSettings.setObjectName("DialogTraceSettings")
        DialogTraceSettings.resize(231, 326)
        DialogTraceSettings.setMinimumSize(QSize(231, 297))
        DialogTraceSettings.setMaximumSize(QSize(2000, 2000))
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        DialogTraceSettings.setFont(font)
        DialogTraceSettings.setSizeGripEnabled(True)
        self.gridLayout = QGridLayout(DialogTraceSettings)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBoxVisual = QCheckBox(DialogTraceSettings)
        self.checkBoxVisual.setObjectName("checkBoxVisual")
        self.checkBoxVisual.setFont(font)

        self.verticalLayout.addWidget(self.checkBoxVisual)

        self.checkBoxTemporal = QCheckBox(DialogTraceSettings)
        self.checkBoxTemporal.setObjectName("checkBoxTemporal")
        self.checkBoxTemporal.setFont(font)

        self.verticalLayout.addWidget(self.checkBoxTemporal)

        self.checkBoxVocal = QCheckBox(DialogTraceSettings)
        self.checkBoxVocal.setObjectName("checkBoxVocal")
        self.checkBoxVocal.setFont(font)

        self.verticalLayout.addWidget(self.checkBoxVocal)

        self.checkBoxCognitive = QCheckBox(DialogTraceSettings)
        self.checkBoxCognitive.setObjectName("checkBoxCognitive")
        self.checkBoxCognitive.setFont(font)

        self.verticalLayout.addWidget(self.checkBoxCognitive)

        self.checkBoxDevice = QCheckBox(DialogTraceSettings)
        self.checkBoxDevice.setObjectName("checkBoxDevice")
        self.checkBoxDevice.setFont(font)

        self.verticalLayout.addWidget(self.checkBoxDevice)

        self.checkBoxManual = QCheckBox(DialogTraceSettings)
        self.checkBoxManual.setObjectName("checkBoxManual")
        self.checkBoxManual.setFont(font)

        self.verticalLayout.addWidget(self.checkBoxManual)

        self.checkBoxOcular = QCheckBox(DialogTraceSettings)
        self.checkBoxOcular.setObjectName("checkBoxOcular")
        self.checkBoxOcular.setFont(font)

        self.verticalLayout.addWidget(self.checkBoxOcular)

        self.checkBoxAuditory = QCheckBox(DialogTraceSettings)
        self.checkBoxAuditory.setObjectName("checkBoxAuditory")
        self.checkBoxAuditory.setFont(font)

        self.verticalLayout.addWidget(self.checkBoxAuditory)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonCancel = QPushButton(DialogTraceSettings)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        font1 = QFont()
        font1.setFamily("Consolas")
        font1.setPointSize(14)
        font1.setBold(True)
        font1.setWeight(75)
        self.pushButtonCancel.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButtonCancel)

        self.pushButtonOK = QPushButton(DialogTraceSettings)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.pushButtonOK.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButtonOK)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(DialogTraceSettings)

        self.pushButtonOK.setDefault(True)

        QMetaObject.connectSlotsByName(DialogTraceSettings)

    # setupUi

    def retranslateUi(self, DialogTraceSettings):
        DialogTraceSettings.setWindowTitle(
            QCoreApplication.translate("DialogTraceSettings", "Trace Settings", None)
        )
        self.checkBoxVisual.setText(
            QCoreApplication.translate("DialogTraceSettings", "Visual", None)
        )
        self.checkBoxTemporal.setText(
            QCoreApplication.translate("DialogTraceSettings", "Temporal", None)
        )
        self.checkBoxVocal.setText(
            QCoreApplication.translate("DialogTraceSettings", "Vocal", None)
        )
        self.checkBoxCognitive.setText(
            QCoreApplication.translate("DialogTraceSettings", "Cognitive", None)
        )
        self.checkBoxDevice.setText(
            QCoreApplication.translate("DialogTraceSettings", "Device", None)
        )
        self.checkBoxManual.setText(
            QCoreApplication.translate("DialogTraceSettings", "Manual", None)
        )
        self.checkBoxOcular.setText(
            QCoreApplication.translate("DialogTraceSettings", "Ocular", None)
        )
        self.checkBoxAuditory.setText(
            QCoreApplication.translate("DialogTraceSettings", "Auditory", None)
        )
        self.pushButtonCancel.setText(
            QCoreApplication.translate("DialogTraceSettings", "Cancel", None)
        )
        self.pushButtonOK.setText(
            QCoreApplication.translate("DialogTraceSettings", "OK", None)
        )

    # retranslateUi
