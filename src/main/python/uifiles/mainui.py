# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from cachedplaintextedit import CachedPlainTextEdit


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(638, 640)
        font = QFont()
        font.setFamily(u"Consolas")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        MainWindow.setFont(font)
        self.actionLoad_Device = QAction(MainWindow)
        self.actionLoad_Device.setObjectName(u"actionLoad_Device")
        font1 = QFont()
        font1.setFamily(u"Consolas")
        font1.setPointSize(12)
        font1.setBold(True)
        font1.setWeight(75)
        self.actionLoad_Device.setFont(font1)
        self.actionCompile_Rules = QAction(MainWindow)
        self.actionCompile_Rules.setObjectName(u"actionCompile_Rules")
        self.actionCompile_Rules.setEnabled(False)
        self.actionCompile_Rules.setFont(font1)
        self.actionRecompile_Rules = QAction(MainWindow)
        self.actionRecompile_Rules.setObjectName(u"actionRecompile_Rules")
        self.actionRecompile_Rules.setEnabled(False)
        font2 = QFont()
        font2.setFamily(u"Consolas")
        font2.setPointSize(12)
        self.actionRecompile_Rules.setFont(font2)
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        self.actionQuit.setFont(font1)
        self.actionRun_Settings = QAction(MainWindow)
        self.actionRun_Settings.setObjectName(u"actionRun_Settings")
        self.actionRun_Settings.setEnabled(False)
        self.actionRun_Settings.setFont(font2)
        self.actionDisplay_Controls = QAction(MainWindow)
        self.actionDisplay_Controls.setObjectName(u"actionDisplay_Controls")
        self.actionDisplay_Controls.setEnabled(False)
        font3 = QFont()
        font3.setFamily(u"Consolas")
        font3.setPointSize(12)
        font3.setBold(False)
        font3.setWeight(50)
        self.actionDisplay_Controls.setFont(font3)
        self.actionTrace_Settings = QAction(MainWindow)
        self.actionTrace_Settings.setObjectName(u"actionTrace_Settings")
        self.actionTrace_Settings.setEnabled(False)
        self.actionTrace_Settings.setFont(font3)
        self.actionRule_Break_Settings = QAction(MainWindow)
        self.actionRule_Break_Settings.setObjectName(u"actionRule_Break_Settings")
        self.actionRule_Break_Settings.setEnabled(False)
        self.actionRule_Break_Settings.setFont(font2)
        self.actionRun = QAction(MainWindow)
        self.actionRun.setObjectName(u"actionRun")
        self.actionRunAll = QAction(MainWindow)
        self.actionRunAll.setObjectName(u"actionRunAll")
        self.actionRunAll.setEnabled(False)
        self.actionRunAll.setFont(font2)
        self.actionStop = QAction(MainWindow)
        self.actionStop.setObjectName(u"actionStop")
        self.actionStop.setEnabled(False)
        self.actionStop.setFont(font2)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionAbout.setFont(font2)
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        self.actionHelp.setFont(font2)
        self.actionPause = QAction(MainWindow)
        self.actionPause.setObjectName(u"actionPause")
        self.actionPause.setEnabled(False)
        self.actionPause.setFont(font2)
        self.actionLogging = QAction(MainWindow)
        self.actionLogging.setObjectName(u"actionLogging")
        self.actionLogging.setEnabled(False)
        self.actionLogging.setFont(font2)
        self.actionExport_Normal_Output = QAction(MainWindow)
        self.actionExport_Normal_Output.setObjectName(u"actionExport_Normal_Output")
        self.actionExport_Normal_Output.setEnabled(False)
        self.actionExport_Normal_Output.setFont(font2)
        self.actionExport_Trace_Output = QAction(MainWindow)
        self.actionExport_Trace_Output.setObjectName(u"actionExport_Trace_Output")
        self.actionExport_Trace_Output.setEnabled(False)
        self.actionExport_Trace_Output.setFont(font2)
        self.actionSave_Layout = QAction(MainWindow)
        self.actionSave_Layout.setObjectName(u"actionSave_Layout")
        self.actionLoad_Layout = QAction(MainWindow)
        self.actionLoad_Layout.setObjectName(u"actionLoad_Layout")
        self.actionReset_Layout = QAction(MainWindow)
        self.actionReset_Layout.setObjectName(u"actionReset_Layout")
        self.actionReset_Layout.setFont(font2)
        self.actionReload_Session = QAction(MainWindow)
        self.actionReload_Session.setObjectName(u"actionReload_Session")
        self.actionReload_Session.setFont(font1)
        self.actionShow_Trace_Window = QAction(MainWindow)
        self.actionShow_Trace_Window.setObjectName(u"actionShow_Trace_Window")
        self.actionShow_Trace_Window.setFont(font2)
        self.actionShow_Visual_Views = QAction(MainWindow)
        self.actionShow_Visual_Views.setObjectName(u"actionShow_Visual_Views")
        self.actionShow_Visual_Views.setFont(font2)
        self.actionShow_Auditory_Views = QAction(MainWindow)
        self.actionShow_Auditory_Views.setObjectName(u"actionShow_Auditory_Views")
        self.actionShow_Auditory_Views.setEnabled(True)
        self.actionShow_Auditory_Views.setFont(font2)
        self.actionShow_All = QAction(MainWindow)
        self.actionShow_All.setObjectName(u"actionShow_All")
        self.actionShow_All.setFont(font2)
        self.actionClear_Output_Windows = QAction(MainWindow)
        self.actionClear_Output_Windows.setObjectName(u"actionClear_Output_Windows")
        self.actionClear_Output_Windows.setFont(font2)
        self.actionAudio_Settings = QAction(MainWindow)
        self.actionAudio_Settings.setObjectName(u"actionAudio_Settings")
        self.actionAudio_Settings.setEnabled(False)
        self.actionAudio_Settings.setFont(font2)
        self.actionAudio_Settings.setVisible(False)
        self.actionEPIC_CLI_Debug_Messages = QAction(MainWindow)
        self.actionEPIC_CLI_Debug_Messages.setObjectName(u"actionEPIC_CLI_Debug_Messages")
        self.actionEPIC_CLI_Debug_Messages.setCheckable(True)
        self.actionFind = QAction(MainWindow)
        self.actionFind.setObjectName(u"actionFind")
        self.actionFind.setFont(font2)
        self.actionFindNext = QAction(MainWindow)
        self.actionFindNext.setObjectName(u"actionFindNext")
        self.actionFindNext.setFont(font2)
        self.actionFindPrevious = QAction(MainWindow)
        self.actionFindPrevious.setObjectName(u"actionFindPrevious")
        self.actionFindPrevious.setFont(font2)
        self.actionRun_One_Step = QAction(MainWindow)
        self.actionRun_One_Step.setObjectName(u"actionRun_One_Step")
        self.actionRun_One_Step.setEnabled(False)
        self.actionRun_One_Step.setFont(font2)
        self.actionLoad_Visual_Encoder = QAction(MainWindow)
        self.actionLoad_Visual_Encoder.setObjectName(u"actionLoad_Visual_Encoder")
        self.actionLoad_Visual_Encoder.setEnabled(False)
        self.actionLoad_Visual_Encoder.setFont(font2)
        self.actionLoad_Auditory_Encoder = QAction(MainWindow)
        self.actionLoad_Auditory_Encoder.setObjectName(u"actionLoad_Auditory_Encoder")
        self.actionLoad_Auditory_Encoder.setEnabled(False)
        self.actionLoad_Auditory_Encoder.setFont(font2)
        self.actionMinimize_All = QAction(MainWindow)
        self.actionMinimize_All.setObjectName(u"actionMinimize_All")
        self.actionMinimize_All.setFont(font2)
        self.actionDevice_Options = QAction(MainWindow)
        self.actionDevice_Options.setObjectName(u"actionDevice_Options")
        self.actionDevice_Options.setFont(font2)
        self.actionEPICLib_Settings = QAction(MainWindow)
        self.actionEPICLib_Settings.setObjectName(u"actionEPICLib_Settings")
        self.actionEPICLib_Settings.setFont(font2)
        self.actionSet_Application_Font = QAction(MainWindow)
        self.actionSet_Application_Font.setObjectName(u"actionSet_Application_Font")
        self.actionSet_Application_Font.setFont(font2)
        self.actionShow_Stats_Window = QAction(MainWindow)
        self.actionShow_Stats_Window.setObjectName(u"actionShow_Stats_Window")
        self.actionShow_Stats_Window.setFont(font2)
        self.actionSound_Text_Settings = QAction(MainWindow)
        self.actionSound_Text_Settings.setObjectName(u"actionSound_Text_Settings")
        self.actionSound_Text_Settings.setFont(font2)
        self.actionExport_Stats_Output = QAction(MainWindow)
        self.actionExport_Stats_Output.setObjectName(u"actionExport_Stats_Output")
        self.actionExport_Stats_Output.setEnabled(False)
        self.actionExport_Stats_Output.setFont(font2)
        self.actionDark_Mode_Toggle = QAction(MainWindow)
        self.actionDark_Mode_Toggle.setObjectName(u"actionDark_Mode_Toggle")
        self.actionDark_Mode_Toggle.setCheckable(True)
        self.actionDark_Mode_Toggle.setFont(font2)
        self.actionUnload_Visual_Encoder = QAction(MainWindow)
        self.actionUnload_Visual_Encoder.setObjectName(u"actionUnload_Visual_Encoder")
        self.actionUnload_Visual_Encoder.setEnabled(False)
        self.actionUnload_Visual_Encoder.setFont(font2)
        self.actionUnload_Auditory_Encoder = QAction(MainWindow)
        self.actionUnload_Auditory_Encoder.setObjectName(u"actionUnload_Auditory_Encoder")
        self.actionUnload_Auditory_Encoder.setEnabled(False)
        self.actionUnload_Auditory_Encoder.setFont(font2)
        self.actionStandard_Run = QAction(MainWindow)
        self.actionStandard_Run.setObjectName(u"actionStandard_Run")
        self.actionStandard_Run.setFont(font2)
        self.actionEncoder_Run = QAction(MainWindow)
        self.actionEncoder_Run.setObjectName(u"actionEncoder_Run")
        self.actionEncoder_Run.setFont(font2)
        self.actionAll_Runs = QAction(MainWindow)
        self.actionAll_Runs.setObjectName(u"actionAll_Runs")
        self.actionAll_Runs.setFont(font2)
        self.actionDelete_Datafile = QAction(MainWindow)
        self.actionDelete_Datafile.setObjectName(u"actionDelete_Datafile")
        self.actionDelete_Datafile.setFont(font2)
        self.actionText_Editor = QAction(MainWindow)
        self.actionText_Editor.setObjectName(u"actionText_Editor")
        self.actionText_Editor.setFont(font2)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setFont(font3)
        self.plainTextEditOutput = CachedPlainTextEdit(self.centralwidget)
        self.plainTextEditOutput.setObjectName(u"plainTextEditOutput")
        self.plainTextEditOutput.setGeometry(QRect(10, 10, 501, 431))
        font4 = QFont()
        font4.setFamily(u"Consolas")
        font4.setPointSize(14)
        font4.setBold(False)
        font4.setWeight(50)
        self.plainTextEditOutput.setFont(font4)
        self.plainTextEditOutput.setContextMenuPolicy(Qt.CustomContextMenu)
        self.plainTextEditOutput.setReadOnly(True)
        self.plainTextEditOutput.setCenterOnScroll(False)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 638, 24))
        self.menubar.setFont(font1)
        self.menuFiles = QMenu(self.menubar)
        self.menuFiles.setObjectName(u"menuFiles")
        self.menuFiles.setFont(font1)
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        self.menuRun = QMenu(self.menubar)
        self.menuRun.setObjectName(u"menuRun")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuWindows = QMenu(self.menubar)
        self.menuWindows.setObjectName(u"menuWindows")
        self.menuSearch = QMenu(self.menubar)
        self.menuSearch.setObjectName(u"menuSearch")
        self.menuSearch.setFont(font1)
        self.menuTests = QMenu(self.menubar)
        self.menuTests.setObjectName(u"menuTests")
        self.menuRun_Tests = QMenu(self.menuTests)
        self.menuRun_Tests.setObjectName(u"menuRun_Tests")
        self.menuRun_Tests.setFont(font1)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setFont(font3)
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFiles.menuAction())
        self.menubar.addAction(self.menuSearch.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuRun.menuAction())
        self.menubar.addAction(self.menuWindows.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menubar.addAction(self.menuTests.menuAction())
        self.menuFiles.addAction(self.actionLoad_Device)
        self.menuFiles.addAction(self.actionCompile_Rules)
        self.menuFiles.addAction(self.actionRecompile_Rules)
        self.menuFiles.addSeparator()
        self.menuFiles.addAction(self.actionLoad_Visual_Encoder)
        self.menuFiles.addAction(self.actionLoad_Auditory_Encoder)
        self.menuFiles.addAction(self.actionUnload_Visual_Encoder)
        self.menuFiles.addAction(self.actionUnload_Auditory_Encoder)
        self.menuFiles.addSeparator()
        self.menuFiles.addAction(self.actionReload_Session)
        self.menuFiles.addSeparator()
        self.menuFiles.addAction(self.actionExport_Normal_Output)
        self.menuFiles.addAction(self.actionExport_Trace_Output)
        self.menuFiles.addAction(self.actionExport_Stats_Output)
        self.menuFiles.addSeparator()
        self.menuFiles.addAction(self.actionQuit)
        self.menuSettings.addAction(self.actionTrace_Settings)
        self.menuSettings.addAction(self.actionDisplay_Controls)
        self.menuSettings.addAction(self.actionRule_Break_Settings)
        self.menuSettings.addAction(self.actionLogging)
        self.menuSettings.addAction(self.actionAudio_Settings)
        self.menuSettings.addAction(self.actionDevice_Options)
        self.menuSettings.addAction(self.actionEPICLib_Settings)
        self.menuSettings.addSeparator()
        self.menuSettings.addAction(self.actionSound_Text_Settings)
        self.menuSettings.addAction(self.actionSet_Application_Font)
        self.menuSettings.addAction(self.actionText_Editor)
        self.menuSettings.addAction(self.actionDark_Mode_Toggle)
        self.menuRun.addAction(self.actionRun_Settings)
        self.menuRun.addAction(self.actionRunAll)
        self.menuRun.addAction(self.actionRun_One_Step)
        self.menuRun.addAction(self.actionPause)
        self.menuRun.addAction(self.actionStop)
        self.menuRun.addSeparator()
        self.menuRun.addAction(self.actionDelete_Datafile)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionHelp)
        self.menuWindows.addAction(self.actionShow_All)
        self.menuWindows.addAction(self.actionMinimize_All)
        self.menuWindows.addAction(self.actionShow_Trace_Window)
        self.menuWindows.addAction(self.actionShow_Stats_Window)
        self.menuWindows.addAction(self.actionShow_Visual_Views)
        self.menuWindows.addAction(self.actionShow_Auditory_Views)
        self.menuWindows.addSeparator()
        self.menuWindows.addAction(self.actionClear_Output_Windows)
        self.menuWindows.addSeparator()
        self.menuWindows.addAction(self.actionReset_Layout)
        self.menuSearch.addAction(self.actionFind)
        self.menuSearch.addAction(self.actionFindNext)
        self.menuSearch.addAction(self.actionFindPrevious)
        self.menuTests.addAction(self.menuRun_Tests.menuAction())
        self.menuRun_Tests.addAction(self.actionStandard_Run)
        self.menuRun_Tests.addAction(self.actionEncoder_Run)
        self.menuRun_Tests.addAction(self.actionAll_Runs)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"EPICpy v2020.1", None))
        self.actionLoad_Device.setText(QCoreApplication.translate("MainWindow", u"Load Device", None))
        self.actionCompile_Rules.setText(QCoreApplication.translate("MainWindow", u"Compile Rules", None))
        self.actionRecompile_Rules.setText(QCoreApplication.translate("MainWindow", u"Recompile Rules", None))
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.actionRun_Settings.setText(QCoreApplication.translate("MainWindow", u"Run Settings", None))
        self.actionDisplay_Controls.setText(QCoreApplication.translate("MainWindow", u"Display Controls", None))
        self.actionTrace_Settings.setText(QCoreApplication.translate("MainWindow", u"Trace Settings", None))
        self.actionRule_Break_Settings.setText(QCoreApplication.translate("MainWindow", u"Rule Break Settings", None))
        self.actionRun.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.actionRunAll.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.actionStop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.actionPause.setText(QCoreApplication.translate("MainWindow", u"Pause", None))
        self.actionLogging.setText(QCoreApplication.translate("MainWindow", u"Logging", None))
        self.actionExport_Normal_Output.setText(QCoreApplication.translate("MainWindow", u"Export Normal Output", None))
        self.actionExport_Trace_Output.setText(QCoreApplication.translate("MainWindow", u"Export Trace Output", None))
        self.actionSave_Layout.setText(QCoreApplication.translate("MainWindow", u"Save Layout", None))
        self.actionLoad_Layout.setText(QCoreApplication.translate("MainWindow", u"Load Layout", None))
        self.actionReset_Layout.setText(QCoreApplication.translate("MainWindow", u"Restore Default Layout", None))
        self.actionReload_Session.setText(QCoreApplication.translate("MainWindow", u"Reload Last Session", None))
        self.actionShow_Trace_Window.setText(QCoreApplication.translate("MainWindow", u"Show Trace Window", None))
        self.actionShow_Visual_Views.setText(QCoreApplication.translate("MainWindow", u"Show Visual Views", None))
        self.actionShow_Auditory_Views.setText(QCoreApplication.translate("MainWindow", u"Show Auditory Views", None))
        self.actionShow_All.setText(QCoreApplication.translate("MainWindow", u"Show All", None))
        self.actionClear_Output_Windows.setText(QCoreApplication.translate("MainWindow", u"Clear Output Windows", None))
        self.actionAudio_Settings.setText(QCoreApplication.translate("MainWindow", u"Audio Settings", None))
        self.actionEPIC_CLI_Debug_Messages.setText(QCoreApplication.translate("MainWindow", u"CLI and Device Debug Messages", None))
        self.actionFind.setText(QCoreApplication.translate("MainWindow", u"Find", None))
        self.actionFindNext.setText(QCoreApplication.translate("MainWindow", u"Find Next", None))
        self.actionFindPrevious.setText(QCoreApplication.translate("MainWindow", u"Find Previous", None))
        self.actionRun_One_Step.setText(QCoreApplication.translate("MainWindow", u"Run One Step", None))
        self.actionLoad_Visual_Encoder.setText(QCoreApplication.translate("MainWindow", u"Load Visual Encoder", None))
        self.actionLoad_Auditory_Encoder.setText(QCoreApplication.translate("MainWindow", u"Load Auditory Encoder", None))
        self.actionMinimize_All.setText(QCoreApplication.translate("MainWindow", u"Minimize All", None))
        self.actionDevice_Options.setText(QCoreApplication.translate("MainWindow", u"Device Options", None))
        self.actionEPICLib_Settings.setText(QCoreApplication.translate("MainWindow", u"EPICLib Settings", None))
        self.actionSet_Application_Font.setText(QCoreApplication.translate("MainWindow", u"Set Application Font", None))
        self.actionShow_Stats_Window.setText(QCoreApplication.translate("MainWindow", u"Show Stats Window", None))
        self.actionSound_Text_Settings.setText(QCoreApplication.translate("MainWindow", u"Sound Text Settings", None))
        self.actionExport_Stats_Output.setText(QCoreApplication.translate("MainWindow", u"Export Stats Output", None))
        self.actionDark_Mode_Toggle.setText(QCoreApplication.translate("MainWindow", u"Dark Mode", None))
        self.actionUnload_Visual_Encoder.setText(QCoreApplication.translate("MainWindow", u"Unload Visual Encoder", None))
        self.actionUnload_Auditory_Encoder.setText(QCoreApplication.translate("MainWindow", u"Unload Auditory Encoder", None))
        self.actionStandard_Run.setText(QCoreApplication.translate("MainWindow", u"Standard Run", None))
        self.actionEncoder_Run.setText(QCoreApplication.translate("MainWindow", u"Encoder Run", None))
        self.actionAll_Runs.setText(QCoreApplication.translate("MainWindow", u"All Runs", None))
        self.actionDelete_Datafile.setText(QCoreApplication.translate("MainWindow", u"Delete Datafile", None))
        self.actionText_Editor.setText(QCoreApplication.translate("MainWindow", u"Text Editor: BUILT-IN", None))
        self.plainTextEditOutput.setDocumentTitle("")
        self.plainTextEditOutput.setPlainText(QCoreApplication.translate("MainWindow", u"Ready.", None))
        self.menuFiles.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.menuRun.setTitle(QCoreApplication.translate("MainWindow", u"Run", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuWindows.setTitle(QCoreApplication.translate("MainWindow", u"Windows", None))
        self.menuSearch.setTitle(QCoreApplication.translate("MainWindow", u"Find", None))
        self.menuTests.setTitle(QCoreApplication.translate("MainWindow", u"Tests", None))
        self.menuRun_Tests.setTitle(QCoreApplication.translate("MainWindow", u"Run Tests", None))
    # retranslateUi

