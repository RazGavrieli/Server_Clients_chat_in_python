![image](https://user-images.githubusercontent.com/90526270/155513141-2ef6bf56-bd43-44cb-ac62-fa07542e91ba.png)
## Introduction
This project has been made for Computer Networking Course at Ariel University.<br>
It is a messaging app between serval clients, through a single server. <br>
The clients can also download files from the server, using a UDP connection with reliabilty layers ontop of it.<br>

### How to run: <<<< READ THIS <<<<
#### Server Side - 
Download server.py and frUDP.py to the same folder on your computer. <br>
Create a new folder within it, called "files".<br>
run server.py through CMD or through an IDE for python. <br>
An IP will be written in the terminal, copy it and send it to your clients. <br>
Make sure ports 55000-55015 are open and ready to be used. <br>
![image](https://user-images.githubusercontent.com/90526270/155517865-ae917fc9-d18e-405a-9141-d5b8fd9b9fc3.png)

#### Client Side - 
Download client.py and frUDP.py to the same folder, run client.py through CMD or an IDE for python. <br>
A small window will pop-up, insert a working IP of a server you want to connect to and wait for the connection to be established. <br>
![image](https://user-images.githubusercontent.com/90526270/155518110-c58d34ad-720e-4886-a251-d9bd5e22b699.png)
<br>

## Implementation - 
(this is introduction of implementation, read more at the wiki page)
#### State Diagrams - 
First we will acknowlage that the simple messages are sent using TCP. Which means the state diagram is fixed, and as followed:<br>
![image](https://user-images.githubusercontent.com/90526270/155519343-42c0fa75-ad0b-4bb4-9710-a574eaec7025.png)


My implementation of CC is in frUDP is more simple, it is also based on unique acks for each segment of the file. 
Read more at the wiki page: 

#### Headers - 
As stated in the diagrams section, the messages are sent using TCP so the header is fixed and as follows: <br>
![image](https://user-images.githubusercontent.com/90526270/155520182-3d8c1e13-bb27-4f7c-8176-489ccb73c0e3.png)

The implementation of headers in frUDP includes checksum, segment ID and data in bytes loaded into pickle (or json..) <br>
FOR PAYLOAD (DATA IN BYTES)
| 32 bytes | rest of bytes | 
| ----------- | ---- | 
| checksum    |  chuncks of 1000 bytes of data with unique segment ID for each chunk |  

FOR MESSAGE DATA (DATA IN STRING)
| 32 bytes | 3 bytes | rest of bytes |
| ----------- | ---- | ------------------------- | 
| checksum    |  segment ID | data in bytes of the string |  

<br>
You can read more about this implementation in the wiki page.


#### Establishing connection - 
Inspired by TCP, I implemented three-way-handshake into frUDP. 
It works the same way as TCP's does, the only difference is for optimization. Information such as 'filesize' is being transffered from the server to the client using the "SYN-ACK" message. 

#### initial construction idea:
For the server there is a main thread that runs in a while true loop, and listens for new connections. <br>
each connection receives 2 threads; one for listening and one for sending. <br>
On the client it is simillar, once connection has been established 2 threads are being ran; one for lisetning and one for sending.<br>
Once the client asks for a file, a new thread is initialized for the function "get_file" so the TCP connection is still running in the background. <br>
On the server side, once a client asks for a file, two threads are being initialized, one for sending the file itself and one for listening for acks\nacks\ack-all. (read more at the wiki page) <br>. 

## Documentation of expermients:
On the client side in lines 75-85 I've implemented "fake packet loss simulation", where we can create packet loss and send nacks messages (or even not send nacks or acks for a specific packet). <br>
Using this method, we could observe our changes in download speeds according to packet losses. (Congestion Control). <br>
<b> one of the most difficult things in this project was figuring out the values for changes in download speed at each nack or latency recognition </b>
<br>
#### Example of 5% packet loss file transfer speeds 
please read more about CC at the wiki page <br>
![image](https://user-images.githubusercontent.com/90526270/155524271-144770e3-3aea-419c-8cb2-72a29c45816d.png)
