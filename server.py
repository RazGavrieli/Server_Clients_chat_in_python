
from socket import *
from os import listdir
from os.path import isfile, join
from frUDP import *

serverSocket = socket(AF_INET, SOCK_STREAM)
host = gethostbyname(gethostname())
port = 55000
msgs = []       # [list of msgs]
pms = {}           # name, [list of msgs]
clients = {}        # id, its name (online clients only)
try:
    serverSocket.bind((host, port))
except:
    print("error")
print('Socket is listening at ', host)
serverSocket.listen(5)


def listen_for_acks(values, nacks, udpSocket):
    while len(nacks) != 0 or not values[0]:
        if not values[0]:
            try:
                data, addr = udpSocket.recvfrom(65535)
            except:
                break
        checksum, _, data = unwrap(data)
        if checksum == 1:
            print("what to do when ack msg gets wrong checksum?")
        if data[:4] == "NACK":
            if values[1]>8:         # CC still WIP
                values[1]-=5        # CC still WIP
            if int(data[4:7]) not in nacks:
                nacks.append(int(data[4:7]))
        if data == "ACK-ALL":
            values[0] = True
        elif data[:3] == "ACK":
            list = eval(data[3:])
            if values[1]<50:        # CC still WIP
                values[1]+=10       # CC still WIP
            elif values[1]<55:      # CC still WIP
                values[1]+=5        # CC still WIP
            elif values[1]<60:      # CC still WIP
                values[1]+=3        # CC still WIP
            for i in list:
                if i in nacks:
                    if nacks.index(i) > 2 and values[1]>8:  # CC still WIP
                        # this checks for latency, where packet 2 arrived before packet 1
                        values[1]-=2                        # CC still WIP
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
    addr = serverside_threewayhandshake(udpSocket, connection, file)

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
        #print(len(msg))
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
    msg = name+"["+str(id)+"] disconnected\n"
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
