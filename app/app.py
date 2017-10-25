#!/usr/bin/python3

import sys
from PyQt4.QtGui import *
from app.controller import Controller

# mixing the Application wrapper with the View
# so Controller is stored in Application
class Application():
    def __init__(self):
        self.app = QApplication([])
        self.defaultWidth = 800
        self.defaultHeight = 500
        self.initGui()
        self.controller = Controller(self)
        self.controller.bind()

    def initGui(self):
        self.window = QWidget()

        self.upperPanel = QHBoxLayout()
        self.propositionInput = QLineEdit()
        self.buttonParse = QPushButton('Parse')
        self.buttonReset = QPushButton('Reset')
        self.upperPanel.addWidget(self.propositionInput)
        self.upperPanel.addWidget(self.buttonParse)
        self.upperPanel.addWidget(self.buttonReset)

        self.middleArea = QTextEdit(self.window)
        self.middleArea.setReadOnly(True)
        self.middleArea.setLineWrapMode(QTextEdit.NoWrap)

        self.lowerPanel = QHBoxLayout()
        self.listOperations = QComboBox()
        self.listOperationsOptions = [
            "Tautology", "Unit propagation", "Pur litteral elimination",
            "Assign true", "Assign false"
        ]
        self.listOperations.addItems(self.listOperationsOptions)
        self.listOperations.setEnabled(False)
        self.listVariables = QComboBox()
        self.listVariables.setEnabled(False)
        self.buttonApply = QPushButton('Apply')
        self.lowerPanel.addWidget(self.listOperations)
        self.lowerPanel.addWidget(self.listVariables)
        self.lowerPanel.addWidget(self.buttonApply)

        self.mainPanel = QVBoxLayout()
        self.mainPanel.addLayout(self.upperPanel)
        self.mainPanel.addWidget(self.middleArea)
        self.mainPanel.addLayout(self.lowerPanel)

        self.window.setLayout(self.mainPanel)
        self.window.resize(self.defaultWidth, self.defaultHeight)
        self.window.setWindowTitle('LogicView')
        self.window.show()

    def showError(self, e):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(str(e))
        msg.setWindowTitle("Error !")
        msg.exec_()

    def clearMiddle(self, proposition):
        self.middleArea.clear()
        self.middleArea.insertPlainText(str(proposition)+"\n")

    def updatePropositionView(self, proposition):
        self.clearMiddle(proposition)
        self.listOperations.setEnabled(True)
        self.listVariables.setEnabled(True)
        var_names = proposition.list_var_names()
        self.listVariables.clear()
        self.listVariables.setEnabled(True)
        self.listVariables.addItems(var_names)

    def start(self):
        sys.exit(self.app.exec_())
