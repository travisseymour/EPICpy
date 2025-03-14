# Form implementation generated from reading ui file '/home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy2/EPICpy2_pyqt6/epicpy/uifiles/sndtextsettingsui.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from qtpy import QtCore, QtGui, QtWidgets


class Ui_DialogSndTextSettings(object):
    def setupUi(self, DialogSndTextSettings):
        DialogSndTextSettings.setObjectName("DialogSndTextSettings")
        DialogSndTextSettings.resize(240, 492)
        DialogSndTextSettings.setMinimumSize(QtCore.QSize(240, 480))
        DialogSndTextSettings.setMaximumSize(QtCore.QSize(2000, 2000))
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        DialogSndTextSettings.setFont(font)
        DialogSndTextSettings.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(DialogSndTextSettings)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        font.setBold(True)
        font.setUnderline(True)
        self.label.setFont(font)
        self.label.setStyleSheet("background-color: rgb(255, 255, 127);\n" "color: rgb(0, 0, 0);")
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.checkBoxSoundKind = QtWidgets.QCheckBox(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxSoundKind.setFont(font)
        self.checkBoxSoundKind.setObjectName("checkBoxSoundKind")
        self.verticalLayout.addWidget(self.checkBoxSoundKind)
        self.checkBoxSoundStream = QtWidgets.QCheckBox(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxSoundStream.setFont(font)
        self.checkBoxSoundStream.setObjectName("checkBoxSoundStream")
        self.verticalLayout.addWidget(self.checkBoxSoundStream)
        self.checkBoxSoundTimbre = QtWidgets.QCheckBox(parent=DialogSndTextSettings)
        self.checkBoxSoundTimbre.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxSoundTimbre.setFont(font)
        self.checkBoxSoundTimbre.setCheckable(True)
        self.checkBoxSoundTimbre.setChecked(True)
        self.checkBoxSoundTimbre.setObjectName("checkBoxSoundTimbre")
        self.verticalLayout.addWidget(self.checkBoxSoundTimbre)
        self.checkBoxSoundLoudness = QtWidgets.QCheckBox(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxSoundLoudness.setFont(font)
        self.checkBoxSoundLoudness.setObjectName("checkBoxSoundLoudness")
        self.verticalLayout.addWidget(self.checkBoxSoundLoudness)
        self.label_2 = QtWidgets.QLabel(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        font.setBold(True)
        font.setUnderline(True)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("background-color: rgb(255, 255, 127);\n" "color: rgb(0, 0, 0);")
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.checkBoxSpeechKind = QtWidgets.QCheckBox(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxSpeechKind.setFont(font)
        self.checkBoxSpeechKind.setObjectName("checkBoxSpeechKind")
        self.verticalLayout.addWidget(self.checkBoxSpeechKind)
        self.checkBoxSpeechStream = QtWidgets.QCheckBox(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxSpeechStream.setFont(font)
        self.checkBoxSpeechStream.setObjectName("checkBoxSpeechStream")
        self.verticalLayout.addWidget(self.checkBoxSpeechStream)
        self.checkBoxSpeechPitch = QtWidgets.QCheckBox(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxSpeechPitch.setFont(font)
        self.checkBoxSpeechPitch.setObjectName("checkBoxSpeechPitch")
        self.verticalLayout.addWidget(self.checkBoxSpeechPitch)
        self.checkBoxSpeechLoudness = QtWidgets.QCheckBox(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxSpeechLoudness.setFont(font)
        self.checkBoxSpeechLoudness.setObjectName("checkBoxSpeechLoudness")
        self.verticalLayout.addWidget(self.checkBoxSpeechLoudness)
        self.checkBoxSpeechContent = QtWidgets.QCheckBox(parent=DialogSndTextSettings)
        self.checkBoxSpeechContent.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxSpeechContent.setFont(font)
        self.checkBoxSpeechContent.setChecked(True)
        self.checkBoxSpeechContent.setObjectName("checkBoxSpeechContent")
        self.verticalLayout.addWidget(self.checkBoxSpeechContent)
        self.checkBoxSpeechSpeaker = QtWidgets.QCheckBox(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxSpeechSpeaker.setFont(font)
        self.checkBoxSpeechSpeaker.setObjectName("checkBoxSpeechSpeaker")
        self.verticalLayout.addWidget(self.checkBoxSpeechSpeaker)
        self.checkBoxSpeechGender = QtWidgets.QCheckBox(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxSpeechGender.setFont(font)
        self.checkBoxSpeechGender.setObjectName("checkBoxSpeechGender")
        self.verticalLayout.addWidget(self.checkBoxSpeechGender)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonCancel = QtWidgets.QPushButton(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.pushButtonCancel.setFont(font)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.horizontalLayout.addWidget(self.pushButtonCancel)
        self.pushButtonOK = QtWidgets.QPushButton(parent=DialogSndTextSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.pushButtonOK.setFont(font)
        self.pushButtonOK.setDefault(True)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.horizontalLayout.addWidget(self.pushButtonOK)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(DialogSndTextSettings)
        QtCore.QMetaObject.connectSlotsByName(DialogSndTextSettings)

    def retranslateUi(self, DialogSndTextSettings):
        _translate = QtCore.QCoreApplication.translate
        DialogSndTextSettings.setWindowTitle(_translate("DialogSndTextSettings", "Sound Text Settings"))
        self.label.setText(_translate("DialogSndTextSettings", "Sound"))
        self.checkBoxSoundKind.setText(_translate("DialogSndTextSettings", "Kind"))
        self.checkBoxSoundStream.setText(_translate("DialogSndTextSettings", "Stream"))
        self.checkBoxSoundTimbre.setText(_translate("DialogSndTextSettings", "Timbre"))
        self.checkBoxSoundLoudness.setText(_translate("DialogSndTextSettings", "Loudness"))
        self.label_2.setText(_translate("DialogSndTextSettings", "Speech"))
        self.checkBoxSpeechKind.setText(_translate("DialogSndTextSettings", "Kind"))
        self.checkBoxSpeechStream.setText(_translate("DialogSndTextSettings", "Stream"))
        self.checkBoxSpeechPitch.setText(_translate("DialogSndTextSettings", "Pitch"))
        self.checkBoxSpeechLoudness.setText(_translate("DialogSndTextSettings", "Loudness"))
        self.checkBoxSpeechContent.setText(_translate("DialogSndTextSettings", "Content"))
        self.checkBoxSpeechSpeaker.setText(_translate("DialogSndTextSettings", "Speaker"))
        self.checkBoxSpeechGender.setText(_translate("DialogSndTextSettings", "Gender"))
        self.pushButtonCancel.setText(_translate("DialogSndTextSettings", "Cancel"))
        self.pushButtonOK.setText(_translate("DialogSndTextSettings", "OK"))
