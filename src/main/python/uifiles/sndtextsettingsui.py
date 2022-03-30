# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sndtextsettingsui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_DialogSndTextSettings(object):
    def setupUi(self, DialogSndTextSettings):
        if not DialogSndTextSettings.objectName():
            DialogSndTextSettings.setObjectName("DialogSndTextSettings")
        DialogSndTextSettings.resize(240, 492)
        DialogSndTextSettings.setMinimumSize(QSize(240, 480))
        DialogSndTextSettings.setMaximumSize(QSize(2000, 2000))
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(12)
        DialogSndTextSettings.setFont(font)
        DialogSndTextSettings.setSizeGripEnabled(True)
        self.gridLayout = QGridLayout(DialogSndTextSettings)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(DialogSndTextSettings)
        self.label.setObjectName("label")
        font1 = QFont()
        font1.setFamily("Consolas")
        font1.setPointSize(14)
        font1.setBold(True)
        font1.setUnderline(True)
        font1.setWeight(75)
        self.label.setFont(font1)
        self.label.setStyleSheet(
            "background-color: rgb(255, 255, 127);\n" "color: rgb(0, 0, 0);"
        )

        self.verticalLayout.addWidget(self.label)

        self.checkBoxSoundKind = QCheckBox(DialogSndTextSettings)
        self.checkBoxSoundKind.setObjectName("checkBoxSoundKind")
        font2 = QFont()
        font2.setFamily("Consolas")
        font2.setPointSize(14)
        self.checkBoxSoundKind.setFont(font2)

        self.verticalLayout.addWidget(self.checkBoxSoundKind)

        self.checkBoxSoundStream = QCheckBox(DialogSndTextSettings)
        self.checkBoxSoundStream.setObjectName("checkBoxSoundStream")
        self.checkBoxSoundStream.setFont(font2)

        self.verticalLayout.addWidget(self.checkBoxSoundStream)

        self.checkBoxSoundTimbre = QCheckBox(DialogSndTextSettings)
        self.checkBoxSoundTimbre.setObjectName("checkBoxSoundTimbre")
        self.checkBoxSoundTimbre.setEnabled(False)
        self.checkBoxSoundTimbre.setFont(font2)
        self.checkBoxSoundTimbre.setCheckable(True)
        self.checkBoxSoundTimbre.setChecked(True)

        self.verticalLayout.addWidget(self.checkBoxSoundTimbre)

        self.checkBoxSoundLoudness = QCheckBox(DialogSndTextSettings)
        self.checkBoxSoundLoudness.setObjectName("checkBoxSoundLoudness")
        self.checkBoxSoundLoudness.setFont(font2)

        self.verticalLayout.addWidget(self.checkBoxSoundLoudness)

        self.label_2 = QLabel(DialogSndTextSettings)
        self.label_2.setObjectName("label_2")
        self.label_2.setFont(font1)
        self.label_2.setStyleSheet(
            "background-color: rgb(255, 255, 127);\n" "color: rgb(0, 0, 0);"
        )

        self.verticalLayout.addWidget(self.label_2)

        self.checkBoxSpeechKind = QCheckBox(DialogSndTextSettings)
        self.checkBoxSpeechKind.setObjectName("checkBoxSpeechKind")
        self.checkBoxSpeechKind.setFont(font2)

        self.verticalLayout.addWidget(self.checkBoxSpeechKind)

        self.checkBoxSpeechStream = QCheckBox(DialogSndTextSettings)
        self.checkBoxSpeechStream.setObjectName("checkBoxSpeechStream")
        self.checkBoxSpeechStream.setFont(font2)

        self.verticalLayout.addWidget(self.checkBoxSpeechStream)

        self.checkBoxSpeechPitch = QCheckBox(DialogSndTextSettings)
        self.checkBoxSpeechPitch.setObjectName("checkBoxSpeechPitch")
        self.checkBoxSpeechPitch.setFont(font2)

        self.verticalLayout.addWidget(self.checkBoxSpeechPitch)

        self.checkBoxSpeechLoudness = QCheckBox(DialogSndTextSettings)
        self.checkBoxSpeechLoudness.setObjectName("checkBoxSpeechLoudness")
        self.checkBoxSpeechLoudness.setFont(font2)

        self.verticalLayout.addWidget(self.checkBoxSpeechLoudness)

        self.checkBoxSpeechContent = QCheckBox(DialogSndTextSettings)
        self.checkBoxSpeechContent.setObjectName("checkBoxSpeechContent")
        self.checkBoxSpeechContent.setEnabled(False)
        self.checkBoxSpeechContent.setFont(font2)
        self.checkBoxSpeechContent.setChecked(True)

        self.verticalLayout.addWidget(self.checkBoxSpeechContent)

        self.checkBoxSpeechSpeaker = QCheckBox(DialogSndTextSettings)
        self.checkBoxSpeechSpeaker.setObjectName("checkBoxSpeechSpeaker")
        self.checkBoxSpeechSpeaker.setFont(font2)

        self.verticalLayout.addWidget(self.checkBoxSpeechSpeaker)

        self.checkBoxSpeechGender = QCheckBox(DialogSndTextSettings)
        self.checkBoxSpeechGender.setObjectName("checkBoxSpeechGender")
        self.checkBoxSpeechGender.setFont(font2)

        self.verticalLayout.addWidget(self.checkBoxSpeechGender)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonCancel = QPushButton(DialogSndTextSettings)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.pushButtonCancel.setFont(font2)

        self.horizontalLayout.addWidget(self.pushButtonCancel)

        self.pushButtonOK = QPushButton(DialogSndTextSettings)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.pushButtonOK.setFont(font2)

        self.horizontalLayout.addWidget(self.pushButtonOK)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(DialogSndTextSettings)

        self.pushButtonOK.setDefault(True)

        QMetaObject.connectSlotsByName(DialogSndTextSettings)

    # setupUi

    def retranslateUi(self, DialogSndTextSettings):
        DialogSndTextSettings.setWindowTitle(
            QCoreApplication.translate(
                "DialogSndTextSettings", "Sound Text Settings", None
            )
        )
        self.label.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Sound", None)
        )
        self.checkBoxSoundKind.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Kind", None)
        )
        self.checkBoxSoundStream.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Stream", None)
        )
        self.checkBoxSoundTimbre.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Timbre", None)
        )
        self.checkBoxSoundLoudness.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Loudness", None)
        )
        self.label_2.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Speech", None)
        )
        self.checkBoxSpeechKind.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Kind", None)
        )
        self.checkBoxSpeechStream.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Stream", None)
        )
        self.checkBoxSpeechPitch.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Pitch", None)
        )
        self.checkBoxSpeechLoudness.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Loudness", None)
        )
        self.checkBoxSpeechContent.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Content", None)
        )
        self.checkBoxSpeechSpeaker.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Speaker", None)
        )
        self.checkBoxSpeechGender.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Gender", None)
        )
        self.pushButtonCancel.setText(
            QCoreApplication.translate("DialogSndTextSettings", "Cancel", None)
        )
        self.pushButtonOK.setText(
            QCoreApplication.translate("DialogSndTextSettings", "OK", None)
        )

    # retranslateUi
