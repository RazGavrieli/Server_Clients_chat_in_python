import hashlib
import os
import pickle
import time
from _thread import *


def md5_checksum(data):
    """
    two hash functions for strings or bytes.
    keep in mind that other functions are responsible for comparing checksum
    :param data to calculate checksum:
    :return 32 bytes of unique hex number
    """
    if isinstance(data, (bytes, bytearray)):
        return hashlib.md5(data).hexdigest()

    elif isinstance(data, str):
        return hashlib.md5(data.encode()).hexdigest()

    else:
        raise ValueError('invalid input. input must be string or bytes')


def unwrap(data):
    """
    receives a wrapped data that has been wrapped by the function :wrap(data, id)
    this method is responsible for comparing checksum.
    :param data to unwrap:
    :return first 32 bytes are checksum, next 3 are id for identifying packet, the rest is the data itself:
    """
    if data[:32].decode('utf-8')!=md5_checksum(data[32:]):
        return 1, data[32:]
    data = data.decode('utf-8')
    return data[:32], data[32:35], data[35:]


def wrap(data, id):
    """
    this method receives data and id, calculate it's checksum and wraps all three
    into a single object.
    :param data to wrap:
    :param id of data for identifying a packet:
    :return single object containing the data, it's id and checksum:
    """
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


def wrap_payload(data):
    # data is a dictionary where key is id and value is bytes of file

    """
    this method receives data. This data is presented in a dictionary, where every key
    is an ID and the value is bytes of data. (the data is chunks of bytes read from the file)
    The method calculates the checksum for all the bytes in all the values.
    :param data as a dictionary that holds bytes:
    :return wrapped data and checksum:
    """
    msg = bytes()
    for i in data.values():
        msg += i
    checksum = md5_checksum(msg)
    msg = pickle.dumps(data)
    msg = bytes(checksum, 'utf-8')+msg
    return msg


def unwrap_payload(payload):
    # get payload which is a list with the payload, IDs, and checksum
    # returns the payload itself and IDs that it got,
    """
    This method receives wrapped data. It calculates the checksum for the data and compares it with the original checksum.
    :param payload:
    :return checksum and the data itself which is a dictionary.:
    """
    checksum = payload[:32].decode('utf-8')
    msg = pickle.loads(payload[32:])
    data = bytes()
    for i in msg.values():
        data += i

    if checksum!=md5_checksum(data):
        checksum = 1
    return checksum, msg


def serverside_threewayhandshake(udpSocket, connection, file):
    """
    initiate connection using frUDP.
    based on threewayhandshake as seen in TCP.
    the "SYN-ACK" message also contains file size
    :param udpSocket:
    :param connection:
    :param file:
    :return:
    """
    # receive SYN from client
    data, addr = udpSocket.recvfrom(1024)
    # unrwrap the data transfered over UDP, first 32 bytes are checksum
    checksum, id, data = unwrap(data)
    if data != "SYN" or checksum == 1:
        connection.sendall(str.encode(str("error")))
        exit_thread()

    data = "SYN-ACK" + str(os.path.getsize("files/" + file))
    udpSocket.sendto(wrap(data, 0), addr)

    data, addr = udpSocket.recvfrom(1024)
    checksum, id, data = unwrap(data)
    if data != "ACK" or checksum == 1:
        connection.sendall(str.encode(str("error")))
        exit_thread()

    return addr


def clientside_threewayhandshake(udpSocket, addr):
    """
    initiate connection using frUDP.
    based on threewayhandshake as seen in TCP.
    the "SYN-ACK" message also contains file size
    :param udpSocket:
    :param addr:
    :return:
    """
    data = "SYN"
    udpSocket.sendto(wrap(data, 0), addr)
    print(addr)
    time.sleep(1)

    data, addr = udpSocket.recvfrom(1024)
    checksum, id, data = unwrap(data)
    print(data, id)
    if data[:7] != "SYN-ACK" or checksum == 1:
        exit_thread()

    filesize = data[7:]
    data = "ACK"
    udpSocket.sendto(wrap(data, 0), addr)
    return filesize
