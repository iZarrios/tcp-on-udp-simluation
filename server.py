import socket
from dotenv import load_dotenv
import os
import pickle
from tcp_packet import TCPPacket

load_dotenv()
port = int(os.getenv("PORT",8080))
address= os.getenv("ADDRESS","localhost")
timeout = int(os.getenv("TIMEOUT",1))


ADDR=(address,port)

# create a UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind the socket to a specific address and port
udp_socket.bind(ADDR)
udp_socket.settimeout(timeout)

print('Server is listening on', ADDR)

while True:
    try:
        # receive a message and the client address from the socket
        data, client_address = udp_socket.recvfrom(1024)

        pkt = TCPPacket.from_bytes(data)
        print(pkt.seq,pkt.packet_type(),":",pkt.data)


        
        # print('Received message:', data)
        print('From client:', client_address)

        # send a response to the client
        # response = 'Hello, client!'
        # udp_socket.sendto(response.encode(), client_address)
        # print('Sent response:', response)
    except socket.timeout:
        # print('Timeout')
        pass
