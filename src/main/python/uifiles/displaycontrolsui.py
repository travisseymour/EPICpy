# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'displaycontrolsui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_DialogDisplayControls(object):
    def setupUi(self, DialogDisplayControls):
        if not DialogDisplayControls.objectName():
            DialogDisplayControls.setObjectName("DialogDisplayControls")
        DialogDisplayControls.resize(681, 333)
        DialogDisplayControls.setMinimumSize(QSize(554, 278))
        DialogDisplayControls.setMaximumSize(QSize(3000, 3000))
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        DialogDisplayControls.setFont(font)
        self.gridLayout = QGridLayout(DialogDisplayControls)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, -1, -1)
        self.checkBoxPPSMemoryContents = QCheckBox(DialogDisplayControls)
        self.checkBoxPPSMemoryContents.setObjectName("checkBoxPPSMemoryContents")
        self.checkBoxPPSMemoryContents.setFont(font)

        self.verticalLayout.addWidget(self.checkBoxPPSMemoryContents)

        self.checkBoxPPSRunMessages = QCheckBox(DialogDisplayControls)
        self.checkBoxPPSRunMessages.setObjectName("checkBoxPPSRunMessages")
        self.checkBoxPPSRunMessages.setFont(font)

        self.verticalLayout.addWidget(self.checkBoxPPSRunMessages)

        self.checkBoxPPSCompilerMessages = QCheckBox(DialogDisplayControls)
        self.checkBoxPPSCompilerMessages.setObjectName("checkBoxPPSCompilerMessages")
        self.checkBoxPPSCompilerMessages.setFont(font)

        self.verticalLayout.addWidget(self.checkBoxPPSCompilerMessages)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.spinBoxSpatialScale = QSpinBox(DialogDisplayControls)
        self.spinBoxSpatialScale.setObjectName("spinBoxSpatialScale")
        self.spinBoxSpatialScale.setEnabled(True)
        self.spinBoxSpatialScale.setMinimumSize(QSize(75, 0))
        self.spinBoxSpatialScale.setFont(font)
        self.spinBoxSpatialScale.setStyleSheet("")
        self.spinBoxSpatialScale.setMinimum(1)
        self.spinBoxSpatialScale.setMaximum(100)
        self.spinBoxSpatialScale.setSingleStep(5)

        self.horizontalLayout.addWidget(self.spinBoxSpatialScale)

        self.label = QLabel(DialogDisplayControls)
        self.label.setObjectName("label")
        self.label.setEnabled(True)
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.horizontalSpacer_2 = QSpacerItem(
            28, 17, QSizePolicy.Fixed, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.checkBoxCompilerDetails = QCheckBox(DialogDisplayControls)
        self.checkBoxCompilerDetails.setObjectName("checkBoxCompilerDetails")
        self.checkBoxCompilerDetails.setFont(font)

        self.verticalLayout_2.addWidget(self.checkBoxCompilerDetails)

        self.checkBoxRunDetails = QCheckBox(DialogDisplayControls)
        self.checkBoxRunDetails.setObjectName("checkBoxRunDetails")
        self.checkBoxRunDetails.setFont(font)

        self.verticalLayout_2.addWidget(self.checkBoxRunDetails)

        self.verticalSpacer = QSpacerItem(
            20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed
        )

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.checkBoxCenterDot = QCheckBox(DialogDisplayControls)
        self.checkBoxCenterDot.setObjectName("checkBoxCenterDot")
        self.checkBoxCenterDot.setEnabled(True)
        self.checkBoxCenterDot.setFont(font)

        self.verticalLayout_2.addWidget(self.checkBoxCenterDot)

        self.checkBoxCalibrationGrid = QCheckBox(DialogDisplayControls)
        self.checkBoxCalibrationGrid.setObjectName("checkBoxCalibrationGrid")
        self.checkBoxCalibrationGrid.setEnabled(True)
        self.checkBoxCalibrationGrid.setFont(font)

        self.verticalLayout_2.addWidget(self.checkBoxCalibrationGrid)

        self.checkBoxDarkMode = QCheckBox(DialogDisplayControls)
        self.checkBoxDarkMode.setObjectName("checkBoxDarkMode")
        self.checkBoxDarkMode.setEnabled(False)
        self.checkBoxDarkMode.setFont(font)
        self.checkBoxDarkMode.setCheckable(True)

        self.verticalLayout_2.addWidget(self.checkBoxDarkMode)

        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.checkBoxShowModelParameters = QCheckBox(DialogDisplayControls)
        self.checkBoxShowModelParameters.setObjectName("checkBoxShowModelParameters")
        self.checkBoxShowModelParameters.setFont(font)

        self.verticalLayout_3.addWidget(self.checkBoxShowModelParameters)

        self.checkBoxAllowDeviceImages = QCheckBox(DialogDisplayControls)
        self.checkBoxAllowDeviceImages.setObjectName("checkBoxAllowDeviceImages")
        self.checkBoxAllowDeviceImages.setFont(font)

        self.verticalLayout_3.addWidget(self.checkBoxAllowDeviceImages)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(
            308, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButtonCancel = QPushButton(DialogDisplayControls)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.pushButtonCancel.setFont(font)

        self.horizontalLayout_2.addWidget(self.pushButtonCancel)

        self.pushButtonOK = QPushButton(DialogDisplayControls)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.pushButtonOK.setFont(font)

        self.horizontalLayout_2.addWidget(self.pushButtonOK)

        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)

        self.retranslateUi(DialogDisplayControls)

        self.pushButtonOK.setDefault(True)

        QMetaObject.connectSlotsByName(DialogDisplayControls)

    # setupUi

    def retranslateUi(self, DialogDisplayControls):
        DialogDisplayControls.setWindowTitle(
            QCoreApplication.translate(
                "DialogDisplayControls", "Display Controls", None
            )
        )
        self.checkBoxPPSMemoryContents.setText(
            QCoreApplication.translate(
                "DialogDisplayControls", "PPS Memory Contents", None
            )
        )
        self.checkBoxPPSRunMessages.setText(
            QCoreApplication.translate(
                "DialogDisplayControls", "PPS Run Messages", None
            )
        )
        self.checkBoxPPSCompilerMessages.setText(
            QCoreApplication.translate(
                "DialogDisplayControls", "PPS Compiler Messages", None
            )
        )
        self.spinBoxSpatialScale.setSuffix("")
        self.label.setText(
            QCoreApplication.translate(
                "DialogDisplayControls", "Spatial scale pixels/degree", None
            )
        )
        self.checkBoxCompilerDetails.setText(
            QCoreApplication.translate(
                "DialogDisplayControls", "Compiler Details", None
            )
        )
        self.checkBoxRunDetails.setText(
            QCoreApplication.translate("DialogDisplayControls", "Run Details", None)
        )
        self.checkBoxCenterDot.setText(
            QCoreApplication.translate("DialogDisplayControls", "Center Dot", None)
        )
        self.checkBoxCalibrationGrid.setText(
            QCoreApplication.translate(
                "DialogDisplayControls", "Calibration Grid", None
            )
        )
        self.checkBoxDarkMode.setText(
            QCoreApplication.translate("DialogDisplayControls", "Dark Mode", None)
        )
        self.checkBoxShowModelParameters.setText(
            QCoreApplication.translate(
                "DialogDisplayControls", "Show Model Parameters Before Each Run", None
            )
        )
        self.checkBoxAllowDeviceImages.setText(
            QCoreApplication.translate(
                "DialogDisplayControls",
                "Allow device to draw view underlay images",
                None,
            )
        )
        self.pushButtonCancel.setText(
            QCoreApplication.translate("DialogDisplayControls", "Cancel", None)
        )
        self.pushButtonOK.setText(
            QCoreApplication.translate("DialogDisplayControls", "OK", None)
        )

    # retranslateUi
