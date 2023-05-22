# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy/EPICpy/src/main/python/uifiles/fontsizeui.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogFontSize(object):
    def setupUi(self, DialogFontSize):
        DialogFontSize.setObjectName("DialogFontSize")
        DialogFontSize.setWindowModality(QtCore.Qt.WindowModal)
        DialogFontSize.resize(800, 600)
        DialogFontSize.setMinimumSize(QtCore.QSize(640, 480))
        DialogFontSize.setMaximumSize(QtCore.QSize(2000, 2000))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        DialogFontSize.setFont(font)
        DialogFontSize.setSizeGripEnabled(True)
        self.layoutWidget = QtWidgets.QWidget(DialogFontSize)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 791, 581))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.spinBoxFontSize = QtWidgets.QSpinBox(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.spinBoxFontSize.setFont(font)
        self.spinBoxFontSize.setObjectName("spinBoxFontSize")
        self.horizontalLayout_3.addWidget(self.spinBoxFontSize)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.plainTextEditFontSample = CachedPlainTextEdit(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.plainTextEditFontSample.setFont(font)
        self.plainTextEditFontSample.setDocumentTitle("")
        self.plainTextEditFontSample.setReadOnly(True)
        self.plainTextEditFontSample.setCenterOnScroll(False)
        self.plainTextEditFontSample.setObjectName("plainTextEditFontSample")
        self.verticalLayout.addWidget(self.plainTextEditFontSample)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButtonCancel = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButtonCancel.setMinimumSize(QtCore.QSize(100, 50))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonCancel.setFont(font)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.horizontalLayout_4.addWidget(self.pushButtonCancel)
        spacerItem = QtWidgets.QSpacerItem(
            308, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_4.addItem(spacerItem)
        self.pushButtonOK = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButtonOK.setMinimumSize(QtCore.QSize(100, 50))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonOK.setFont(font)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.horizontalLayout_4.addWidget(self.pushButtonOK)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.retranslateUi(DialogFontSize)
        QtCore.QMetaObject.connectSlotsByName(DialogFontSize)

    def retranslateUi(self, DialogFontSize):
        _translate = QtCore.QCoreApplication.translate
        DialogFontSize.setWindowTitle(_translate("DialogFontSize", "Font Size Dialog"))
        self.label_3.setText(
            _translate(
                "DialogFontSize",
                '<html><head/><body><p><span style=" font-size:20pt; font-weight:600;">Application Font Name: Consolas</span></p></body></html>',
            )
        )
        self.label_4.setText(
            _translate(
                "DialogFontSize",
                '<html><head/><body><p><span style=" font-size:20pt; font-weight:600;">Application Font Size:</span></p></body></html>',
            )
        )
        self.plainTextEditFontSample.setPlainText(
            _translate(
                "DialogFontSize",
                "ℹ loading device code from choice_device.py...\n"
                "ℹ found EpicDevice class, creating new device instance based on this class.\n"
                "\n"
                "☑ Choice_Device_v2021.10.24 device was created successfully.\n"
                "☑ Model successfully initialized.\n"
                "\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃ RULE FILE: choicetask_rules_VM.prs ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                "",
            )
        )
        self.pushButtonCancel.setText(_translate("DialogFontSize", "Cancel"))
        self.pushButtonOK.setText(_translate("DialogFontSize", "OK"))


from epicpy2.widgets.cachedplaintextedit import CachedPlainTextEdit
