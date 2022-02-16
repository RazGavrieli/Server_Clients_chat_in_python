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
