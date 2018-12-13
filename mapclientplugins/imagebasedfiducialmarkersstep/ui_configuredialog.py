# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt\configuredialog.ui'
#
# Created: Thu Dec 13 12:38:32 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ConfigureDialog(object):
    def setupUi(self, ConfigureDialog):
        ConfigureDialog.setObjectName("ConfigureDialog")
        ConfigureDialog.resize(418, 303)
        self.verticalLayout_2 = QtGui.QVBoxLayout(ConfigureDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.configGroupBox = QtGui.QGroupBox(ConfigureDialog)
        self.configGroupBox.setTitle("")
        self.configGroupBox.setObjectName("configGroupBox")
        self.gridLayout = QtGui.QGridLayout(self.configGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.identifier_lineEdit = QtGui.QLineEdit(self.configGroupBox)
        self.identifier_lineEdit.setObjectName("identifier_lineEdit")
        self.gridLayout.addWidget(self.identifier_lineEdit, 0, 1, 1, 2)
        self.identifier_label = QtGui.QLabel(self.configGroupBox)
        self.identifier_label.setObjectName("identifier_label")
        self.gridLayout.addWidget(self.identifier_label, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.preparedData_lineEdit = QtGui.QLineEdit(self.configGroupBox)
        self.preparedData_lineEdit.setObjectName("preparedData_lineEdit")
        self.gridLayout.addWidget(self.preparedData_lineEdit, 1, 1, 1, 1)
        self.preparedData_label = QtGui.QLabel(self.configGroupBox)
        self.preparedData_label.setObjectName("preparedData_label")
        self.gridLayout.addWidget(self.preparedData_label, 1, 0, 1, 1)
        self.preparedData_pushButton = QtGui.QPushButton(self.configGroupBox)
        self.preparedData_pushButton.setObjectName("preparedData_pushButton")
        self.gridLayout.addWidget(self.preparedData_pushButton, 1, 2, 1, 1)
        self.verticalLayout_2.addWidget(self.configGroupBox)
        self.buttonBox = QtGui.QDialogButtonBox(ConfigureDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(ConfigureDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ConfigureDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ConfigureDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConfigureDialog)

    def retranslateUi(self, ConfigureDialog):
        ConfigureDialog.setWindowTitle(QtGui.QApplication.translate("ConfigureDialog", "Configure Step", None, QtGui.QApplication.UnicodeUTF8))
        self.identifier_label.setText(QtGui.QApplication.translate("ConfigureDialog", "identifier:  ", None, QtGui.QApplication.UnicodeUTF8))
        self.preparedData_label.setText(QtGui.QApplication.translate("ConfigureDialog", "Prepared data:  ", None, QtGui.QApplication.UnicodeUTF8))
        self.preparedData_pushButton.setText(QtGui.QApplication.translate("ConfigureDialog", "...", None, QtGui.QApplication.UnicodeUTF8))

