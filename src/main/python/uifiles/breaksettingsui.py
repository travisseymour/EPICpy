# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'breaksettingsui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_DialogRuleBreak(object):
    def setupUi(self, DialogRuleBreak):
        if not DialogRuleBreak.objectName():
            DialogRuleBreak.setObjectName("DialogRuleBreak")
        DialogRuleBreak.resize(593, 644)
        DialogRuleBreak.setMinimumSize(QSize(593, 644))
        DialogRuleBreak.setMaximumSize(QSize(3000, 3000))
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        DialogRuleBreak.setFont(font)
        self.layoutWidget = QWidget(DialogRuleBreak)
        self.layoutWidget.setObjectName("layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 571, 621))
        self.layoutWidget.setFont(font)
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.checkBoxEnableRuleBreaks = QCheckBox(self.layoutWidget)
        self.checkBoxEnableRuleBreaks.setObjectName("checkBoxEnableRuleBreaks")
        font1 = QFont()
        font1.setFamily("Consolas")
        font1.setPointSize(14)
        font1.setBold(True)
        font1.setWeight(75)
        self.checkBoxEnableRuleBreaks.setFont(font1)

        self.verticalLayout.addWidget(self.checkBoxEnableRuleBreaks)

        self.listWidgetRules = QListWidget(self.layoutWidget)
        self.listWidgetRules.setObjectName("listWidgetRules")
        self.listWidgetRules.setFont(font)

        self.verticalLayout.addWidget(self.listWidgetRules)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(
            368, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButtonCancel = QPushButton(self.layoutWidget)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.pushButtonCancel.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButtonCancel)

        self.pushButtonOK = QPushButton(self.layoutWidget)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.pushButtonOK.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButtonOK)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(DialogRuleBreak)

        self.pushButtonOK.setDefault(True)

        QMetaObject.connectSlotsByName(DialogRuleBreak)

    # setupUi

    def retranslateUi(self, DialogRuleBreak):
        DialogRuleBreak.setWindowTitle(
            QCoreApplication.translate("DialogRuleBreak", "Rule Break Settings", None)
        )
        self.checkBoxEnableRuleBreaks.setText(
            QCoreApplication.translate("DialogRuleBreak", "Enable Rule Breaks?", None)
        )
        self.pushButtonCancel.setText(
            QCoreApplication.translate("DialogRuleBreak", "Cancel", None)
        )
        self.pushButtonOK.setText(
            QCoreApplication.translate("DialogRuleBreak", "OK", None)
        )

    # retranslateUi
