import threading
from socket import *
from _thread import *
from tkinter import *
from functools import partial

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
print("connected")
# res = clientSocket.recv(1024)


def listen(clientSocket, chat):
    connected = True
    while connected:
        res = clientSocket.recv(1024)
        if not res:
            connected = False
        chat.config(state=NORMAL)
        chat.insert("end", res.decode('utf-8'))
        chat.see("end")
        chat.config(state=DISABLED)
        print(res.decode('utf-8'))


def send(clientSocket, msg, text, chat):
    if msg is None:
        msg = text.get("0.0", "end - 1 chars")

        if msg[0:3] == "!pm" or msg[0:3] == "!PM" or msg[0:3] == "!Pm" or msg[0:3] == "!pM":
            clientSocket.send(str.encode("set_msg"))
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

label = Label(frame, text="chat ver 0.2")
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

