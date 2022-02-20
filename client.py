import threading
from socket import *
from _thread import *
from tkinter import *
from functools import partial
import hashlib
import math
from pathlib import Path
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
    md5h = hashlib.md5()
    md5h.update(data)
    return md5h.hexdigest()

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

    data, addr = udpSocket.recvfrom(1024)
    checksum, id, data = unrwrap(data)
    print(data, id)
    if data[:7] != "SYN-ACK" or checksum == 1:
        exit_thread()

    filesize = data[7:]
    data = "ACK"
    udpSocket.sendto(wrap(data, 0), addr)
    return filesize


def get_file(port, file):
    udpSocket = socket(AF_INET, SOCK_DGRAM)
    addr = ("127.0.0.1", int(port))

    filesize = threewayhandshake(udpSocket, addr)
    segments = []
    b=0
    while b<int(filesize)+1000:
        segments.append("")
        b+=1000
    segments.append("")
    amount_of_segments = len(segments)
    print("amount ", amount_of_segments)

    flag = True
    acks = 0
    while acks!=amount_of_segments-1:
        data, addr = udpSocket.recvfrom(65535)
        checksum, id, downloadedData = unrwrap(data)
        if checksum==1:
            data = "NACK"+id
        else:
            if segments[int(id)] == "":
                acks+=1
                if acks>=amount_of_segments/2 and flag:
                    flag = False
                    downloadwin = Tk()
                    downloadwin.geometry("200x100")
                    Label(downloadwin, text="downloaded 50%").pack(pady=20)
                    Button(downloadwin, text="proceed", command=downloadwin.destroy).pack()
                    downloadwin.mainloop()
            data = "ACK"+id
            segments[int(id)] = downloadedData

        udpSocket.sendto(wrap(data,00), addr)





    data = "ACK-ALL"
    udpSocket.sendto(wrap(data, 00), addr)
    downloads_path = str(Path.home() / "Downloads")
    f = open(downloads_path+"/"+file,"wb+")
    for i in segments:
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
chat = Text(frame, undo = True, height = 10, width = 70)
start_new_thread(listen, (clientSocket, chat))
leftframe = Frame(root)
leftframe.pack(side=LEFT)

rightframe = Frame(root)
rightframe.pack(side=RIGHT)

bottomframe = Frame(root)
bottomframe.pack(side=BOTTOM)

label = Label(frame, text="chat ver 0.3")
label.pack()

label = Label(frame, text="message: ")
label.pack()

text = Text(bottomframe, undo=True, height=1, width=40, padx=30, pady=1)
text.pack(expand=True, fill=BOTH)

chat.pack(fill=BOTH)
chat.insert("1.0", "enter your nickname first\n"
                   "for Private Messages use !pm NAME MSG\n")
chat.config(state=DISABLED)

button0 = Button(leftframe, state=DISABLED, text="available files", command=partial(send, clientSocket, "get_files", text, chat))
button0.pack(padx=3, pady=3)
button1 = Button(leftframe, state=DISABLED, text="online users", command=partial(send, clientSocket, "get_users", text, chat))
button1.pack(padx=3, pady=3)
button2 = Button(frame, text="enter nickname", command=partial(send, clientSocket, "nickname", text, chat))
button2.pack(padx=3, pady=3)
button3 = Button(rightframe, state=DISABLED, text="send", command=partial(send, clientSocket, None, text, chat))
button3.pack(padx=3, pady=3)

root.title("chat")
root.mainloop()

clientSocket.close()

