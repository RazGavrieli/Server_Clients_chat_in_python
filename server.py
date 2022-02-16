import threading
from socket import *
from _thread import *

serverSocket = socket(AF_INET, SOCK_STREAM)
addr = ("127.0.0.1", 55000)
msgs = []
clients = {}
try:
    serverSocket.bind(addr)
except:
    print("error")
print('Socket is listening..')
serverSocket.listen(5)

def newconnection(connection, id):
    print(clients)
    data = connection.recv(2048)
    if not data:
        print("not data!")
        exit_thread()
    name = data.decode('utf-8')
    clients[id] = name
    print(name, "connected with id ", id)
    receive_req_from_client(connection, name, id)


def get_users(connection):
    for i in clients.values():
        connection.sendall(str.encode(i))

def receive_req_from_client(connection, name, id):
    start_new_thread(send_msg_to_client, (connection, name, id))
    connected = True
    while connected:
        try:
            data = connection.recv(2048)
            if not data:
                print("not data! from ", name, id)
                connected = False
                decoded_data = "disconnect"
            decoded_data = data.decode('utf-8')
            print("got ", decoded_data, " from ", name, id)
            if decoded_data == "set_msg_all":
                print("msg sending", decoded_data)
                data = connection.recv(2048)
                msg = name + ": " + data.decode('utf-8')+"\n"
                msgs.append(msg)
            elif decoded_data == "disconnect":
                connected = False
            elif decoded_data == "get_users":
                get_users(connection)
            else:
                print("error got weird command:"+ decoded_data)
        except:
            break
    print(id, "disconnected \n")
    clients.pop(id)
    connection.close()
    msg = name+" disconnected\n"
    msgs.append(msg)


def send_msg_to_client(connection, name, id):
    prevmsgs = []
    while id in clients.keys():
        if len(msgs)!=len(prevmsgs):
            for i in msgs:
                if i not in prevmsgs:
                    connection.sendall(str.encode(i))
            prevmsgs = msgs.copy()


id = 0
while True:
    Client, address = serverSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    id += 1
    start_new_thread(newconnection, (Client, id))
