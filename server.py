import socket
from dotenv import load_dotenv
import threading
import os
from tcp_packet import TCPPacket
from udp_tcp_socket import TCPOverUDPSocket, pickle

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
    connected = True
    while connected:
        # recieve message from client
        try:
            data = conn.recvfrom(1024)
            if not data:
                break
            print(pickle.loads(data[0]))
        except socket.timeout:
            print("Timeout")

while True:
    addr, _= udp_socket.accept()
    thread = threading.Thread(target=handle_client, args=(udp_socket, addr))
    thread.start()
    while udp_socket.status == 0:
        pass
