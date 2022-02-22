import random
import time
from socket import *
from _thread import *
from tkinter import *
from functools import partial
import hashlib
import math
from pathlib import Path
import pickle
from tkinter.ttk import Progressbar

clientSocket = socket(AF_INET, SOCK_STREAM)
##############################################################################################################
win = Tk()
win.geometry("200x100")
host = []


def sethost(host):
    ip = text.get("1.0", "end - 1 chars")
    if ip == "":
        host.append("127.0.0.1")
    else:
        host.append(ip)
    win.destroy()


text = Text(win, undo=True, height=1, width=40, padx=30, pady=1)
text.pack(expand=True, fill=BOTH)
Label(win, text=" enter ip address").pack(pady=20)
Button(win, text= "connect", command=partial(sethost, host)).pack()
win.mainloop()
##############################################################################################################
port = 55000
print('Waiting for connection response')
try:
    clientSocket.connect((host[0], port))
except:
    print("error in connecting")
    exit()
print("connected")


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
        data = data.decode().strip()

    data = id + data
    checksum = md5_checksum(data.encode('utf-8'))
    data = checksum+data
    return data.encode('utf-8')

def threewayhandshake(udpSocket, addr):
    data = "SYN"
    udpSocket.sendto(wrap(data, 0), addr)
    print(addr)
    time.sleep(1)

    data, addr = udpSocket.recvfrom(1024)
    checksum, id, data = unrwrap(data)
    print(data, id)
    if data[:7] != "SYN-ACK" or checksum == 1:
        exit_thread()

    filesize = data[7:]
    data = "ACK"
    udpSocket.sendto(wrap(data, 0), addr)
    return filesize

def unwrap_payload(payload):
    # get payload which is a list with the payload, IDs, and checksum
    # returns the payload itself and IDs that it got,
    checksum = payload[:32].decode('utf-8')
    msg = pickle.loads(payload[32:])
    data = bytes()
    for i in msg.values():
        data += i

    if checksum!=md5_checksum(data):
        checksum = 1
    return checksum, msg


def get_file(port, file):

    udpSocket = socket(AF_INET, SOCK_DGRAM)
    addr = (host[0], int(port))
    progress['value'] = 0
    filesize = threewayhandshake(udpSocket, addr)
    segments = []
    b = 0
    while b < int(filesize) + 1000:
        segments.append("")
        b += 1000
    segments.append("")
    amount_of_segments = len(segments)
    print("amount ", amount_of_segments)

    flag = True
    packet_loss = False
    acks = []

    while len(acks) <= amount_of_segments - 1:
        data, addr = udpSocket.recvfrom(65535)
        checksum, downloadedData = unwrap_payload(data)
        if random.randint(0,100)>7:  # delete for final version
            packet_loss = True       # delete for final version
        if checksum == 1 or packet_loss:    # delete "or packet loss" for final version
            packet_loss = False      # delete for final version
            print(" check sum is 1")
            if random.randint(0,10)==9: # delete for final version
                for i in downloadedData.keys():
                    data = "NACK" + i
                    udpSocket.sendto(wrap(data, 00), addr)
        else:
            for i in downloadedData.keys():
                if segments[int(i)] == "":
                    acks.append(int(i))
                    progress['value'] = (len(acks)/amount_of_segments)*100

                    if len(acks) >= amount_of_segments / 2 and flag:
                        flag = False
                        downloadwin = Tk()
                        downloadwin.geometry("200x100")
                        Label(downloadwin, text="downloaded 50%\ncontinue?").pack(pady=20)
                        Button(downloadwin, text="proceed", command=downloadwin.destroy).pack()
                        downloadwin.mainloop()
                segments[int(i)] = downloadedData.get(i)
                data = "ACK" + str(acks)
                udpSocket.sendto(wrap(data, 00), addr)

    data = "ACK-ALL"
    udpSocket.sendto(wrap(data, 00), addr)

    downloads_path = str(Path.home() / "Downloads")
    f = open(downloads_path + "/" + file, "wb+")
    for i in segments:
        if type(i) is bytes:
            f.write(i)
        elif type(i) is str:
            f.write(i.encode('utf-8'))


