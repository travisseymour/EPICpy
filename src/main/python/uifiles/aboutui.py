# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'aboutui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_aboutDialog(object):
    def setupUi(self, aboutDialog):
        if not aboutDialog.objectName():
            aboutDialog.setObjectName("aboutDialog")
        aboutDialog.setWindowModality(Qt.ApplicationModal)
        aboutDialog.resize(680, 640)
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(14)
        aboutDialog.setFont(font)
        self.gridLayout = QGridLayout(aboutDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.labelEPICicon = QLabel(aboutDialog)
        self.labelEPICicon.setObjectName("labelEPICicon")
        self.labelEPICicon.setMinimumSize(QSize(180, 180))
        self.labelEPICicon.setBaseSize(QSize(180, 180))

        self.horizontalLayout.addWidget(self.labelEPICicon)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.textBrowser = QTextBrowser(aboutDialog)
        self.textBrowser.setObjectName("textBrowser")

        self.verticalLayout.addWidget(self.textBrowser)

        self.pushButtonClose = QPushButton(aboutDialog)
        self.pushButtonClose.setObjectName("pushButtonClose")
        font1 = QFont()
        font1.setFamily("Consolas")
        font1.setPointSize(18)
        font1.setBold(True)
        font1.setWeight(75)
        self.pushButtonClose.setFont(font1)

        self.verticalLayout.addWidget(self.pushButtonClose)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(aboutDialog)

        self.pushButtonClose.setDefault(True)

        QMetaObject.connectSlotsByName(aboutDialog)

    # setupUi

    def retranslateUi(self, aboutDialog):
        aboutDialog.setWindowTitle(
            QCoreApplication.translate("aboutDialog", "About EPICpy", None)
        )
        self.labelEPICicon.setText("")
        self.textBrowser.setHtml(
            QCoreApplication.translate(
                "aboutDialog",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'Consolas'; font-size:14pt; font-weight:400; font-style:normal;\">\n"
                '<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'JetBrains Mono\',\'monospace\'; font-size:28pt; font-weight:600; color:#000000;">** EPICpy **</span></p>\n'
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">EPICpy is based on EPIClib and EPICapp by "
                "David Kieras, as well as EpicCLI by David Kieras and Yunfeng Zhang.</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br />EPICpy is is made possible by a C++/Python interface layer called &lt;a href=&quot;https://cppyy.readthedocs.io/en/latest/&quot;&gt;cppyy&lt;/a&gt; that allows cross platform device and encoder programming in Python (in addition to the PyQt5 based GUI itself).</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; font-weight:600"
                '; text-decoration: underline; color:#000000;">License Statement:</span></p>\n'
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">EPICpy is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.</span></p>\n"
                '<p style="'
                "-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.</span></p>\n"
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-'
                "indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">You should have received a copy of the GNU General Public License along with EPICpy.</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">If not, see &lt;https://www.gnu.org/licenses/&gt;.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:13.5pt; color:#808080;\"><br /></p>\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0'
                "px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; font-weight:600; text-decoration: underline; color:#000000;\">License:</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">GNU LESSER GENERAL PUBLIC LICENSE</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">Version 3, 29 June 2007</span></p>\n"
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px;'
                " margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">Copyright (C) 2007 Free Software Foundation, Inc. &lt;http://fsf.org/&gt;</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not"
                " allowed.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">This version of the GNU Lesser General Public License incorporates the terms and conditions of version 3 of the GNU General Public License, supplemented by the additional permissions listed below.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; t'
                "ext-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">0. Additional Definitions.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">As used herein, \u201cthis License\u201d refers to version 3 of the GNU Lesser General Public License, and the \u201cGNU GPL\u201d refers to version 3 of the GNU General Public License.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><b"
                "r /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">\u201cThe Library\u201d refers to a covered work governed by this License, other than an Application or a Combined Work as defined below.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">An \u201cApplication\u201d is any work that makes use of an interface provided by the Library, but which is not otherwise based on the Library. Defining a subclass of a class defined by the Library"
                " is deemed a mode of using an interface provided by the Library.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">A \u201cCombined Work\u201d is a work produced by combining or linking an Application with the Library. The particular version of the Library with which the Combined Work was made is also called the \u201cLinked Version\u201d.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                '<p style=" margin'
                "-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">The \u201cMinimal Corresponding Source\u201d for a Combined Work means the Corresponding Source for the Combined Work, excluding any source code for portions of the Combined Work that, considered in isolation, are based on the Application, and not on the Linked Version.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">The \u201cCorresponding Application Code\u201d for a Combined Work means the object code and/or"
                " source code for the Application, including any data and utility programs needed for reproducing the Combined Work from the Application, but excluding the System Libraries of the Combined Work.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">1. Exception to Section 3 of the GNU GPL.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-rig'
                "ht:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">You may convey a covered work under sections 3 and 4 of this License without being bound by section 3 of the GNU GPL.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">2. Conveying Modified Versions.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                '<p style=" margin-to'
                "p:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">If you modify a copy of the Library, and, in your modifications, a facility refers to a function or data to be supplied by an Application that uses the facility (other than as an argument passed when the facility is invoked), then you may convey a copy of the modified version:</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">a) under this License, provided that you make a good faith effort to ensure that, in the ev"
                "ent an Application does not supply the function or data, the facility still operates, and performs whatever part of its purpose remains meaningful, or</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">b) under the GNU GPL, with none of the additional permissions of this License applicable to that copy.</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">3. Object Code Incorporating Material from Library Header Files.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                ""
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">The object code form of an Application may incorporate material from a header file that is part of the Library. You may convey such object code under terms of your choice, provided that, if the incorporated material is not limited to numerical parameters, data structure layouts and accessors, or small macros, inline functions and templates (ten or fewer lines in length), you do both of the following:</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'JetBrain'
                "s Mono','monospace'; font-size:15.8pt; color:#000000;\">a) Give prominent notice with each copy of the object code that the Library is used in it and that the Library and its use are covered by this License.</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">b) Accompany the object code with a copy of the GNU GPL and this license document.</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">4. Combined Works.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style"
                "=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">You may convey a Combined Work under terms of your choice that, taken together, effectively do not restrict modification of the portions of the Library contained in the Combined Work and reverse engineering for debugging such modifications, if you also do each of the following:</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">a) Give prominent notice with each copy of the Combined Work that the Library"
                " is used in it and that the Library and its use are covered by this License.</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">b) Accompany the Combined Work with a copy of the GNU GPL and this license document.</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">c) For a Combined Work that displays copyright notices during execution, include the copyright notice for the Library among these notices, as well as a reference directing the user to the copies of the GNU GPL and this license document.</span></p>\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'JetBra'
                "ins Mono','monospace'; font-size:15.8pt; color:#000000;\">d) Do one of the following:</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">0) Convey the Minimal Corresponding Source under the terms of this License, and the Corresponding Application Code in a form suitable for, and under terms that permit, the user to recombine or relink the Application with a modified version of the Linked Version to produce a modified Combined Work, in the manner specified by section 6 of the GNU GPL for conveying Corresponding Source.</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">1) Use a suitable shared library mechanism for linking with the Library. A suitable mechanism is"
                " one that (a) uses at run time a copy of the Library already present on the user's computer system, and (b) will operate properly with a modified version of the Library that is interface-compatible with the Linked Version.</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">e) Provide Installation Information, but only if you would otherwise be required to provide such information under section 6 of the GNU GPL, and only to the extent that such information is necessary to install and execute a modified version of the Combined Work produced by recombining or relinking the Application with a modified version of the Linked Version. (If you use option 4d0, the Installation Information must accompany the Minimal Corresponding Source and Corresponding Application Code. If you use option 4d1, you must provide the Installation Information in the"
                " manner specified by section 6 of the GNU GPL for conveying Corresponding Source.)</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">5. Combined Libraries.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">You may place library facilities that are a work based on the Library side by side in a single library together with other library facilities that are not Applications and are not covered by this License, and convey such a comb"
                "ined library under terms of your choice, if you do both of the following:</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">a) Accompany the combined library with a copy of the same work based on the Library, uncombined with any other library facilities, conveyed under the terms of this License.</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">b) Give prominent notice with the combined library that part of it is a work based on "
                "the Library, and explaining where to find the accompanying uncombined form of the same work.</span></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">6. Revised Versions of the GNU Lesser General Public License.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">The Free Software Foundation may publish revised and/or new versions of the GNU Lesser General Public License from time to time. Such new versions will be similar in spirit to th"
                "e present version, but may differ in detail to address new problems or concerns.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">Each version is given a distinguishing version number. If the Library as you received it specifies that a certain numbered version of the GNU Lesser General Public License \u201cor any later version\u201d applies to it, you have the option of following the terms and conditions either of that published version or of any later version published by the Free Software Foundation. If the Library as you received it does not specify a version number of the GNU Lesser General Public L"
                "icense, you may choose any version of the GNU Lesser General Public License ever published by the Free Software Foundation.</span></p>\n"
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\"><br /></p>\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'JetBrains Mono','monospace'; font-size:15.8pt; color:#000000;\">If the Library as you received it specifies that a proxy can decide whether future versions of the GNU Lesser General Public License shall apply, that proxy's public statement of acceptance of any version is permanent authorization for you to choose that version for the Library.</span></p></body></html>",
                None,
            )
        )
        self.pushButtonClose.setText(
            QCoreApplication.translate("aboutDialog", "Close", None)
        )

    # retranslateUi
