# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gpt2.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QPushButton, QSizePolicy, QSpacerItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_IOGB(object):
    def setupUi(self, IOGB):
        if not IOGB.objectName():
            IOGB.setObjectName(u"IOGB")
        IOGB.resize(400, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(IOGB.sizePolicy().hasHeightForWidth())
        IOGB.setSizePolicy(sizePolicy)
        IOGB.setStyleSheet(u"/* --- GLOBAL DARK THEME --- */\n"
"QWidget {\n"
"    background-color: #588182;  /* Deep black background */\n"
"    color: #0c0c0c;             /* High contrast off-white text */\n"
"    font-family: \"Roboto Mono\", \"Consolas\", monospace;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"/* --- FRAMES --- */\n"
"QFrame {\n"
"    background-color: #101010;  /* Slightly off-black for depth */\n"
"    border: 2px solid #222222;  /* High contrast yet subtle */\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"/* --- GROUP BOXES --- */\n"
"QGroupBox {\n"
"    border: 2px solid #0a0a0a; /* Slightly brighter for separation */\n"
"    border-radius: 8px;\n"
"    margin-top: 8px;\n"
"    font-weight: bold;\n"
"    color: #60ffe8;  /* Muted neon purple */\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position: top center;\n"
"    padding: 4px;\n"
"    color: #60ffe8;\n"
"    background-color: #0a0a0a;\n"
"}\n"
"\n"
"/* --- TEXT FIELDS --- */\n"
"QTextEdit, QLineEdit {\n"
"    background-col"
                        "or: #151515;\n"
"    border: 2px solid #333333;\n"
"    border-radius: 3px;\n"
"    color: #e0e0e0;\n"
"    padding: 6px;\n"
"    selection-background-color: #4feeff; /* Highlight */\n"
"}\n"
"\n"
"/* --- BUTTONS --- */\n"
"QPushButton {\n"
"    background-color: #181818;\n"
"    border: 2px solid #444444;\n"
"    border-radius: 5px;\n"
"    padding: 6px;\n"
"    font-weight: bold;\n"
"    color: #E0E0E0;\n"
"    transition: all 0.2s ease-in-out;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #222222;\n"
"    border-color: #4feeff;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #4feeff;\n"
"    color: #0a0a0a;\n"
"}\n"
"\n"
"/* --- SPACERS --- */\n"
"QSpacerItem {\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"/* --- MAIN FRAME HIGH CONTRAST --- */\n"
"QFrame#mainFrame {\n"
"    border: 3px solid #BB86FC;\n"
"    background-color: #0d0d0d;\n"
"}\n"
"\n"
"/* --- GROUP BOX FRAME --- */\n"
"QFrame#GBFrame {\n"
"    border: 3px solid #444444;\n"
"    background-color: #131313;\n"
""
                        "}\n"
"\n"
"/* --- TEXT BOXES & INPUT FIELDS --- */\n"
"QTextEdit {\n"
"    background-color: #121212;\n"
"    border: 2px solid #2d2d2d;\n"
"    border-radius: 5px;\n"
"    color: #e0e0e0;\n"
"    selection-background-color: #BB86FC;\n"
"}\n"
"\n"
"/* --- INPUT FIELDS --- */\n"
"QLineEdit {\n"
"    background-color: #121212;\n"
"    border: 2px solid #444;\n"
"    color: #e0e0e0;\n"
"    padding: 5px;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"QLineEdit:focus {\n"
"    border-color: #BB86FC;\n"
"    background-color: #181818;\n"
"}\n"
"\n"
"/* --- DYSTOPIAN BUTTONS --- */\n"
"QPushButton#pauseGptPlayBtn {\n"
"    background-color: #660000; /* Deep red for danger */\n"
"    border: 2px solid #aa0000;\n"
"    color: #e0e0e0;\n"
"}\n"
"\n"
"QPushButton#pauseGptPlayBtn:hover {\n"
"    background-color: #880000;\n"
"    border-color: #ff0000;\n"
"}\n"
"\n"
"QPushButton#pauseGptPlayBtn:pressed {\n"
"    background-color: #ff0000;\n"
"    color: #0a0a0a;\n"
"}\n"
"\n"
"/* --- SEND BUTTON (CYBERPUNK GREEN) --- */\n"
""
                        "QPushButton#sendBtn {\n"
"    background-color: #004400;\n"
"    border: 2px solid #00aa00;\n"
"    color: #e0e0e0;\n"
"}\n"
"\n"
"QPushButton#sendBtn:hover {\n"
"    background-color: #006600;\n"
"    border-color: #00ff00;\n"
"}\n"
"\n"
"QPushButton#sendBtn:pressed {\n"
"    background-color: #00ff00;\n"
"    color: #0a0a0a;\n"
"}\n"
"\n"
"/* --- HIGHLIGHT VALID MOVES (FOR CHESS) --- */\n"
"QPushButton[validmove=\"true\"] {\n"
"    background-color: #007722;\n"
"    border: 2px solid #00cc44;\n"
"}\n"
"\n"
"/* --- ERROR STATES --- */\n"
"QLineEdit:focus, QTextEdit:focus {\n"
"    border: 2px solid #60ffe8;\n"
"}\n"
"")
        self.verticalLayout = QVBoxLayout(IOGB)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.mainFrame = QFrame(IOGB)
        self.mainFrame.setObjectName(u"mainFrame")
        self.mainFrame.setFrameShape(QFrame.StyledPanel)
        self.mainFrame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.mainFrame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.IO_GB = QGroupBox(self.mainFrame)
        self.IO_GB.setObjectName(u"IO_GB")
        self.verticalLayout_3 = QVBoxLayout(self.IO_GB)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.GBFrame = QFrame(self.IO_GB)
        self.GBFrame.setObjectName(u"GBFrame")
        self.GBFrame.setFrameShape(QFrame.StyledPanel)
        self.GBFrame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.GBFrame)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.gptResponseWindow = QTextEdit(self.GBFrame)
        self.gptResponseWindow.setObjectName(u"gptResponseWindow")
        self.gptResponseWindow.setReadOnly(True)

        self.verticalLayout_4.addWidget(self.gptResponseWindow)

        self.userInputTextEdit = QTextEdit(self.GBFrame)
        self.userInputTextEdit.setObjectName(u"userInputTextEdit")

        self.verticalLayout_4.addWidget(self.userInputTextEdit)

        self.btnWidget = QWidget(self.GBFrame)
        self.btnWidget.setObjectName(u"btnWidget")
        self.horizontalLayout = QHBoxLayout(self.btnWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cancelBn = QPushButton(self.btnWidget)
        self.cancelBn.setObjectName(u"cancelBn")
        self.cancelBn.setStyleSheet(u"/* --- GLOBAL DARK THEME --- */\n"
"QWidget {\n"
"    background-color: #0a0a0a;  /* Deep black background */\n"
"    color: #0a0a0a;             /* High contrast off-white text */\n"
"    font-family: \"Roboto Mono\", \"Consolas\", monospace;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"/* --- FRAMES --- */\n"
"QFrame {\n"
"    background-color: #101010;  /* Slightly off-black for depth */\n"
"    border: 2px solid #222222;  /* High contrast yet subtle */\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"/* --- GROUP BOXES --- */\n"
"QGroupBox {\n"
"    border: 2px solid #0a0a0a; /* Slightly brighter for separation */\n"
"    border-radius: 8px;\n"
"    margin-top: 8px;\n"
"    font-weight: bold;\n"
"    color: #BB86FC;  /* Muted neon purple */\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position: top center;\n"
"    padding: 4px;\n"
"    color: #BB86FC;\n"
"    background-color: #0a0a0a;\n"
"}\n"
"\n"
"/* --- TEXT FIELDS --- */\n"
"QTextEdit, QLineEdit {\n"
"    background-col"
                        "or: #151515;\n"
"    border: 2px solid #333333;\n"
"    border-radius: 3px;\n"
"    color: #e0e0e0;\n"
"    padding: 6px;\n"
"    selection-background-color: #BB86FC; /* Highlight */\n"
"}\n"
"\n"
"/* --- BUTTONS --- */\n"
"QPushButton {\n"
"    background-color: #181818;\n"
"    border: 2px solid #444444;\n"
"    border-radius: 5px;\n"
"    padding: 6px;\n"
"    font-weight: bold;\n"
"    color: #E0E0E0;\n"
"    transition: all 0.2s ease-in-out;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #222222;\n"
"    border-color: #BB86FC;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #BB86FC;\n"
"    color: #0a0a0a;\n"
"}\n"
"\n"
"/* --- SPACERS --- */\n"
"QSpacerItem {\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"/* --- MAIN FRAME HIGH CONTRAST --- */\n"
"QFrame#mainFrame {\n"
"    border: 3px solid #BB86FC;\n"
"    background-color: #0d0d0d;\n"
"}\n"
"\n"
"/* --- GROUP BOX FRAME --- */\n"
"QFrame#GBFrame {\n"
"    border: 3px solid #444444;\n"
"    background-color: #131313;\n"
""
                        "}\n"
"\n"
"/* --- TEXT BOXES & INPUT FIELDS --- */\n"
"QTextEdit {\n"
"    background-color: #121212;\n"
"    border: 2px solid #2d2d2d;\n"
"    border-radius: 5px;\n"
"    color: #e0e0e0;\n"
"    selection-background-color: #BB86FC;\n"
"}\n"
"\n"
"/* --- INPUT FIELDS --- */\n"
"QLineEdit {\n"
"    background-color: #121212;\n"
"    border: 2px solid #444;\n"
"    color: #e0e0e0;\n"
"    padding: 5px;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"QLineEdit:focus {\n"
"    border-color: #BB86FC;\n"
"    background-color: #181818;\n"
"}\n"
"\n"
"/* --- DYSTOPIAN BUTTONS --- */\n"
"QPushButton#pauseGptPlayBtn {\n"
"    background-color: #660000; /* Deep red for danger */\n"
"    border: 2px solid #aa0000;\n"
"    color: #e0e0e0;\n"
"}\n"
"\n"
"QPushButton#pauseGptPlayBtn:hover {\n"
"    background-color: #880000;\n"
"    border-color: #ff0000;\n"
"}\n"
"\n"
"QPushButton#pauseGptPlayBtn:pressed {\n"
"    background-color: #ff0000;\n"
"    color: #0a0a0a;\n"
"}\n"
"\n"
"/* --- SEND BUTTON (CYBERPUNK GREEN) --- */\n"
""
                        "QPushButton#sendBtn {\n"
"    background-color: #004400;\n"
"    border: 2px solid #00aa00;\n"
"    color: #e0e0e0;\n"
"}\n"
"\n"
"QPushButton#sendBtn:hover {\n"
"    background-color: #006600;\n"
"    border-color: #00ff00;\n"
"}\n"
"\n"
"QPushButton#sendBtn:pressed {\n"
"    background-color: #00ff00;\n"
"    color: #0a0a0a;\n"
"}\n"
"\n"
"/* --- HIGHLIGHT VALID MOVES (FOR CHESS) --- */\n"
"QPushButton[validmove=\"true\"] {\n"
"    background-color: #007722;\n"
"    border: 2px solid #00cc44;\n"
"}\n"
"\n"
"/* --- ERROR STATES --- */\n"
"QLineEdit:focus, QTextEdit:focus {\n"
"    border: 2px solid #ff4444;\n"
"}\n"
"")

        self.horizontalLayout.addWidget(self.cancelBn)

        self.sendBtn = QPushButton(self.btnWidget)
        self.sendBtn.setObjectName(u"sendBtn")

        self.horizontalLayout.addWidget(self.sendBtn)


        self.verticalLayout_4.addWidget(self.btnWidget)

        self.verticalLayout_4.setStretch(0, 70)
        self.verticalLayout_4.setStretch(1, 20)
        self.verticalLayout_4.setStretch(2, 10)

        self.verticalLayout_3.addWidget(self.GBFrame)


        self.verticalLayout_2.addWidget(self.IO_GB)


        self.verticalLayout.addWidget(self.mainFrame)


        self.retranslateUi(IOGB)

        QMetaObject.connectSlotsByName(IOGB)
    # setupUi

    def retranslateUi(self, IOGB):
        IOGB.setWindowTitle(QCoreApplication.translate("IOGB", u"I/O View", None))
        self.IO_GB.setTitle(QCoreApplication.translate("IOGB", u"IO  LLM", None))
        self.cancelBn.setText(QCoreApplication.translate("IOGB", u"Caneel", None))
        self.sendBtn.setText(QCoreApplication.translate("IOGB", u"Send", None))
    # retranslateUi

