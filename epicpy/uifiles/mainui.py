# Form implementation generated from reading ui file '/home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy2/EPICpy2/epicpy/uifiles/mainui.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from qtpy import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(638, 640)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        font.setBold(True)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(False)
        self.centralwidget.setFont(font)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 638, 25))
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(True)
        self.menubar.setFont(font)
        self.menubar.setObjectName("menubar")
        self.menuFiles = QtWidgets.QMenu(parent=self.menubar)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(True)
        self.menuFiles.setFont(font)
        self.menuFiles.setObjectName("menuFiles")
        self.menuSettings = QtWidgets.QMenu(parent=self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuDarkMode = QtWidgets.QMenu(parent=self.menuSettings)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(True)
        self.menuDarkMode.setFont(font)
        self.menuDarkMode.setObjectName("menuDarkMode")
        self.menuRun = QtWidgets.QMenu(parent=self.menubar)
        self.menuRun.setObjectName("menuRun")
        self.menuHelp = QtWidgets.QMenu(parent=self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuTests = QtWidgets.QMenu(parent=self.menuHelp)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(True)
        self.menuTests.setFont(font)
        self.menuTests.setObjectName("menuTests")
        self.menuWindows = QtWidgets.QMenu(parent=self.menubar)
        self.menuWindows.setObjectName("menuWindows")
        self.menuSearch = QtWidgets.QMenu(parent=self.menubar)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(True)
        self.menuSearch.setFont(font)
        self.menuSearch.setObjectName("menuSearch")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(False)
        self.statusbar.setFont(font)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad_Device = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(True)
        self.actionLoad_Device.setFont(font)
        self.actionLoad_Device.setObjectName("actionLoad_Device")
        self.actionCompile_Rules = QtGui.QAction(parent=MainWindow)
        self.actionCompile_Rules.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(True)
        self.actionCompile_Rules.setFont(font)
        self.actionCompile_Rules.setObjectName("actionCompile_Rules")
        self.actionRecompile_Rules = QtGui.QAction(parent=MainWindow)
        self.actionRecompile_Rules.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionRecompile_Rules.setFont(font)
        self.actionRecompile_Rules.setObjectName("actionRecompile_Rules")
        self.actionQuit = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(True)
        self.actionQuit.setFont(font)
        self.actionQuit.setObjectName("actionQuit")
        self.actionRun_Settings = QtGui.QAction(parent=MainWindow)
        self.actionRun_Settings.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionRun_Settings.setFont(font)
        self.actionRun_Settings.setObjectName("actionRun_Settings")
        self.actionDisplay_Controls = QtGui.QAction(parent=MainWindow)
        self.actionDisplay_Controls.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(False)
        self.actionDisplay_Controls.setFont(font)
        self.actionDisplay_Controls.setObjectName("actionDisplay_Controls")
        self.actionTrace_Settings = QtGui.QAction(parent=MainWindow)
        self.actionTrace_Settings.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(False)
        self.actionTrace_Settings.setFont(font)
        self.actionTrace_Settings.setObjectName("actionTrace_Settings")
        self.actionRule_Break_Settings = QtGui.QAction(parent=MainWindow)
        self.actionRule_Break_Settings.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionRule_Break_Settings.setFont(font)
        self.actionRule_Break_Settings.setObjectName("actionRule_Break_Settings")
        self.actionRun = QtGui.QAction(parent=MainWindow)
        self.actionRun.setObjectName("actionRun")
        self.actionRunAll = QtGui.QAction(parent=MainWindow)
        self.actionRunAll.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionRunAll.setFont(font)
        self.actionRunAll.setObjectName("actionRunAll")
        self.actionStop = QtGui.QAction(parent=MainWindow)
        self.actionStop.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionStop.setFont(font)
        self.actionStop.setObjectName("actionStop")
        self.actionAbout = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionAbout.setFont(font)
        self.actionAbout.setObjectName("actionAbout")
        self.actionHelp = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionHelp.setFont(font)
        self.actionHelp.setObjectName("actionHelp")
        self.actionPause = QtGui.QAction(parent=MainWindow)
        self.actionPause.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionPause.setFont(font)
        self.actionPause.setObjectName("actionPause")
        self.actionLogging = QtGui.QAction(parent=MainWindow)
        self.actionLogging.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionLogging.setFont(font)
        self.actionLogging.setObjectName("actionLogging")
        self.actionExport_Normal_Output = QtGui.QAction(parent=MainWindow)
        self.actionExport_Normal_Output.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionExport_Normal_Output.setFont(font)
        self.actionExport_Normal_Output.setObjectName("actionExport_Normal_Output")
        self.actionExport_Trace_Output = QtGui.QAction(parent=MainWindow)
        self.actionExport_Trace_Output.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionExport_Trace_Output.setFont(font)
        self.actionExport_Trace_Output.setObjectName("actionExport_Trace_Output")
        self.actionSave_Layout = QtGui.QAction(parent=MainWindow)
        self.actionSave_Layout.setObjectName("actionSave_Layout")
        self.actionLoad_Layout = QtGui.QAction(parent=MainWindow)
        self.actionLoad_Layout.setObjectName("actionLoad_Layout")
        self.actionReset_Layout = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionReset_Layout.setFont(font)
        self.actionReset_Layout.setObjectName("actionReset_Layout")
        self.actionReload_Session = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        font.setBold(True)
        self.actionReload_Session.setFont(font)
        self.actionReload_Session.setObjectName("actionReload_Session")
        self.actionShow_Trace_Window = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionShow_Trace_Window.setFont(font)
        self.actionShow_Trace_Window.setObjectName("actionShow_Trace_Window")
        self.actionShow_Visual_Views = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionShow_Visual_Views.setFont(font)
        self.actionShow_Visual_Views.setObjectName("actionShow_Visual_Views")
        self.actionShow_Auditory_Views = QtGui.QAction(parent=MainWindow)
        self.actionShow_Auditory_Views.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionShow_Auditory_Views.setFont(font)
        self.actionShow_Auditory_Views.setObjectName("actionShow_Auditory_Views")
        self.actionShow_All = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionShow_All.setFont(font)
        self.actionShow_All.setObjectName("actionShow_All")
        self.actionClear_Output_Windows = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionClear_Output_Windows.setFont(font)
        self.actionClear_Output_Windows.setObjectName("actionClear_Output_Windows")
        self.actionAudio_Settings = QtGui.QAction(parent=MainWindow)
        self.actionAudio_Settings.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionAudio_Settings.setFont(font)
        self.actionAudio_Settings.setVisible(False)
        self.actionAudio_Settings.setObjectName("actionAudio_Settings")
        self.actionEPIC_CLI_Debug_Messages = QtGui.QAction(parent=MainWindow)
        self.actionEPIC_CLI_Debug_Messages.setCheckable(True)
        self.actionEPIC_CLI_Debug_Messages.setObjectName("actionEPIC_CLI_Debug_Messages")
        self.actionFind = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionFind.setFont(font)
        self.actionFind.setObjectName("actionFind")
        self.actionFindNext = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionFindNext.setFont(font)
        self.actionFindNext.setObjectName("actionFindNext")
        self.actionFindPrevious = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionFindPrevious.setFont(font)
        self.actionFindPrevious.setObjectName("actionFindPrevious")
        self.actionRun_One_Step = QtGui.QAction(parent=MainWindow)
        self.actionRun_One_Step.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionRun_One_Step.setFont(font)
        self.actionRun_One_Step.setObjectName("actionRun_One_Step")
        self.actionLoad_Visual_Encoder = QtGui.QAction(parent=MainWindow)
        self.actionLoad_Visual_Encoder.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionLoad_Visual_Encoder.setFont(font)
        self.actionLoad_Visual_Encoder.setObjectName("actionLoad_Visual_Encoder")
        self.actionLoad_Auditory_Encoder = QtGui.QAction(parent=MainWindow)
        self.actionLoad_Auditory_Encoder.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionLoad_Auditory_Encoder.setFont(font)
        self.actionLoad_Auditory_Encoder.setObjectName("actionLoad_Auditory_Encoder")
        self.actionMinimize_All = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionMinimize_All.setFont(font)
        self.actionMinimize_All.setObjectName("actionMinimize_All")
        self.actionDevice_Options = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionDevice_Options.setFont(font)
        self.actionDevice_Options.setObjectName("actionDevice_Options")
        self.actionEPICLib_Settings = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionEPICLib_Settings.setFont(font)
        self.actionEPICLib_Settings.setObjectName("actionEPICLib_Settings")
        self.actionSet_Application_Font = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionSet_Application_Font.setFont(font)
        self.actionSet_Application_Font.setObjectName("actionSet_Application_Font")
        self.actionShow_Stats_Window = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionShow_Stats_Window.setFont(font)
        self.actionShow_Stats_Window.setObjectName("actionShow_Stats_Window")
        self.actionSound_Text_Settings = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionSound_Text_Settings.setFont(font)
        self.actionSound_Text_Settings.setObjectName("actionSound_Text_Settings")
        self.actionExport_Stats_Output = QtGui.QAction(parent=MainWindow)
        self.actionExport_Stats_Output.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionExport_Stats_Output.setFont(font)
        self.actionExport_Stats_Output.setObjectName("actionExport_Stats_Output")
        self.actionUnload_Visual_Encoder = QtGui.QAction(parent=MainWindow)
        self.actionUnload_Visual_Encoder.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionUnload_Visual_Encoder.setFont(font)
        self.actionUnload_Visual_Encoder.setObjectName("actionUnload_Visual_Encoder")
        self.actionUnload_Auditory_Encoder = QtGui.QAction(parent=MainWindow)
        self.actionUnload_Auditory_Encoder.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionUnload_Auditory_Encoder.setFont(font)
        self.actionUnload_Auditory_Encoder.setObjectName("actionUnload_Auditory_Encoder")
        self.actionStandard_Run = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionStandard_Run.setFont(font)
        self.actionStandard_Run.setObjectName("actionStandard_Run")
        self.actionEncoder_Run = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionEncoder_Run.setFont(font)
        self.actionEncoder_Run.setObjectName("actionEncoder_Run")
        self.actionAll_Runs = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionAll_Runs.setFont(font)
        self.actionAll_Runs.setObjectName("actionAll_Runs")
        self.actionDelete_Datafile = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionDelete_Datafile.setFont(font)
        self.actionDelete_Datafile.setObjectName("actionDelete_Datafile")
        self.actionText_Editor = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionText_Editor.setFont(font)
        self.actionText_Editor.setObjectName("actionText_Editor")
        self.actionStandardRun = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionStandardRun.setFont(font)
        self.actionStandardRun.setObjectName("actionStandardRun")
        self.actionEncoderRun = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionEncoderRun.setFont(font)
        self.actionEncoderRun.setObjectName("actionEncoderRun")
        self.actionAllRuns = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionAllRuns.setFont(font)
        self.actionAllRuns.setObjectName("actionAllRuns")
        self.actionRun_Simulation_Script = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionRun_Simulation_Script.setFont(font)
        self.actionRun_Simulation_Script.setObjectName("actionRun_Simulation_Script")
        self.actionLight = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionLight.setFont(font)
        self.actionLight.setObjectName("actionLight")
        self.actionDark = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionDark.setFont(font)
        self.actionDark.setObjectName("actionDark")
        self.actionAuto = QtGui.QAction(parent=MainWindow)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(12)
        self.actionAuto.setFont(font)
        self.actionAuto.setObjectName("actionAuto")
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
        self.menuFiles.addAction(self.actionRun_Simulation_Script)
        self.menuFiles.addSeparator()
        self.menuFiles.addAction(self.actionExport_Normal_Output)
        self.menuFiles.addAction(self.actionExport_Trace_Output)
        self.menuFiles.addAction(self.actionExport_Stats_Output)
        self.menuFiles.addSeparator()
        self.menuFiles.addAction(self.actionQuit)
        self.menuDarkMode.addAction(self.actionLight)
        self.menuDarkMode.addAction(self.actionDark)
        self.menuDarkMode.addAction(self.actionAuto)
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
        self.menuSettings.addAction(self.menuDarkMode.menuAction())
        self.menuRun.addAction(self.actionRun_Settings)
        self.menuRun.addAction(self.actionRunAll)
        self.menuRun.addAction(self.actionRun_One_Step)
        self.menuRun.addAction(self.actionPause)
        self.menuRun.addAction(self.actionStop)
        self.menuRun.addSeparator()
        self.menuRun.addAction(self.actionDelete_Datafile)
        self.menuTests.addAction(self.actionStandardRun)
        self.menuTests.addAction(self.actionEncoderRun)
        self.menuTests.addAction(self.actionAllRuns)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.menuTests.menuAction())
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
        self.menubar.addAction(self.menuFiles.menuAction())
        self.menubar.addAction(self.menuSearch.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuRun.menuAction())
        self.menubar.addAction(self.menuWindows.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "EPICpy v2020.1"))
        self.menuFiles.setTitle(_translate("MainWindow", "File"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.menuDarkMode.setTitle(_translate("MainWindow", "Dark Mode: Light"))
        self.menuRun.setTitle(_translate("MainWindow", "Run"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.menuTests.setTitle(_translate("MainWindow", "Tests"))
        self.menuWindows.setTitle(_translate("MainWindow", "Windows"))
        self.menuSearch.setTitle(_translate("MainWindow", "Find"))
        self.actionLoad_Device.setText(_translate("MainWindow", "Load Device"))
        self.actionCompile_Rules.setText(_translate("MainWindow", "Compile Rules"))
        self.actionRecompile_Rules.setText(_translate("MainWindow", "Recompile Rules"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionRun_Settings.setText(_translate("MainWindow", "Run Settings"))
        self.actionDisplay_Controls.setText(_translate("MainWindow", "Display Controls"))
        self.actionTrace_Settings.setText(_translate("MainWindow", "Trace Settings"))
        self.actionRule_Break_Settings.setText(_translate("MainWindow", "Rule Break Settings"))
        self.actionRun.setText(_translate("MainWindow", "Run"))
        self.actionRunAll.setText(_translate("MainWindow", "Run"))
        self.actionStop.setText(_translate("MainWindow", "Stop"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionHelp.setText(_translate("MainWindow", "Help"))
        self.actionPause.setText(_translate("MainWindow", "Pause"))
        self.actionLogging.setText(_translate("MainWindow", "Logging"))
        self.actionExport_Normal_Output.setText(_translate("MainWindow", "Export Normal Output"))
        self.actionExport_Trace_Output.setText(_translate("MainWindow", "Export Trace Output"))
        self.actionSave_Layout.setText(_translate("MainWindow", "Save Layout"))
        self.actionLoad_Layout.setText(_translate("MainWindow", "Load Layout"))
        self.actionReset_Layout.setText(_translate("MainWindow", "Restore Default Layout"))
        self.actionReload_Session.setText(_translate("MainWindow", "Reload Last Session"))
        self.actionShow_Trace_Window.setText(_translate("MainWindow", "Show Trace Window"))
        self.actionShow_Visual_Views.setText(_translate("MainWindow", "Show Visual Views"))
        self.actionShow_Auditory_Views.setText(_translate("MainWindow", "Show Auditory Views"))
        self.actionShow_All.setText(_translate("MainWindow", "Show All"))
        self.actionClear_Output_Windows.setText(_translate("MainWindow", "Clear Output Windows"))
        self.actionAudio_Settings.setText(_translate("MainWindow", "Audio Settings"))
        self.actionEPIC_CLI_Debug_Messages.setText(_translate("MainWindow", "CLI and Device Debug Messages"))
        self.actionFind.setText(_translate("MainWindow", "Find"))
        self.actionFindNext.setText(_translate("MainWindow", "Find Next"))
        self.actionFindPrevious.setText(_translate("MainWindow", "Find Previous"))
        self.actionRun_One_Step.setText(_translate("MainWindow", "Run One Step"))
        self.actionLoad_Visual_Encoder.setText(_translate("MainWindow", "Load Visual Encoder"))
        self.actionLoad_Auditory_Encoder.setText(_translate("MainWindow", "Load Auditory Encoder"))
        self.actionMinimize_All.setText(_translate("MainWindow", "Minimize All"))
        self.actionDevice_Options.setText(_translate("MainWindow", "Device Options"))
        self.actionEPICLib_Settings.setText(_translate("MainWindow", "EPICLib Settings"))
        self.actionSet_Application_Font.setText(_translate("MainWindow", "Set Application Font"))
        self.actionShow_Stats_Window.setText(_translate("MainWindow", "Show Stats Window"))
        self.actionSound_Text_Settings.setText(_translate("MainWindow", "Sound Text Settings"))
        self.actionExport_Stats_Output.setText(_translate("MainWindow", "Export Stats Output"))
        self.actionUnload_Visual_Encoder.setText(_translate("MainWindow", "Unload Visual Encoder"))
        self.actionUnload_Auditory_Encoder.setText(_translate("MainWindow", "Unload Auditory Encoder"))
        self.actionStandard_Run.setText(_translate("MainWindow", "Standard Run"))
        self.actionEncoder_Run.setText(_translate("MainWindow", "Encoder Run"))
        self.actionAll_Runs.setText(_translate("MainWindow", "All Runs"))
        self.actionDelete_Datafile.setText(_translate("MainWindow", "Delete Datafile"))
        self.actionText_Editor.setText(_translate("MainWindow", "Text Editor: BUILT-IN"))
        self.actionStandardRun.setText(_translate("MainWindow", "Standard Run"))
        self.actionEncoderRun.setText(_translate("MainWindow", "Encoder Run"))
        self.actionAllRuns.setText(_translate("MainWindow", "All Runs"))
        self.actionRun_Simulation_Script.setText(_translate("MainWindow", "Run Simulation Script"))
        self.actionLight.setText(_translate("MainWindow", "Light"))
        self.actionDark.setText(_translate("MainWindow", "Dark"))
        self.actionAuto.setText(_translate("MainWindow", "Auto"))
