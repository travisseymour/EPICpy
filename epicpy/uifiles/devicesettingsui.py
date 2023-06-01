# Form implementation generated from reading ui file '/home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy2/EPICpy2_pyqt6/epicpy/uifiles/devicesettingsui.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_DialogDeviceOptions(object):
    def setupUi(self, DialogDeviceOptions):
        DialogDeviceOptions.setObjectName("DialogDeviceOptions")
        DialogDeviceOptions.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        DialogDeviceOptions.resize(482, 505)
        DialogDeviceOptions.setMinimumSize(QtCore.QSize(482, 505))
        DialogDeviceOptions.setMaximumSize(QtCore.QSize(3000, 3000))
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        DialogDeviceOptions.setFont(font)
        DialogDeviceOptions.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(DialogDeviceOptions)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelDeviceNameAndInfo = QtWidgets.QLabel(parent=DialogDeviceOptions)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        font.setBold(True)
        self.labelDeviceNameAndInfo.setFont(font)
        self.labelDeviceNameAndInfo.setWordWrap(True)
        self.labelDeviceNameAndInfo.setObjectName("labelDeviceNameAndInfo")
        self.verticalLayout.addWidget(self.labelDeviceNameAndInfo)
        self.listWidgetOptions = QtWidgets.QListWidget(parent=DialogDeviceOptions)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.listWidgetOptions.setFont(font)
        self.listWidgetOptions.setObjectName("listWidgetOptions")
        self.verticalLayout.addWidget(self.listWidgetOptions)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(
            368,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.horizontalLayout.addItem(spacerItem)
        self.pushButtonCancel = QtWidgets.QPushButton(parent=DialogDeviceOptions)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        font.setBold(True)
        self.pushButtonCancel.setFont(font)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.horizontalLayout.addWidget(self.pushButtonCancel)
        self.pushButtonOK = QtWidgets.QPushButton(parent=DialogDeviceOptions)
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

        self.retranslateUi(DialogDeviceOptions)
        QtCore.QMetaObject.connectSlotsByName(DialogDeviceOptions)

    def retranslateUi(self, DialogDeviceOptions):
        _translate = QtCore.QCoreApplication.translate
        DialogDeviceOptions.setWindowTitle(
            _translate("DialogDeviceOptions", "Device Options")
        )
        self.labelDeviceNameAndInfo.setText(
            _translate(
                "DialogDeviceOptions",
                "Device Options - There are No Options Exposed Here",
            )
        )
        self.pushButtonCancel.setText(_translate("DialogDeviceOptions", "Cancel"))
        self.pushButtonOK.setText(_translate("DialogDeviceOptions", "OK"))