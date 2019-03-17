# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import sys

class setserver(QtGui.QDialog):
    def __init__(self, parent=None, funcion_retorno = None, defaultdir = "",  defaultport = ""): #ans = []
        super(setserver, self).__init__(parent)
        self.ret  = funcion_retorno # retorno
        acceptb= QtGui.QPushButton("&Ok")
        acceptb.clicked.connect(self.accepted)
        
        
        self.checkb = QtGui.QCheckBox("Por defecto")
        self.checkb.toggled.connect(self.checkedado)
        #############
        #labname = QtGui.QLabel("Entre su nombre:")
        #self.tname = QtGui.QLineEdit()
        ############
        labip = QtGui.QLabel("Entre IP:")
        self.tip = QtGui.QLineEdit(text = defaultdir)
        ############
        labport = QtGui.QLabel("Entre Puerto:")
        self.tport = QtGui.QLineEdit(text = defaultport)
        #################3
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(labip, 0, 0)
        mainLayout.addWidget(self.tip, 0, 1)
        mainLayout.addWidget(labport, 1, 0)
        mainLayout.addWidget(self.tport, 1, 1)
        #mainLayout.addWidget(labname,2,0)
        #mainLayout.addWidget(self.tname,2,1)
        mainLayout.addWidget(self.checkb,2,0)
        mainLayout.addWidget(acceptb,2,1)

        self.setLayout(mainLayout)
        self.setWindowTitle("Configurar cliente:")
        self.setModal(1)
        
        
    def accepted(self):
        self.close()
        self.ret((self.tip.text(),  self.tport.text()) )

    def checkedado(self):
        if self.checkb.isChecked():
            self.tip.setText("127.0.0.1")
            self.tport.setText("8070")
            #self.tname.setText("annonymous")
            self.tport.setEnabled(0)
            self.tip.setEnabled(0)
        else:
            self.tport.setEnabled(1)
            self.tip.setEnabled(1)

