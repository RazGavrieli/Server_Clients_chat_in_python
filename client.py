import threading
from socket import *
from _thread import *

ClientMultiSocket = socket(AF_INET, SOCK_STREAM)
host = '127.0.0.1'
port = 55000
print('Waiting for connection response')
try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))
print("connected")
# res = ClientMultiSocket.recv(1024)

def listen(ClientMultiSocket):
    connected = True
    while connected:
        res = ClientMultiSocket.recv(1024)
        if not res:
            connected = False
        print(res.decode('utf-8'))


Input = input('enter nickname: ')
ClientMultiSocket.send(str.encode(Input))

start_new_thread(listen, (ClientMultiSocket, ))
connected = True
while connected:
    Input = input('')
    ClientMultiSocket.send(str.encode(Input))
    if Input == "disconnect":
        connected = False

ClientMultiSocket.close()