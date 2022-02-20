### initial construction idea:
Server: main thread that is in while True, listens for NEW connections.<br>
Every new connection gets two threads. <br>
1. one thread is in While True that receives new data to manage (either send or initiate another function in the server).
2. second thread is in While True that is ready to send data to the client.<br>when a new message is received it detects that and send the data.

The server will have many different function such as sending a broadcast msg, sending a PM, or downloading a file. 
<br> When a user asks for downloading a file it will be connection through a different socket for fast realiable UDP (or frdudp)

Client: connects to the server. When connected, two threads are initialized: 
1. for receiving input from the user, and send it to the server <br> 
(basically this thread sends data to the server)
<br>
2. for receiving data from the <b>server</b>. this thread listens <br>
to the server for when the server send a message to the client. 

### Documentation:
#### Server:
enter your ip address in addr.<br>
msgs list is a list of broadcast msgs.
pm is a dictinary, the key is the target of the pm, the value is a list of msgs for the target.
clients is a dictinary, the key is id and value is name.
<br>
<br>
at the end of the file there is a while True loop, this loop listens for NEW CONNECTIONS. for each new connection it creates a new thread for him and calls "newconnection" function. <br>
"newconnection" function get a nickname from the user, make sure its unique and then assign it with an id and sets up its PM lists in the dictinary mentioned above.
<br> it also calls a function that listen to the client and a function that send to the client. These two functions work in different threads.
<br> The function that sends to the client is rather simple: <br> 
"send_msg_to_client" works as long as the client is connected, and it always checks if there is a new broadcast msg or new pm msg that it didn't already send to the client. 
<br> The function that listens to the client is more complicated:
<br> it needs to differ between different commands that the clients asks the server to do. 
<br> so inside the main while connected loop, there is a long if-elif-else loop that - after receiving the data - checks what the users asked for and commit it. 
<br>

get users, get files are example of commands that the user can ask the server.
<br> 
<br>
#### Client:

at the top of the code there is a popup message that asks for an IP, it is a bit of an after thought because the instructions were not clear. <br>
after getting the IP from the user, it connects to the server. At the end of the code there are lines for the GUI which also works the inputs from the user. <br>
for listening to the server there is a new thread that runs in the background and adds things to the text box. 
<br> the send function is more complicated because it needs to differ between commands to the server and actual content the user wants to send. 

#### frUDP initial construction idea:
after the client sent a download request: 
the client opens a UDP socket and send SYN to server <br>
the server binds to a UDP socket and recv SYN and sends ACK <br>
the client receives ACK and sends ACK <br>
 **once the three-way handshake happend** 
<br> the server prepares the file for transfer: send size, bytes, amount of segments. 
each segme nt will be numbers and the client will ask for numbers that it didn't receive (select n repeat)