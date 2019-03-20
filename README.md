# Simplechat
## About:
Chat project from when I was a "mid-career" student in 2014. Developed with Reynaldo Gil Pons.
This simple chat project is based on plain TCP sockets in Python.
[Download](bin)

## [BackendCode](codes/my_server.py) :
The server use a non-blocking socket and select.
### The communication protocol is extremely simple:
Each packet (1024 bytes) will have the first 5 bytes for the command to execute:
List of commands:
 - login <username> (The server refuse if someone tries to use your username>
 - write [all, user] <message> (Write in public chat or to someone private chat)
 - list <users> (List all connected users)
 - said [all, user] <userid> <message> (Receive messages in GUI from server) 

## GUI:
This is developed using PyQt and implements the protocol with a simple GUI. 

## Some small recommendations (5 years latter :-) )
- The structure of project could be improved
- The protocol is too simple and should be improved. (Ex: To support large messages and other stuffs).
