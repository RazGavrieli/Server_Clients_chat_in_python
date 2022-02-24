![image](https://user-images.githubusercontent.com/90526270/155513141-2ef6bf56-bd43-44cb-ac62-fa07542e91ba.png)
## Introduction
This project has been made for Computer Networking Course at Ariel University.<br>
It is a messaging app between serval clients, through a single server. <br>
The clients can also download files from the server, using a UDP connection with reliabilty layers ontop of it.<br>

### How to run: <<<<<<<<<<<<<<<<<<<<<<<< READ THIS <<<<<<<<<<<<<<<<<<<<<<<<<<<<
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
For a linux based client side you have to install the libraries manually, install tkinter. 

## Implementation - 

#### State Diagrams - 
First we will acknowlage that the simple messages are sent using TCP. Which means the state diagram is fixed, and as followed:<br>
![image](https://user-images.githubusercontent.com/90526270/155519343-42c0fa75-ad0b-4bb4-9710-a574eaec7025.png)


My implementation of CC is in frUDP is more simple, it is also based on unique acks for each segment of the file. 
When the server receives nack from the client, it lowers the amount of bytes sent at each packet. 
When the server does not receive and ack nor nack, it lowers the amount of bytes sent at each packet. 
This way, the download stays stable even though the connection is not. This way we over come packet losses and latency problems. 


![image](https://user-images.githubusercontent.com/90526270/155531628-13783e82-8f2e-4a42-8800-2216090ef605.png)

 When the server is initialized, it always listens to a new client. 

 
![image](https://user-images.githubusercontent.com/90526270/155531431-6489a8ac-5344-4c1b-953e-3af9a35b2374.png)



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
The managment of the two kinds of headers is easily observered in drUDP.py at lines 25-100.  It is managed by the 4 functions: 
wrap() and unwrap() are for string data and wrap_payload() and unwrap_payload() are for data in bytes saved in a dictionary. 


#### Establishing connection - 
Inspired by TCP, I implemented three-way-handshake into frUDP. 
It works the same way as TCP's does, the only difference is for optimization. Information such as 'filesize' is being transffered from the server to the client using the "SYN-ACK" message. 
<br> in frUDP.py there are two functions that are responsible for establshing frUDP connection: serverside_threewayhandshake() and clientside_threewayhandshake().
At first, the client sends the server a "SYN" message and waits for reply. Once the server receives the message it sends a "SYN-ACK" message, that is followed by 'filesize' which is the amount of bytes the server is intending to send to the client. The client receives the message and sends a final "ACK" message before the file tranfer initializes. <br> 
![image](https://user-images.githubusercontent.com/90526270/155533109-8dfe608f-b457-4110-b3e1-174fbc7f2a79.png)



#### initial construction idea:
For the server there is a main thread that runs in a while true loop, and listens for new connections. <br>
each connection receives 2 threads; one for listening and one for sending. <br>
On the client it is simillar, once connection has been established 2 threads are being ran; one for lisetning and one for sending.<br>
Once the client asks for a file, a new thread is initialized for the function "get_file" so the TCP connection is still running in the background. <br>
On the server side, once a client asks for a file, two threads are being initialized, one for sending the file itself and one for listening for acks\nacks\ack-all. <br>. 



## Documentation of expermients:
On the client side in lines 75-85 I've implemented "fake packet loss simulation", where we can create packet loss and send nacks messages (or even not send nacks or acks for a specific packet). <br>
Using this method, we could observe our changes in download speeds according to packet losses. (Congestion Control). <br>
<b> one of the most difficult things in this project was figuring out the values for changes in download speed at each nack or latency recognition </b> <br>
The following image shows the part of the code where you can create packet loss, send nacks or not send anything back to the server (as if the packet didn't arrive) <br>
![image](https://user-images.githubusercontent.com/90526270/155533778-d28caf0a-8e93-4148-80a2-9d1dd84b5a6a.png)

<br>


#### The part of the code that controls the transfer speeds (in server.py lines)
keep in mind that values[1] represents the amount of bytes (in thousands) that will be sent at a time. 
```
        if data[:4] == "NACK":
            if values[1]>8:
                values[1]-=3
        ...
        
        ...
        elif data[:3] == "ACK":
            list = eval(data[3:])
            if values[1]<60:       
                values[1]+=1 
```

The raw data for the following charts is in google sheets: <br> 
https://docs.google.com/spreadsheets/d/1wk7WyMW9k_cAbM6wEbKLBgx3a4vXbHEUQjmjdHLtLuA/edit?usp=sharing
#### Example of 0% packet loss file transfer speeds
![image](https://user-images.githubusercontent.com/90526270/155535584-70d4f694-d360-4afc-bff1-0f844486cbf8.png)

#### Example of 5% packet loss file transfer speeds 
![image](https://user-images.githubusercontent.com/90526270/155524271-144770e3-3aea-419c-8cb2-72a29c45816d.png)

#### Example of 10% packet loss file transfer speeds
![image](https://user-images.githubusercontent.com/90526270/155536343-f9a7fcb2-97ce-43a0-ba70-35c0e770b0b0.png)


#### wireshark snapshot of a file transfer, the pcap file is included for more information
![image](https://user-images.githubusercontent.com/90526270/155538938-c5c3a24a-c310-421d-9382-e65a98964b5e.png)


#### Example of 10% packet loss file transfer speeds, with a pause after 50% (initiates slow-start), the wireshark snapshot included is of this transfer
![image](https://user-images.githubusercontent.com/90526270/155538668-6ed8bbb0-2029-46c4-bbfe-9c8bbed76856.png)

