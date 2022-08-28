# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'texteditorui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_TextEditorChooser(object):
    def setupUi(self, TextEditorChooser):
        if not TextEditorChooser.objectName():
            TextEditorChooser.setObjectName(u"TextEditorChooser")
        TextEditorChooser.resize(708, 384)
        TextEditorChooser.setMinimumSize(QSize(708, 300))
        TextEditorChooser.setMaximumSize(QSize(3000, 3000))
        font = QFont()
        font.setFamily(u"Consolas")
        font.setPointSize(12)
        TextEditorChooser.setFont(font)
        self.gridLayout = QGridLayout(TextEditorChooser)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(TextEditorChooser)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.checkBoxUseBuiltin = QCheckBox(TextEditorChooser)
        self.checkBoxUseBuiltin.setObjectName(u"checkBoxUseBuiltin")
        font1 = QFont()
        font1.setFamily(u"Consolas")
        font1.setPointSize(12)
        font1.setBold(True)
        font1.setWeight(75)
        self.checkBoxUseBuiltin.setFont(font1)

        self.horizontalLayout_2.addWidget(self.checkBoxUseBuiltin)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(TextEditorChooser)
        self.label.setObjectName(u"label")
        self.label.setFont(font1)

        self.horizontalLayout_3.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.toolButtonTextEditor = QToolButton(TextEditorChooser)
        self.toolButtonTextEditor.setObjectName(u"toolButtonTextEditor")
        self.toolButtonTextEditor.setFont(font1)

        self.horizontalLayout_3.addWidget(self.toolButtonTextEditor)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.plainTextEditPath = QPlainTextEdit(TextEditorChooser)
        self.plainTextEditPath.setObjectName(u"plainTextEditPath")
        self.plainTextEditPath.setFont(font)
        self.plainTextEditPath.setInputMethodHints(Qt.ImhMultiLine|Qt.ImhNoAutoUppercase)
        self.plainTextEditPath.setReadOnly(True)

        self.verticalLayout.addWidget(self.plainTextEditPath)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.pushButtonCancel = QPushButton(TextEditorChooser)
        self.pushButtonCancel.setObjectName(u"pushButtonCancel")
        self.pushButtonCancel.setFont(font1)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.pushButtonCancel)

        self.pushButtonOK = QPushButton(TextEditorChooser)
        self.pushButtonOK.setObjectName(u"pushButtonOK")
        self.pushButtonOK.setFont(font1)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.pushButtonOK)


        self.horizontalLayout.addLayout(self.formLayout)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(TextEditorChooser)

        QMetaObject.connectSlotsByName(TextEditorChooser)
    # setupUi

    def retranslateUi(self, TextEditorChooser):
        TextEditorChooser.setWindowTitle(QCoreApplication.translate("TextEditorChooser", u"Text Editor Choice Dialog", None))
        self.label_2.setText(QCoreApplication.translate("TextEditorChooser", u"<html><head/><body><p>Some EPICpy features require a text editor (e.g., those available when you right-click the Normal Output Window). We recommend you use the BUILT-IN version of EPICcoder so that production rule files get colorful syntax-highlighting. However, EPICcoder is a rather minimal editor, so if you have another text-editor you would rather use (e.g., Atom, Sublimetext, etc.), select it below.</p></body></html>", None))
        self.checkBoxUseBuiltin.setText(QCoreApplication.translate("TextEditorChooser", u"Use BUILT-IN Version Of The EPICcoder Editor?", None))
        self.label.setText(QCoreApplication.translate("TextEditorChooser", u"Which Text Editor Will Be Used WIth EPICpy?", None))
        self.toolButtonTextEditor.setText(QCoreApplication.translate("TextEditorChooser", u"...", None))
        self.plainTextEditPath.setPlainText("")
        self.pushButtonCancel.setText(QCoreApplication.translate("TextEditorChooser", u"Cancel", None))
        self.pushButtonOK.setText(QCoreApplication.translate("TextEditorChooser", u"OK", None))
    # retranslateUi

