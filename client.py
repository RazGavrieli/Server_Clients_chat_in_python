import random       # for packet loss simulation
from socket import *
from tkinter import *
from functools import partial
from pathlib import Path
from tkinter.ttk import Progressbar
from frUDP import *

clientSocket = socket(AF_INET, SOCK_STREAM)
##############################################################################################################
win = Tk()
win.geometry("200x100")
host = []


def sethost(host):
    """
    set the host ip the client wants to connect to
    """
    ip = text.get("1.0", "end - 1 chars")
    if ip == "":
        host.append("127.0.0.1")
    else:
        host.append(ip)
    win.destroy()


text = Text(win, undo=True, height=1, width=40, padx=30, pady=1)
text.pack(expand=True, fill=BOTH)
Label(win, text=" enter ip address").pack(pady=20)
Button(win, text="connect", command=partial(sethost, host)).pack()
win.mainloop()
##############################################################################################################
port = 55000
print('Waiting for connection response')
try:
    clientSocket.connect((host[0], port))
except:
    win = Tk()
    win.geometry("200x100")
    Label(win, text="could not connect").pack(pady=20)
    win.mainloop()
    time.sleep(1)
    exit()


def get_file(port, file):
    """
    this method is called when the client wants to download a file from the server,
    using the frUDP protocol.
    :param port:
    :param file:
    :return:
    """
    udpSocket = socket(AF_INET, SOCK_DGRAM)
    addr = (host[0], int(port))
    progress['value'] = 0
    filesize = clientside_threewayhandshake(udpSocket, addr)
    segments = []
    b = 0
    while b < int(filesize) + 1000:
        segments.append("")
        b += 1000
    segments.append("")
    amount_of_segments = len(segments)

    flag = True
    packet_loss = False
    acks = []

    # begin receiving the file from the server
    while len(acks) <= amount_of_segments - 1:
        data, addr = udpSocket.recvfrom(65535)
        checksum, downloadedData = unwrap_payload(data)
        #if random.randint(0,100)>89:               #\** packet loss simulation **\
        #    packet_loss = True                     #\** packet loss simulation **\
        if checksum == 1 or packet_loss:            # "or packet_loss" is for packet loss simulation
        #    packet_loss = False                    #\** packet loss simulation **\
        #    if random.randint(0,10)!=9:            #\** packet loss simulation **\
            for i in downloadedData.keys():
                data = "NACK" + i
                udpSocket.sendto(wrap(data, 00), addr)
        else:
            for i in downloadedData.keys():
                if segments[int(i)] == "":
                    acks.append(int(i))
                    progress['value'] = (len(acks) / amount_of_segments) * 100

                    if len(acks) >= amount_of_segments / 2 and flag:
                        # stop at 50%
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
    """
    listens for new messages from the server, process it and show the client
    the correct output
    :param clientSocket:
    :param chat:
    """
    connected = True
    while connected:
        res = clientSocket.recv(1024)
        if not res:
            connected = False
        decoded_res = res.decode('utf-8')
        if decoded_res == "connect_frudp":
            res = clientSocket.recv(1024)
            decoded_res = res.decode('utf-8')
            if decoded_res == "e":
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


def send(clientSocket, msg, text, chat):
    """
    Once an input is received (usually from the GUI),
    process it and send to the server the correct message.
    :param clientSocket:
    :param msg:
    :param text:
    :param chat:
    """
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


"""
GUI and input management
"""
root = Tk()
root.geometry("500x300")
frame = Frame(root)
frame.pack()
chat = Text(frame, undo=True, height=10, width=60)
start_new_thread(listen, (clientSocket, chat))
leftframe = Frame(root)
leftframe.pack(side=LEFT)

rightframe = Frame(root)
rightframe.pack(side=RIGHT)

bottomframe = Frame(root)
bottomframe.pack(side=BOTTOM)

label = Label(frame, text="chat ver 0.44")
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

progress = Progressbar(frame, orient=HORIZONTAL, length=100, mode='determinate')
progress.pack(padx=1, pady=0)

button0 = Button(leftframe, state=DISABLED, text="available files",
                 command=partial(send, clientSocket, "get_files", text, chat))
button0.pack(padx=3, pady=1)
button1 = Button(leftframe, state=DISABLED, text="online users",
                 command=partial(send, clientSocket, "get_users", text, chat))
button1.pack(padx=0, pady=1)
button2 = Button(frame, text="enter nickname", command=partial(send, clientSocket, "nickname", text, chat))
button2.pack(padx=3, pady=0)
button3 = Button(rightframe, state=DISABLED, text="send", command=partial(send, clientSocket, None, text, chat))
button3.pack(padx=3, pady=1)

root.title("chat")
root.mainloop()

clientSocket.close()
