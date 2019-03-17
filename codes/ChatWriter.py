# -*- coding: utf-8 -*-
from PyQt4 import QtGui

class ChatWriter(QtGui.QTextEdit):
# La funci�n es para llamar una vez escrito y poder escribir el valor en el visualizador para el Private Chat
# en el caso del Global no hace falta, pues el servidor lo enviar� para todos...
    def __init__(self, parent = None, sockett = None, statusBar = None , id_dest = 'all', func = None ,my_id = None):
        super(ChatWriter, self).__init__(parent)
        self.statusbar = statusBar
        self.sock = sockett
        self.id_dest = id_dest
        self.func = func
        self.my_id = my_id

    def keyPressEvent(self, event):
            if event.key() == 16777220:#QtCore.Qt.Key_Enter:
                text = ""
                try:
                    text = str(self.toPlainText())
                    print text
                    if self.sock != None:
                        print 'sending:',"write " + self.id_dest+ " " + text
                        self.sock.sendall("write " + self.id_dest+ " " + text) #parche a quitar luego
                    self.clear()
                except:
                    if self.statusbar != None:
                        self.statusbar.showMessage('Error Cliente no Configurado')
                    return
                if self.func != None:
                    self.func(user = self.my_id, text = text , color = '"#023fbf"')
                    
            else: 
                super(ChatWriter, self).keyPressEvent(event)
                #pasar el evento al padre por si lo necesita en algo... Qt

 
