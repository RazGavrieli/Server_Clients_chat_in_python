import struct
import time
from socket import *
from _thread import *
from os import listdir
from os.path import isfile, join
import os
import hashlib
import pickle

serverSocket = socket(AF_INET, SOCK_STREAM)
host = "127.0.0.1"
port = 55000
msgs = []       # [list of msgs]
pms = {}           # name, [list of msgs]
clients = {}        # id, its name (online clients only)
try:
    serverSocket.bind((host, port))
except:
    print("error")
print('Socket is listening..')
serverSocket.listen(5)

def md5_checksum(data):
    if isinstance(data, (bytes, bytearray)):
        return hashlib.md5(data).hexdigest()

    elif isinstance(data, str):
        return hashlib.md5(data.encode()).hexdigest()

    else:
        raise ValueError('invalid input. input must be string or bytes')

def unrwrap(data):
    if data[:32].decode('utf-8')!=md5_checksum(data[32:]):
        return 1, data[32:]
    data = data.decode('utf-8')
    return data[:32], data[32:35], data[35:]

def wrap(data, id):
    if id > 999:
        print("error segment id too big")
        exit_thread()
    elif 9 >= id >= 0:
        id = "00" + str(id)
    elif 99 >= id >=10:
        id = "0"+str(id)
    else:
        id = str(id)
    if type(data)!=str:
        data = data.decode()

    data = id + data
    checksum = md5_checksum(data.encode('utf-8'))
    data = checksum+data
    return data.encode('utf-8')

def threewayhandshake(udpSocket, connection, file):
    # receive SYN from client
    data, addr = udpSocket.recvfrom(1024)
    # unrwrap the data transfered over UDP, first 32 bytes are checksum
    checksum, id, data = unrwrap(data)
    if data != "SYN" or checksum == 1:
        connection.sendall(str.encode(str("error")))
        exit_thread()

    data = "SYN-ACK" + str(os.path.getsize("files/" + file))
    udpSocket.sendto(wrap(data, 0), addr)

    data, addr = udpSocket.recvfrom(1024)
    checksum, id, data = unrwrap(data)
    if data != "ACK" or checksum == 1:
        connection.sendall(str.encode(str("error")))
        exit_thread()

    return addr

def wrap_payload(data):
    # data is a dictionary where key is id and value is bytes of file
    msg = bytes()
    for i in data.values():
        msg += i
    checksum = md5_checksum(msg)
    msg = pickle.dumps(data)
    msg = bytes(checksum, 'utf-8')+msg
    return msg


def listen_for_acks(values, nacks, udpSocket):
    while len(nacks) != 0 or not values[0]:
        if not values[0]:
            try:
                data, addr = udpSocket.recvfrom(65535)
            except:
                break
        checksum, _, data = unrwrap(data)
        if checksum == 1:
            print("what to do when ack msg gets wrong checksum?")
        if data[:4] == "NACK":
            if values[1]>8:
                values[1]-=5
            if int(data[4:7]) not in nacks:
                nacks.append(int(data[4:7]))
        if data == "ACK-ALL":
            values[0] = True
        elif data[:3] == "ACK":
            list = eval(data[3:])
            if values[1]<50:
                values[1]+=10
            elif values[1]<55:
                values[1]+=5
            elif values[1]<60:
                values[1]+=3
            for i in list:
                if i in nacks:
                    if nacks.index(i) > 2 and values[1]>8:
                        values[1]-=2
                    nacks.remove(i)
    values[0] = True


def frUDP(connection, file):
    connection.sendall(str.encode("connect_frudp"))
    udpSocket = socket(AF_INET, SOCK_DGRAM)
    udport = 55001
    ready = False
    while not ready:
        try:
            udpSocket.bind((host, udport))
            ready = True
        except:
            print("could not udp at "+str(udport))
            udport+=1
            if udport>55015:
                break
    if not ready:
        connection.sendall(str.encode("e"))
        exit_thread()
    else:
        # send over TCP the dedicated port for file transfer
        connection.sendall(str.encode(str(udport)+file))

    print("socket ready at port "+str(udport))
    addr = threewayhandshake(udpSocket, connection, file)

    segments = []
    nacks = []

    # save file to memory
    f = open("files/"+file, "rb")
    b=0
    id = 0
    filesize = os.path.getsize("files/" + file)
    while b<filesize+1000:
        segments.append(f.read(1000))
        nacks.append(id)
        id+=1
        b+=1000

    segments.append(f.read(1000))
    nacks.append(id)
    values = []
    values.append(False)
    values.append(60)
    values[1] = 10   # "speed" as in the amount of segments sent every time
    start_new_thread(listen_for_acks, (values, nacks, udpSocket))
    while not values[0]:

        data = {}

        for id in range(len(segments)):
            if id in nacks and len(data)<=values[1]:
                data[str(id)] = segments[id]

        msg = wrap_payload(data)
        print(len(msg))
        udpSocket.sendto(msg, addr)
    connection.sendall(str.encode("download complete\n"))


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
                files = [f for f in listdir("files") if isfile(join("files", f))]
                if decoded_data[1:] not in files:
                    msg = decoded_data[1:]+" not available\n"
                    #pms[name].append(msg)
                    connection.sendall(str.encode(msg))
                else:
                    msg = "establishing frUDP connection..\n"
                    #pms[name].append(msg)
                    connection.sendall(str.encode(msg))
                    start_new_thread(frUDP, (connection, decoded_data[1:]))

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
