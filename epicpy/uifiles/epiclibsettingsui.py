# Form implementation generated from reading ui file '/home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy2/EPICpy2_pyqt6/epicpy/uifiles/epiclibsettingsui.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_DialogEPICLibSettings(object):
    def setupUi(self, DialogEPICLibSettings):
        DialogEPICLibSettings.setObjectName("DialogEPICLibSettings")
        DialogEPICLibSettings.setWindowModality(
            QtCore.Qt.WindowModality.ApplicationModal
        )
        DialogEPICLibSettings.resize(482, 352)
        DialogEPICLibSettings.setMinimumSize(QtCore.QSize(482, 352))
        DialogEPICLibSettings.setMaximumSize(QtCore.QSize(3001, 3001))
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        DialogEPICLibSettings.setFont(font)
        DialogEPICLibSettings.setModal(True)
        self.layoutWidget = QtWidgets.QWidget(parent=DialogEPICLibSettings)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 461, 331))
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.layoutWidget.setFont(font)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelInfo = QtWidgets.QLabel(parent=self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        self.labelInfo.setFont(font)
        self.labelInfo.setWordWrap(True)
        self.labelInfo.setObjectName("labelInfo")
        self.verticalLayout.addWidget(self.labelInfo)
        self.listWidgetOptions = QtWidgets.QListWidget(parent=self.layoutWidget)
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
        self.pushButtonCancel = QtWidgets.QPushButton(parent=self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        font.setBold(True)
        self.pushButtonCancel.setFont(font)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.horizontalLayout.addWidget(self.pushButtonCancel)
        self.pushButtonOK = QtWidgets.QPushButton(parent=self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        font.setBold(True)
        self.pushButtonOK.setFont(font)
        self.pushButtonOK.setDefault(True)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.horizontalLayout.addWidget(self.pushButtonOK)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(DialogEPICLibSettings)
        QtCore.QMetaObject.connectSlotsByName(DialogEPICLibSettings)

    def retranslateUi(self, DialogEPICLibSettings):
        _translate = QtCore.QCoreApplication.translate
        DialogEPICLibSettings.setWindowTitle(
            _translate("DialogEPICLibSettings", "EPICLib Settings")
        )
        self.labelInfo.setText(
            _translate(
                "DialogEPICLibSettings",
                "Which EPICLib Version Should Be Used (Requires App Restart)",
            )
        )
        self.pushButtonCancel.setText(_translate("DialogEPICLibSettings", "Cancel"))
        self.pushButtonOK.setText(_translate("DialogEPICLibSettings", "OK"))