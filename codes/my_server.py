#!usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import threading
import time
import signal, os
import select

PORT = 8070
HOST = None
packages_list = []
Spackages_list = threading.Semaphore()

list_connections = []
Slist_conections = threading.Semaphore()

users = {}
Susers =threading.Semaphore()


class Broadcast(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = 1
    def run(self):
        global packages_list, list_connections
        while self.running:
            #print threading.currentThread()
            if len(packages_list) > 0:
                Spackages_list.acquire()
                pl = packages_list[:]
                packages_list = []
                Spackages_list.release()
                for pack in pl:
                    Slist_conections.acquire()
                    for conn in list_connections:
                        if pack[1] == None or pack[1] == conn.login:
                            conn.send(pack[0])
                    Slist_conections.release()
            time.sleep(0)
    def kill(self):
        self.running = 0

class Command_Control:
    def __init__(self):
        self.buffer = ""
        self.list_command = []
        self.login = ""
    def parse(self, command):
        com = command[0:5]
        if com == "write":
            rest = command.split(' ', 2)
            if rest[1] == "all":
                package = "said all " + self.login + " " + rest[2]
                Spackages_list.acquire()
                packages_list.append((package, None))
                Spackages_list.release()
            else:
                package = "said user " + self.login + " " + rest[2]
                Spackages_list.acquire()
                packages_list.append((package, rest[1]))
                Spackages_list.release()
            print rest
        print command
class Connection_chat_sending():
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.login = ""
        self.sem = threading.Semaphore()
    def send(self, package):
        self.conn.sendall(package)

class Connection_chat_listen(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.running = 1
        self.conn = conn
        self.addr = addr
        self.login = ""
        self.cmdctr = Command_Control()
    def kill(self):
        self.running = 0
    def run(self):
        # Select loop for listen
        self.cmdctr.login = self.login
        while self.running:
            # Handle sockets
            rs, ws, es = select.select([self.conn],[], [], 1)
            if len(rs) == 0: continue
            data = self.conn.recv(1024)
            if data == "exit":
                break
            if data:
                self.cmdctr.parse(data)
            else:
                break
            time.sleep(0)
        self.conn.close()


class Authentication(threading.Thread):
    def __init__(self, sock, chat_listen, chat_send):
        threading.Thread.__init__(self)
        self.sock = sock 
        self.chat_listen = chat_listen
        self.chat_send = chat_send
    def run(self):
        counter = 0
        while not self.authentication() and counter < 3:  
            self.sock.sendall("wrong")
            counter = counter + 1
        if counter == 3:
            return
            
        self.chat_listen.start()
        #self.list_connections.append(self.chat_listen)
        Slist_conections.acquire()
        list_connections.append(self.chat_send)
        Slist_conections.release()
    def authentication(self):
        data= self.sock.recv(1024)
        if not data.strip(): return False
        parts = data.split(' ', 1)
        cmd = parts[0]
        if cmd != "login": return False
        if len(parts) > 2: return False
        user = str(parts[1])
        Susers.acquire()
        if users.get(user) != None: 
            Susers.release()
            return False
        users[user] = len(users)
        Susers.release()
        self.chat_send.login = user
        self.chat_listen.login = user
        self.sock.sendall("accepted")
        return True


class Chat_Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = 1
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST,PORT))
        s.listen(5)
        while self.running:
            #print threading.currentThread()
            while self.running:
                try:
                    conn, addr = s.accept()
                    break
                except socket.error:
                    continue
            if not self.running: break
            print "Connection accepted from ", conn, addr
            conn.setblocking(1)
            new_chat_listen = Connection_chat_listen(conn, addr)
            new_chat_send = Connection_chat_sending(conn, addr)
            
            server_auth = Authentication(conn, new_chat_listen, new_chat_send)
            server_auth.start()
            
            
            
        s.close()
    def kill(self):
        self.running = 0
    def check_to_kill(self):
        return self.running




if __name__ == "__main__":
    chat_server = Chat_Server() 
    chat_server.start()
    broad = Broadcast()
    broad.start()
    def handler(signum, frame):
        print 'Signal handler called with signal', signum
        chat_server.kill()
        broad.kill()
        time.sleep(0)
        for th in threading.enumerate():
            if th != threading.currentThread():
                th.kill()
        exit()
    signal.signal(signal.SIGINT, handler)
    while True:
        #print threading.currentThread()
        time.sleep(5)
        Susers.acquire()
        if len(users) > 0:
            Susers.release()
            pusers = "list "
            Slist_conections.acquire()
            for conn in list_connections:
                pusers += conn.login + " "
            for conn in list_connections:
                conn.sem.acquire()
                try:
                    conn.send(pusers)
                except socket.error:
                    conn.sem.release()
                    Susers.acquire()
                    users.pop(conn.login)
                    Susers.release()
                    list_connections.remove(conn)
                    continue
                conn.sem.release()
            Slist_conections.release()
        else: Susers.release()
