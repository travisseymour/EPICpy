# Form implementation generated from reading ui file '/home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy2/EPICpy2_pyqt6/epicpy/uifiles/tracesettingsui.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_DialogTraceSettings(object):
    def setupUi(self, DialogTraceSettings):
        DialogTraceSettings.setObjectName("DialogTraceSettings")
        DialogTraceSettings.resize(231, 326)
        DialogTraceSettings.setMinimumSize(QtCore.QSize(231, 297))
        DialogTraceSettings.setMaximumSize(QtCore.QSize(2000, 2000))
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        DialogTraceSettings.setFont(font)
        DialogTraceSettings.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(DialogTraceSettings)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBoxVisual = QtWidgets.QCheckBox(parent=DialogTraceSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxVisual.setFont(font)
        self.checkBoxVisual.setObjectName("checkBoxVisual")
        self.verticalLayout.addWidget(self.checkBoxVisual)
        self.checkBoxTemporal = QtWidgets.QCheckBox(parent=DialogTraceSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxTemporal.setFont(font)
        self.checkBoxTemporal.setObjectName("checkBoxTemporal")
        self.verticalLayout.addWidget(self.checkBoxTemporal)
        self.checkBoxVocal = QtWidgets.QCheckBox(parent=DialogTraceSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxVocal.setFont(font)
        self.checkBoxVocal.setObjectName("checkBoxVocal")
        self.verticalLayout.addWidget(self.checkBoxVocal)
        self.checkBoxCognitive = QtWidgets.QCheckBox(parent=DialogTraceSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxCognitive.setFont(font)
        self.checkBoxCognitive.setObjectName("checkBoxCognitive")
        self.verticalLayout.addWidget(self.checkBoxCognitive)
        self.checkBoxDevice = QtWidgets.QCheckBox(parent=DialogTraceSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxDevice.setFont(font)
        self.checkBoxDevice.setObjectName("checkBoxDevice")
        self.verticalLayout.addWidget(self.checkBoxDevice)
        self.checkBoxManual = QtWidgets.QCheckBox(parent=DialogTraceSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxManual.setFont(font)
        self.checkBoxManual.setObjectName("checkBoxManual")
        self.verticalLayout.addWidget(self.checkBoxManual)
        self.checkBoxOcular = QtWidgets.QCheckBox(parent=DialogTraceSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxOcular.setFont(font)
        self.checkBoxOcular.setObjectName("checkBoxOcular")
        self.verticalLayout.addWidget(self.checkBoxOcular)
        self.checkBoxAuditory = QtWidgets.QCheckBox(parent=DialogTraceSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.checkBoxAuditory.setFont(font)
        self.checkBoxAuditory.setObjectName("checkBoxAuditory")
        self.verticalLayout.addWidget(self.checkBoxAuditory)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonCancel = QtWidgets.QPushButton(parent=DialogTraceSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        font.setBold(True)
        self.pushButtonCancel.setFont(font)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.horizontalLayout.addWidget(self.pushButtonCancel)
        self.pushButtonOK = QtWidgets.QPushButton(parent=DialogTraceSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        font.setBold(True)
        self.pushButtonOK.setFont(font)
        self.pushButtonOK.setDefault(True)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.horizontalLayout.addWidget(self.pushButtonOK)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(DialogTraceSettings)
        QtCore.QMetaObject.connectSlotsByName(DialogTraceSettings)

    def retranslateUi(self, DialogTraceSettings):
        _translate = QtCore.QCoreApplication.translate
        DialogTraceSettings.setWindowTitle(
            _translate("DialogTraceSettings", "Trace Settings")
        )
        self.checkBoxVisual.setText(_translate("DialogTraceSettings", "Visual"))
        self.checkBoxTemporal.setText(_translate("DialogTraceSettings", "Temporal"))
        self.checkBoxVocal.setText(_translate("DialogTraceSettings", "Vocal"))
        self.checkBoxCognitive.setText(_translate("DialogTraceSettings", "Cognitive"))
        self.checkBoxDevice.setText(_translate("DialogTraceSettings", "Device"))
        self.checkBoxManual.setText(_translate("DialogTraceSettings", "Manual"))
        self.checkBoxOcular.setText(_translate("DialogTraceSettings", "Ocular"))
        self.checkBoxAuditory.setText(_translate("DialogTraceSettings", "Auditory"))
        self.pushButtonCancel.setText(_translate("DialogTraceSettings", "Cancel"))
        self.pushButtonOK.setText(_translate("DialogTraceSettings", "OK"))