def listen(clientSocket, chat):
    connected = True
    while connected:
        res = clientSocket.recv(1024)
        if not res:
            connected = False
        decoded_res = res.decode('utf-8')
        if decoded_res == "connect_frudp":
            print("connect_frudp began")
            res = clientSocket.recv(1024)
            decoded_res = res.decode('utf-8')
            if decoded_res=="e":
                chat.config(state=NORMAL)
                chat.insert("end", "can not download file, try again later")
                chat.see("end")
                chat.config(state=DISABLED)
            else:
                port = decoded_res[:5]
                file = decoded_res[5:]
                start_new_thread(get_file, (port, file))
        else:
            chat.config(state=NORMAL)
            chat.insert("end", decoded_res)
            chat.see("end")
            chat.config(state=DISABLED)
            # print(res.decode('utf-8'))


def send(clientSocket, msg, text, chat):
    if msg is None:
        msg = text.get("0.0", "end - 1 chars")

        if msg[0:3] == "!pm" or msg[0:3] == "!PM" or msg[0:3] == "!Pm" or msg[0:3] == "!pM":
            clientSocket.send(str.encode("set_msg"))
            msg = msg[3:]
        elif msg[0:3] == "!df" or msg[0:3] == "!DF" or msg[0:3] == "!Df" or msg[0:3] == "!dF":
            clientSocket.send(str.encode("download_file"))
            msg = msg[3:]
        else:
            clientSocket.send(str.encode("set_msg_all"))

    elif msg == "nickname":
        msg = text.get("1.0", "end - 1 chars")
        if msg == "" or msg == " " or msg == "   ":
            msg = "anonymous"
        chat.config(state=NORMAL)
        chat.delete("1.0", "end")
        chat.config(state=DISABLED)
        button2.config(state=DISABLED)
        button0.config(state=NORMAL)
        button1.config(state=NORMAL)
        button3.config(state=NORMAL)

    clientSocket.send(str.encode(msg))
    text.delete("1.0", "end")


root = Tk()
root.geometry("500x300")
frame = Frame(root)
frame.pack()
chat = Text(frame, undo = True, height = 10, width = 60)
start_new_thread(listen, (clientSocket, chat))
leftframe = Frame(root)
leftframe.pack(side=LEFT)

rightframe = Frame(root)
rightframe.pack(side=RIGHT)

bottomframe = Frame(root)
bottomframe.pack(side=BOTTOM)

label = Label(frame, text="chat ver 0.4")
label.pack()

label = Label(frame, text="message: ")
label.pack()

text = Text(bottomframe, undo=True, height=1, width=40, padx=30, pady=1)
text.pack(expand=True, fill=BOTH)

chat.pack(fill=BOTH)
chat.insert("1.0", "enter your nickname first\n"
                   "for Private Messages use !pm NAME MSG\n"
                   "for Downloading Files use !df NAME_OF_FILE\n"
                   "")
chat.config(state=DISABLED)

progress = Progressbar(frame,orient = HORIZONTAL,length = 100, mode = 'determinate')
progress.pack(padx=1, pady=0)

button0 = Button(leftframe, state=DISABLED, text="available files", command=partial(send, clientSocket, "get_files", text, chat))
button0.pack(padx=3, pady=1)
button1 = Button(leftframe, state=DISABLED, text="online users", command=partial(send, clientSocket, "get_users", text, chat))
button1.pack(padx=0, pady=1)
button2 = Button(frame, text="enter nickname", command=partial(send, clientSocket, "nickname", text, chat))
button2.pack(padx=3, pady=0)
button3 = Button(rightframe, state=DISABLED, text="send", command=partial(send, clientSocket, None, text, chat))
button3.pack(padx=3, pady=3)

root.title("chat")
root.mainloop()

clientSocket.close()

