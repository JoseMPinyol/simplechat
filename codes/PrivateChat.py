# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from ChatWriter import ChatWriter


class PrivateChat(QtGui.QDialog):
    def __init__(self, parent=None,socket = None, id = "None", my_id = "Anonymous"):
        super(PrivateChat, self).__init__(parent)
        
        label1 = QtGui.QLabel("Chat Privado con: %s"%id)
        label2 = QtGui.QLabel("Write Here")
        mainLayout = QtGui.QGridLayout()
        
        self.my_id = my_id
        self.id = id
        self.WriteHere = ChatWriter(sockett = socket, id_dest = id ,func=self.Write_in_PrivateChat, my_id = my_id )
        self.PrivChat = QtGui.QTextEdit()
        self.PrivChat.setReadOnly(1) 
        
        
        mainLayout.addWidget(label1,0,0)
        mainLayout.addWidget(self.PrivChat,1,0)
        mainLayout.addWidget(label2,2,0)
        mainLayout.addWidget(self.WriteHere,3,0)
        
        mainLayout.setRowStretch(1,6)
        mainLayout.setRowStretch(3,1)
                
        self.setWindowTitle("Chat Privado")
        self.setLayout(mainLayout)
        
        desktop = QtGui.QDesktopWidget()
        resolution = desktop.screenGeometry()
        (y,x) = (resolution.height(),resolution.width()) #mejorar esta basura
        self.setGeometry(x/2,y/2, 200,200*1.6)
    
    def Write_in_PrivateChat(self,user = None,text = None , color = '"#FF0000"'):#Agrega lo escrito por mi mis
        if user == None: user = self.my_id
        self.PrivChat.append( '<font color=' + color + '>' +  user + ': '  + '''</font></a>''' + text)
        
        
        
