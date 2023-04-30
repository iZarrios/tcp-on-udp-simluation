import socket
from dotenv import load_dotenv
import os
import pickle as pkl

# from tcp_packet import TCPPacket
from udp_tcp_socket import TCPOverUDPSocket, print_packet

load_dotenv()
port = int(os.getenv("PORT",8080))
address= os.getenv("ADDRESS","localhost")
timeout = int(os.getenv("TIMEOUT",1))


ADDR=(address,port)

# create a UDP socket
# udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

udp_socket = TCPOverUDPSocket()

# bind the socket to a specific address and port
udp_socket.bind(ADDR)
udp_socket.settimeout(timeout)

udp_socket.listen()

print('Server is listening on', ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    while True:
        if conn.status == 1:
            print("Connection closed")
            break
        # recieve message from client
        try:
            data = conn.rcv()
            if not data:
                continue
            # packet_type = packet.packet_type()
            print_packet(data)
        except socket.timeout:
            print("Timeout")
            conn.close()
            break

while True:
    addr, _= udp_socket.accept()
    handle_client(udp_socket, addr)
