# Form implementation generated from reading ui file '/home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy2/EPICpy2/epicpy/uifiles/traceui.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from qtpy import QtCore, QtGui, QtWidgets


class Ui_TraceWindow(object):
    def setupUi(self, TraceWindow):
        TraceWindow.setObjectName("TraceWindow")
        TraceWindow.resize(636, 635)
        font = QtGui.QFont()
        font.setFamily("Fira Mono")
        font.setPointSize(14)
        TraceWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(parent=TraceWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        TraceWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=TraceWindow)
        self.statusbar.setObjectName("statusbar")
        TraceWindow.setStatusBar(self.statusbar)

        self.retranslateUi(TraceWindow)
        QtCore.QMetaObject.connectSlotsByName(TraceWindow)

    def retranslateUi(self, TraceWindow):
        _translate = QtCore.QCoreApplication.translate
        TraceWindow.setWindowTitle(_translate("TraceWindow", "Trace Output Window"))
