import socket
import pickle
from dotenv import load_dotenv
import os
import time
from tcp_packet import TCPPacket
from udp_tcp_socket import TCPOverUDPSocket




load_dotenv()
port = int(os.getenv("PORT",8080))
address= os.getenv("ADDRESS","localhost")
timeout = int(os.getenv("TIMEOUT",1))

ADDR=(address,port)



# create a UDP socket
# udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

udp_socket = TCPOverUDPSocket()
udp_socket.settimeout(timeout)
udp_socket.connect(ADDR)

flag = True
while flag:
    try:
        flag = False

        pkt = TCPPacket()
        # send a message to the server
        message = "hahahahhahahahahaa"
        print('Sending message:', message)

        pkt.data = message
        pkt_pk= pickle.dumps(pkt)
        # udp_socket.sendto(pkt_pk,ADDR)
        udp_socket.send(pkt_pk)

        # receive a response from the server
        # data, server_address = udp_socket.recvfrom(1024)
        # print('Received message:', data.decode())
        # print('From server:', server_address)
    except socket.timeout:
        pass

# close the socket
udp_socket.close()
print("Client closed")
