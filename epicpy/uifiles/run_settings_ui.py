# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'runsettingsui.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QDoubleSpinBox, QFormLayout,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_DialogRunSettings(object):
    def setupUi(self, DialogRunSettings):
        if not DialogRunSettings.objectName():
            DialogRunSettings.setObjectName(u"DialogRunSettings")
        DialogRunSettings.resize(877, 420)
        DialogRunSettings.setMinimumSize(QSize(840, 408))
        DialogRunSettings.setMaximumSize(QSize(3000, 3000))
        font = QFont()
        font.setFamilies([u"Fira Mono"])
        DialogRunSettings.setFont(font)
        self.gridLayout = QGridLayout(DialogRunSettings)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(DialogRunSettings)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 20))
        self.label.setMaximumSize(QSize(16777215, 20))
        font1 = QFont()
        font1.setFamilies([u"Fira Mono"])
        font1.setPointSize(14)
        font1.setBold(True)
        self.label.setFont(font1)

        self.verticalLayout.addWidget(self.label)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.radioButtonRunForSecs = QRadioButton(DialogRunSettings)
        self.radioButtonRunForSecs.setObjectName(u"radioButtonRunForSecs")
        self.radioButtonRunForSecs.setEnabled(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.radioButtonRunForSecs)

        self.spinBoxRunRealSecs = QSpinBox(DialogRunSettings)
        self.spinBoxRunRealSecs.setObjectName(u"spinBoxRunRealSecs")
        self.spinBoxRunRealSecs.setEnabled(True)
        self.spinBoxRunRealSecs.setMinimumSize(QSize(150, 0))
        font2 = QFont()
        font2.setFamilies([u"Fira Mono"])
        font2.setPointSize(12)
        font2.setBold(False)
        self.spinBoxRunRealSecs.setFont(font2)
        self.spinBoxRunRealSecs.setStyleSheet(u"")
        self.spinBoxRunRealSecs.setMinimum(50)
        self.spinBoxRunRealSecs.setMaximum(100000000)
        self.spinBoxRunRealSecs.setSingleStep(50)
        self.spinBoxRunRealSecs.setValue(5000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinBoxRunRealSecs)


        self.verticalLayout.addLayout(self.formLayout)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.radioButtonRunUntilSim = QRadioButton(DialogRunSettings)
        self.radioButtonRunUntilSim.setObjectName(u"radioButtonRunUntilSim")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.radioButtonRunUntilSim)

        self.spinBoxRunSimMsecs = QSpinBox(DialogRunSettings)
        self.spinBoxRunSimMsecs.setObjectName(u"spinBoxRunSimMsecs")
        self.spinBoxRunSimMsecs.setMinimumSize(QSize(150, 0))
        self.spinBoxRunSimMsecs.setFont(font2)
        self.spinBoxRunSimMsecs.setStyleSheet(u"")
        self.spinBoxRunSimMsecs.setMinimum(50)
        self.spinBoxRunSimMsecs.setMaximum(100000000)
        self.spinBoxRunSimMsecs.setSingleStep(50)
        self.spinBoxRunSimMsecs.setValue(600000)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinBoxRunSimMsecs)


        self.verticalLayout.addLayout(self.formLayout_2)

        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.radioButtonRunForCycles = QRadioButton(DialogRunSettings)
        self.radioButtonRunForCycles.setObjectName(u"radioButtonRunForCycles")
        self.radioButtonRunForCycles.setChecked(False)

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.radioButtonRunForCycles)

        self.spinBoxRunSimCycles = QSpinBox(DialogRunSettings)
        self.spinBoxRunSimCycles.setObjectName(u"spinBoxRunSimCycles")
        self.spinBoxRunSimCycles.setMinimumSize(QSize(150, 0))
        self.spinBoxRunSimCycles.setFont(font2)
        self.spinBoxRunSimCycles.setStyleSheet(u"")
        self.spinBoxRunSimCycles.setMinimum(1)
        self.spinBoxRunSimCycles.setMaximum(10000)

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinBoxRunSimCycles)


        self.verticalLayout.addLayout(self.formLayout_3)

        self.radioButtonRunUntilDone = QRadioButton(DialogRunSettings)
        self.radioButtonRunUntilDone.setObjectName(u"radioButtonRunUntilDone")
        font3 = QFont()
        font3.setFamilies([u"Fira Mono"])
        font3.setPointSize(14)
        font3.setBold(False)
        self.radioButtonRunUntilDone.setFont(font3)
        self.radioButtonRunUntilDone.setCheckable(True)

        self.verticalLayout.addWidget(self.radioButtonRunUntilDone)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.horizontalSpacer_3 = QSpacerItem(70, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_2 = QLabel(DialogRunSettings)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(0, 20))
        self.label_2.setMaximumSize(QSize(16777215, 20))
        self.label_2.setFont(font1)

        self.verticalLayout_2.addWidget(self.label_2)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.radioButtonRefreshEachCycle = QRadioButton(DialogRunSettings)
        self.radioButtonRefreshEachCycle.setObjectName(u"radioButtonRefreshEachCycle")
        self.radioButtonRefreshEachCycle.setEnabled(True)
        self.radioButtonRefreshEachCycle.setChecked(False)

        self.horizontalLayout_9.addWidget(self.radioButtonRefreshEachCycle)

        self.spinBoxRefreshSteps = QSpinBox(DialogRunSettings)
        self.spinBoxRefreshSteps.setObjectName(u"spinBoxRefreshSteps")
        self.spinBoxRefreshSteps.setEnabled(True)
        self.spinBoxRefreshSteps.setMinimumSize(QSize(110, 0))
        font4 = QFont()
        font4.setFamilies([u"Fira Mono"])
        font4.setPointSize(11)
        font4.setBold(False)
        self.spinBoxRefreshSteps.setFont(font4)
        self.spinBoxRefreshSteps.setMinimum(1)
        self.spinBoxRefreshSteps.setMaximum(100)
        self.spinBoxRefreshSteps.setSingleStep(1)
        self.spinBoxRefreshSteps.setValue(5)

        self.horizontalLayout_9.addWidget(self.spinBoxRefreshSteps)

        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.radioButtonRefreshEachSecs = QRadioButton(DialogRunSettings)
        self.radioButtonRefreshEachSecs.setObjectName(u"radioButtonRefreshEachSecs")
        self.radioButtonRefreshEachSecs.setEnabled(True)

        self.horizontalLayout_7.addWidget(self.radioButtonRefreshEachSecs)

        self.doubleSpinBoxRefreshSecs = QDoubleSpinBox(DialogRunSettings)
        self.doubleSpinBoxRefreshSecs.setObjectName(u"doubleSpinBoxRefreshSecs")
        self.doubleSpinBoxRefreshSecs.setEnabled(True)
        self.doubleSpinBoxRefreshSecs.setMinimumSize(QSize(110, 0))
        font4 = QFont()
        font4.setFamilies([u"Fira Mono"])
        font4.setPointSize(11)
        font4.setBold(False)
        self.doubleSpinBoxRefreshSecs.setFont(font4)
        self.doubleSpinBoxRefreshSecs.setStyleSheet(u"")
        self.doubleSpinBoxRefreshSecs.setMinimum(0.050000000000000)
        self.doubleSpinBoxRefreshSecs.setMaximum(600.000000000000000)
        self.doubleSpinBoxRefreshSecs.setSingleStep(0.050000000000000)
        self.doubleSpinBoxRefreshSecs.setValue(0.100000000000000)

        self.horizontalLayout_7.addWidget(self.doubleSpinBoxRefreshSecs)


        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.radioButtonRefreshNone = QRadioButton(DialogRunSettings)
        self.radioButtonRefreshNone.setObjectName(u"radioButtonRefreshNone")
        self.radioButtonRefreshNone.setCheckable(True)
        self.radioButtonRefreshNone.setChecked(False)

        self.verticalLayout_2.addWidget(self.radioButtonRefreshNone)

        self.verticalSpacer_4 = QSpacerItem(158, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_5 = QLabel(DialogRunSettings)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(0, 20))
        self.label_5.setMaximumSize(QSize(16777215, 20))
        self.label_5.setFont(font1)

        self.verticalLayout_6.addWidget(self.label_5)

        self.radioButtonRefreshContinuouslyText = QRadioButton(DialogRunSettings)
        self.radioButtonRefreshContinuouslyText.setObjectName(u"radioButtonRefreshContinuouslyText")
        self.radioButtonRefreshContinuouslyText.setEnabled(False)
        self.radioButtonRefreshContinuouslyText.setChecked(False)

        self.verticalLayout_6.addWidget(self.radioButtonRefreshContinuouslyText)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.radioButtonRefreshEachCycleText = QRadioButton(DialogRunSettings)
        self.radioButtonRefreshEachCycleText.setObjectName(u"radioButtonRefreshEachCycleText")
        self.radioButtonRefreshEachCycleText.setEnabled(True)
        self.radioButtonRefreshEachCycleText.setChecked(False)

        self.horizontalLayout_8.addWidget(self.radioButtonRefreshEachCycleText)

        self.spinBoxTextRefreshSteps = QSpinBox(DialogRunSettings)
        self.spinBoxTextRefreshSteps.setObjectName(u"spinBoxTextRefreshSteps")
        self.spinBoxTextRefreshSteps.setMinimumSize(QSize(110, 0))
        self.spinBoxTextRefreshSteps.setFont(font2)
        self.spinBoxTextRefreshSteps.setStyleSheet(u"")
        self.spinBoxTextRefreshSteps.setMinimum(1)
        self.spinBoxTextRefreshSteps.setMaximum(50)
        self.spinBoxTextRefreshSteps.setSingleStep(1)
        self.spinBoxTextRefreshSteps.setValue(1)

        self.horizontalLayout_8.addWidget(self.spinBoxTextRefreshSteps)


        self.verticalLayout_6.addLayout(self.horizontalLayout_8)

        self.radioButtonRefreshNoneText = QRadioButton(DialogRunSettings)
        self.radioButtonRefreshNoneText.setObjectName(u"radioButtonRefreshNoneText")
        self.radioButtonRefreshNoneText.setEnabled(False)
        self.radioButtonRefreshNoneText.setCheckable(True)
        self.radioButtonRefreshNoneText.setChecked(False)

        self.verticalLayout_6.addWidget(self.radioButtonRefreshNoneText)

        self.verticalSpacer_5 = QSpacerItem(158, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_6.addItem(self.verticalSpacer_5)


        self.horizontalLayout_3.addLayout(self.verticalLayout_6)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_4 = QLabel(DialogRunSettings)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_6.addWidget(self.label_4)

        self.spinBoxTimeDelay = QSpinBox(DialogRunSettings)
        self.spinBoxTimeDelay.setObjectName(u"spinBoxTimeDelay")
        self.spinBoxTimeDelay.setMinimumSize(QSize(150, 0))
        self.spinBoxTimeDelay.setFont(font2)
        self.spinBoxTimeDelay.setStyleSheet(u"")
        self.spinBoxTimeDelay.setMinimum(0)
        self.spinBoxTimeDelay.setMaximum(10000)
        self.spinBoxTimeDelay.setSingleStep(1)
        self.spinBoxTimeDelay.setValue(0)

        self.horizontalLayout_6.addWidget(self.spinBoxTimeDelay)

        self.horizontalSpacer_5 = QSpacerItem(388, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_5)


        self.verticalLayout_4.addLayout(self.horizontalLayout_6)

        self.verticalSpacer = QSpacerItem(648, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButtonRunContinuously = QPushButton(DialogRunSettings)
        self.pushButtonRunContinuously.setObjectName(u"pushButtonRunContinuously")

        self.horizontalLayout_2.addWidget(self.pushButtonRunContinuously)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_2 = QSpacerItem(648, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)


        self.verticalLayout_5.addLayout(self.verticalLayout_4)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_3 = QLabel(DialogRunSettings)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font3)

        self.horizontalLayout.addWidget(self.label_3)

        self.pushButtonResetParams = QPushButton(DialogRunSettings)
        self.pushButtonResetParams.setObjectName(u"pushButtonResetParams")
        self.pushButtonResetParams.setFont(font2)
        self.pushButtonResetParams.setAutoFillBackground(False)
        self.pushButtonResetParams.setStyleSheet(u"")
        self.pushButtonResetParams.setFlat(False)

        self.horizontalLayout.addWidget(self.pushButtonResetParams)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.lineEditDeviceParameters = QLineEdit(DialogRunSettings)
        self.lineEditDeviceParameters.setObjectName(u"lineEditDeviceParameters")
        self.lineEditDeviceParameters.setFont(font2)
        self.lineEditDeviceParameters.setStyleSheet(u"")

        self.verticalLayout_3.addWidget(self.lineEditDeviceParameters)

        self.verticalSpacer_3 = QSpacerItem(648, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)


        self.verticalLayout_5.addLayout(self.verticalLayout_3)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.pushButtonDeleteData = QPushButton(DialogRunSettings)
        self.pushButtonDeleteData.setObjectName(u"pushButtonDeleteData")
        self.pushButtonDeleteData.setFont(font2)
        self.pushButtonDeleteData.setAutoFillBackground(False)
        self.pushButtonDeleteData.setStyleSheet(u"color: rgb(255, 0, 0);")
        self.pushButtonDeleteData.setFlat(False)

        self.horizontalLayout_5.addWidget(self.pushButtonDeleteData)

        self.dataInfoLabel = QLabel(DialogRunSettings)
        self.dataInfoLabel.setObjectName(u"dataInfoLabel")
        self.dataInfoLabel.setFont(font2)

        self.horizontalLayout_5.addWidget(self.dataInfoLabel)

        self.horizontalSpacer_4 = QSpacerItem(428, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_4)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.pushButtonCancel = QPushButton(DialogRunSettings)
        self.pushButtonCancel.setObjectName(u"pushButtonCancel")

        self.horizontalLayout_4.addWidget(self.pushButtonCancel)

        self.pushButtonOK = QPushButton(DialogRunSettings)
        self.pushButtonOK.setObjectName(u"pushButtonOK")

        self.horizontalLayout_4.addWidget(self.pushButtonOK)


        self.horizontalLayout_5.addLayout(self.horizontalLayout_4)


        self.verticalLayout_5.addLayout(self.horizontalLayout_5)


        self.gridLayout.addLayout(self.verticalLayout_5, 0, 0, 1, 1)


        self.retranslateUi(DialogRunSettings)

        self.pushButtonOK.setDefault(True)


        QMetaObject.connectSlotsByName(DialogRunSettings)
    # setupUi

    def retranslateUi(self, DialogRunSettings):
        DialogRunSettings.setWindowTitle(QCoreApplication.translate("DialogRunSettings", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("DialogRunSettings", u"Run Command Duration", None))
        self.radioButtonRunForSecs.setText(QCoreApplication.translate("DialogRunSettings", u"Run For", None))
        self.spinBoxRunRealSecs.setSuffix(QCoreApplication.translate("DialogRunSettings", u" sim. msec", None))
        self.radioButtonRunUntilSim.setText(QCoreApplication.translate("DialogRunSettings", u"Run Until", None))
        self.spinBoxRunSimMsecs.setSuffix(QCoreApplication.translate("DialogRunSettings", u" sim. msec", None))
        self.radioButtonRunForCycles.setText(QCoreApplication.translate("DialogRunSettings", u"Run For", None))
        self.spinBoxRunSimCycles.setSuffix(QCoreApplication.translate("DialogRunSettings", u" step(s)", None))
        self.radioButtonRunUntilDone.setText(QCoreApplication.translate("DialogRunSettings", u"Run Until Done", None))
        self.label_2.setText(QCoreApplication.translate("DialogRunSettings", u"Display Refresh", None))
        self.radioButtonRefreshEachCycle.setText(QCoreApplication.translate("DialogRunSettings", u"After Every", None))
        self.spinBoxRefreshSteps.setSuffix(QCoreApplication.translate("DialogRunSettings", u" step(s)", None))
        self.radioButtonRefreshEachSecs.setText(QCoreApplication.translate("DialogRunSettings", u"After Every", None))
        self.doubleSpinBoxRefreshSecs.setSuffix(QCoreApplication.translate("DialogRunSettings", u" sec(s)", None))
        self.radioButtonRefreshNone.setText(QCoreApplication.translate("DialogRunSettings", u"None During Run", None))
        self.label_5.setText(QCoreApplication.translate("DialogRunSettings", u"Text Refresh", None))
        self.radioButtonRefreshContinuouslyText.setText(QCoreApplication.translate("DialogRunSettings", u"Continuously (slow)", None))
        self.radioButtonRefreshEachCycleText.setText(QCoreApplication.translate("DialogRunSettings", u"After Every", None))
        self.spinBoxTextRefreshSteps.setSuffix(QCoreApplication.translate("DialogRunSettings", u" step(s)", None))
        self.radioButtonRefreshNoneText.setText(QCoreApplication.translate("DialogRunSettings", u"None During Run", None))
        self.label_4.setText(QCoreApplication.translate("DialogRunSettings", u"Real Time Per Step ", None))
        self.spinBoxTimeDelay.setSuffix(QCoreApplication.translate("DialogRunSettings", u" msec(s)", None))
        self.pushButtonRunContinuously.setText(QCoreApplication.translate("DialogRunSettings", u"Run continuously at maximum rate without display or text refresh", None))
        self.label_3.setText(QCoreApplication.translate("DialogRunSettings", u"Device Parameter String", None))
#if QT_CONFIG(whatsthis)
        self.pushButtonResetParams.setWhatsThis(QCoreApplication.translate("DialogRunSettings", u"<html><head/><body><p><span style=\" font-size:12pt;\">Reset the device parameter string to the device default.</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.pushButtonResetParams.setText(QCoreApplication.translate("DialogRunSettings", u"Reset", None))
#if QT_CONFIG(whatsthis)
        self.pushButtonDeleteData.setWhatsThis(QCoreApplication.translate("DialogRunSettings", u"<html><head/><body><p><span style=\" font-size:12pt;\">If the current device exposes a method called </span><span style=\" font-size:12pt; font-weight:600;\">delete_data_file()</span><span style=\" font-size:12pt;\">, this button will trigger it. Otherwise, this button will not be shown.</span></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.pushButtonDeleteData.setText(QCoreApplication.translate("DialogRunSettings", u"Delete Datafile", None))
        self.dataInfoLabel.setText(QCoreApplication.translate("DialogRunSettings", u"Data Info: ???", None))
        self.pushButtonCancel.setText(QCoreApplication.translate("DialogRunSettings", u"Cancel", None))
        self.pushButtonOK.setText(QCoreApplication.translate("DialogRunSettings", u"OK", None))
    # retranslateUi

