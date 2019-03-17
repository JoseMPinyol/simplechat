# -*- coding: utf-8 -*-
## usar señales para notificar al estatus bar 
## y no hacer acceso directo desde el thread
import sys
import thread
from PyQt4 import QtGui ,  QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QMainWindow
import setserver
import socket
import ChatWriter
from PrivateChat import PrivateChat



class mainwindow(QMainWindow): #, Ui_MainWindow

    def __init__(self, parent = None):
        super(mainwindow, self).__init__(parent)
        
        self.semaphoro = thread.allocate() # ya no se usa eliminar del código
        self.winconfig = setserver.setserver(funcion_retorno = self.set_address)
        self.my_id = None
        self.msocket = None
        self.address = (None, None)
        
        self.Chats = {} # diccionario con todos los Chats
        
        frame = QtGui.QFrame(self)
        grid = QtGui.QGridLayout(frame)
        grid.setSpacing(4)
        grid.setMargin(4)

        
        labelChat = QtGui.QLabel(frame, text = "Global Chat:")
        self.GlobalChat = QtGui.QTextEdit(frame)
        self.GlobalChat.setReadOnly(1)
        labelwrite = QtGui.QLabel(frame, text = "Escribe aqui:")
        self.WriteHere = ChatWriter.ChatWriter(parent= frame,  sockett = self.msocket , statusBar= self.statusBar())
        labelusers = QtGui.QLabel(frame, text = "Usuarios Conectados:") 
        self.users_conected = QtGui.QListWidget(frame);
        #################################################
		##########################Usar dic... para todos los conectados...
        self.users_conected.itemDoubleClicked.connect(self.clicked_user)
        ############################################################
		############################################################
        ##############Creando los menus
        self.fileMenu = self.menuBar().addMenu("&Acciones")
        self.fileMenu.addAction(
            QtGui.QAction("&Configurar", self,
            shortcut='Ctrl+O',
            statusTip="Configurar servidor",
            triggered=self.configurar)
        )
        self.fileMenu.addAction(
            QtGui.QAction("&Crear Servidor", self,
            shortcut='Ctrl+R',
            statusTip="Crear Servidor",
            triggered=self.start_server)
        )
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(
            QtGui.QAction("E&xit", self, 
            shortcut="Ctrl+Q",
            statusTip="Sale del Chat",
            triggered=self.cierra)
        )

        grid.addWidget(labelChat, 0, 0)
        grid.addWidget(self.GlobalChat, 1,0)
        grid.setRowStretch(1,6)
        
        grid.addWidget(labelwrite, 2, 0)
        grid.addWidget(self.WriteHere, 3, 0)
        grid.setRowStretch(3,1)
        
        grid.setColumnStretch(0,3)
        
        grid.addWidget(labelusers,0,1)
        grid.addWidget(self.users_conected,1,1,-1,1)
        grid.setColumnStretch(1,1)
        self.setCentralWidget(frame)
        
        ############################Establecer tamaño de ventana/////////////////////
        desktop = QtGui.QDesktopWidget()
        resolution = desktop.screenGeometry()
        (y,x) = (resolution.height(),resolution.width())
        self.setGeometry(5*x/6,2*y/3 - 50,x/6,y/3) #mejorar esta basura
        

        self.setWindowTitle("Simple Chat:")
        self.statusBar().showMessage(u'Bienvenido a Simple Chat')
        ###################Señales para el Thread Principal#############################
        #QObject.connect(self, SIGNAL("crear_usuario"),self.create_private_chat)
        QObject.connect(self,SIGNAL("Sescribir_chat_privado"),self.escribir_chat_privado)
        QObject.connect(self,SIGNAL("Sactualizar_usuarios"),self.set_connected_users)
        QObject.connect(self,SIGNAL("Swrite_global_chat"),self.Write_Global)
        QObject.connect(self,SIGNAL("Sinformar"),self.informar)
        
        
    def configurar(self):
        #self.msocket.close() #debe mejorarse
        self.winconfig.show()
    def cierra(self):
        #desconectar socket
        self.msocket.close()
        
        #########
        self.close()
    def set_address(self, addr): #set and connect socket
        ############validar### que exista
        self.msocket = socket.socket()
        self.WriteHere.sock = self.msocket #parche
        try:
            print addr
            self.address = (str(addr[0]) ,int(addr[1]) )
            self.msocket.connect(self.address)
        except:
            self.statusBar().showMessage(u'Error en la direción o el servidor no existe')
            self.winconfig.show()
            return
        
        self.statusBar().showMessage(u'Conexión Exitosa')
        intentos = 0
        
        while True:
            name, ok = QtGui.QInputDialog.getText(self, "Nick?",
                "Nombre de Usuario:", QtGui.QLineEdit.Normal,
                QtCore.QDir.home().dirName())
            try:
                rname = str(name)
            except:
                self.statusBar().showMessage(u'No ANSI caracter')
                continue
            if " " in rname:
                self.statusBar().showMessage(u'El nombre no puede contener espacios')
                continue
            if len(rname) < 3:
                self.statusBar().showMessage(u'El nombre debe tener más de 3 caracteres')
                continue
            if rname.isalnum() == False :
                self.statusBar().showMessage(u'Solo caracteres alphanuméricos')
                continue
                
            self.msocket.sendall("login " + rname)
            data = self.msocket.recv(1024)
            if data == "accepted":
                self.statusBar().showMessage('Saludos: ' + rname )
                self.my_id = rname
                break
            else:
                intentos += 1
                self.statusBar().showMessage(u'Error en el nombre, ya está en uso')
                if intentos == 3:
                    self.statusBar().showMessage(u'Conexión terminada por el servidor')
                    self.msocket.close()
                    return
        thread.start_new_thread(self.read_from_server, ( )) #Thread para procesar la lectura del socket

    def read_from_server(self):
        while True:
            try:
                rec = self.msocket.recv(1024)
                if rec[:5] == 'said ': #global Flag
                    print rec
                    ident = rec.split(" ",2)[1]
                    if ident == "all":
                        info = rec.split(" ",3)
                        self.emit(SIGNAL("Swrite_global_chat"), info[2] , info[3]  )
                    else:
                        destinatario = rec.split(" ",3)[2]
                        self.emit(SIGNAL("Sescribir_chat_privado"),destinatario , rec.split(" ")[2] ,rec.split(" ",3)[3]  )
                        
                elif rec[:5] == 'list ':
                    self.emit(SIGNAL("Sactualizar_usuarios"), rec.split(" ")[1:-1] ) #quitarme el espacio vacío que Reynaldo manda
                else:
                    print u'Violación del Protocolo: ',rec 
            except:
                self.emit(SIGNAL("Sinformar"), u'Se cayó la conexión con el servidor' ) #debe usar señales
                thread.exit()
        
    def informar(self,text):
        self.statusBar().showMessage(text)
        
    def set_connected_users(self,lista_users):
        self.users_conected.clear()
        for user in lista_users:
            if self.my_id == user: continue
            if self.Chats.has_key(user):
                pass
            else:
                self.Chats[user] = None # self.create_private_chat(user) #####dejame ver
        _temp = []
        self.semaphoro.acquire()
        for key in self.Chats: #hacer en dos pasadas si error
            if not key in lista_users:
                _temp.append(key)
        
        for key in _temp:
            self.Chats.pop(key)
        
        for key in self.Chats:
            self.users_conected.addItem(key)
        self.semaphoro.release()
            
    
    def start_server(self):#######esto actualmente no funciona bien
        puerto = 8070
        print sys.argv
        import os
        serv = 'server.exe'
        if sys.platform[0] != 'w':
            serv = './server' #para poder ejecutar... el servidor
        self.statusBar().showMessage(u'Creando Servidor... en puerto: %d'%(puerto,))
        thread.start_new_thread(os.system , (serv,)) #mala práctica arreglar y hacer bien
        self.statusBar().showMessage(u'Servidor creado en puerto: %d'%(puerto,))
                                         
    def create_private_chat(self,user):
        self.semaphoro.acquire()
        self.Chats[user] = PrivateChat(id = user,socket = self.msocket , my_id = self.my_id)
        self.semaphoro.release()
    
    def escribir_chat_privado(self,destinatario,user,text):
        if self.Chats[destinatario] == None: # si no existe lo crea
            self.create_private_chat(destinatario)
        self.Chats[destinatario].Write_in_PrivateChat(user = user, text = text)
        self.Chats[destinatario].show()
    
    def clicked_user(self,item):
        idu = str(item.text())
        if self.Chats[idu] == None:#lo crea si no existe
            self.create_private_chat(idu)
        self.Chats[idu].show()
        #print self.users_conected.AboveItem
    
    def color_from_user(self,user):
        val = ""
        last = '0'
        cuser = user.lower()
        for i in range(6):
            if i < len(cuser):
                temp = cuser[i]
                if temp > 'f':
                    temp = last
                val = val + temp
                last = temp
            else: val = val + '0'
        color = '"#' + val  + '"'
        return color
        
    
    def Write_Global(self,user,text):
        color = self.color_from_user(user)
        self.GlobalChat.append( '<font color=' + color + '>' +  user + ': '  + '''</font></a>''' + text)
   
        

        
         


app=QtGui.QApplication(sys.argv)
main= mainwindow()
main.show()
ret = app.exec_()

