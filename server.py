import threading
from socket import *
from _thread import *
from os import listdir
from os.path import isfile, join

serverSocket = socket(AF_INET, SOCK_STREAM)
addr = ("127.0.0.1", 55000)
msgs = [] # [list of msgs]
pms = {} # name, [list of msgs]
clients = {} # id, its name (online clients only)
try:
    serverSocket.bind(addr)
except:
    print("error")
print('Socket is listening..')
serverSocket.listen(5)

def newconnection(connection, id):
    data = connection.recv(2048)
    if not data:
        print("not data!")
        exit_thread()
    name = data.decode('utf-8')
    while name in clients.values():
        name += str(id)

    clients[id] = name
    print(name, "connected with id ", id)
    pms[name] = []
    msgs.append(name+"["+str(id)+"] connected\n")
    receive_req_from_client(connection, name, id)


def get_users(connection):
    msg = "---ONLINE USERS---\n"
    connection.sendall(str.encode(msg))
    for i in clients:
        msg = clients.get(i)+"["+str(i)+"]\n"
        connection.sendall(str.encode(msg))
    #connection.sendall("\n")


def get_files(connection):
    files = [f for f in listdir("files") if isfile(join("files", f))]
    if len(files)==0:
        msg = "---NO FILES AVAILABLE---\n"
        connection.sendall(str.encode(msg))
    else:
        msg = "---AVAILABLE FILES---\n"
        connection.sendall(str.encode(msg))
        i = 1
        for f in files:
            msg = str(i)+". "+f+"\n"
            i+=1
            connection.sendall(str.encode(msg))


def receive_req_from_client(connection, name, id):
    start_new_thread(send_msg_to_client, (connection, name, id))
    connected = True
    while connected:
        try:
            data = connection.recv(2048)
            if not data:
                print("not data! from ", name, id)
                connected = False
            decoded_data = data.decode('utf-8')
            print("got ", decoded_data, " from ", name, id)
            if decoded_data == "set_msg":
                data = connection.recv(2048)
                decoded_data = data.decode('utf-8')
                splited_msg = decoded_data.split()
                target = splited_msg[0]
                decoded_data = decoded_data[len(target)+1:]
                print("target is "+target)
                msg = "|PM| " + name + "[" + str(id) + "]: " + decoded_data + "\n"
                print("msg is "+msg)

                if target in pms.keys():
                    pms[name].append(msg)
                    print("entering ")
                    pms[target].append(msg)
                elif target.isdecimal():
                    if int(target) in clients.keys():
                        pms[name].append(msg)
                        print("transfuming")
                        targetemp = clients.get(int(target))
                        print(targetemp)
                        pms[targetemp].append(msg)
                else:
                    msg = target+" not online\n"
                    pms[name].append(msg)
            elif decoded_data == "download_file":
                print("downloading file process")
                data = connection.recv(2048)
                decoded_data = data.decode('utf-8')
                print(decoded_data)
                files = [f for f in listdir("files") if isfile(join("files", f))]
                if decoded_data[1:] not in files:
                    msg = decoded_data[1:]+" not available\n"
                    #pms[name].append(msg)
                    connection.sendall(str.encode(msg))
                else:
                    msg = "establishing frUDP connection\n"
                    #pms[name].append(msg)
                    connection.sendall(str.encode(msg))
                    #################
                    ### UDP magic ###
                    #################
            elif decoded_data == "set_msg_all":
                print("msg sending", decoded_data)
                data = connection.recv(2048)
                msg = name + "["+str(id)+"]: " + data.decode('utf-8')+"\n"
                print("size is ", len(str.encode(msg)))
                msgs.append(msg)
            elif decoded_data == "disconnect":
                connected = False
            elif decoded_data == "get_users":
                get_users(connection)
            elif decoded_data == "get_files":
                get_files(connection)
            else:
                print("error got weird command:"+ decoded_data)
        except:
            print("problem occured")
            break
    print(id, "disconnected \n")
    clients.pop(id)
    connection.close()
    msg = name+" disconnected\n"
    msgs.append(msg)


def send_msg_to_client(connection, name, id):
    prevmsgs = []
    prevpms = []
    while id in clients.keys():
        if len(msgs)!=len(prevmsgs):
            for i in msgs:
                if i not in prevmsgs:        # cause bugs if msg already was sent in the past
                    connection.sendall(str.encode(i))
            prevmsgs = msgs.copy()
        if pms.get(name) is not None:
            if len(pms.get(name))!=len(prevpms):
                for i in pms.get(name):
                    if i not in prevpms:      # cause bugs if msg already was sent in the past
                        connection.sendall(str.encode(i))
                prevpms = pms.get(name).copy()


id = 0
while True:
    Client, address = serverSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    id += 1
    start_new_thread(newconnection, (Client, id))
