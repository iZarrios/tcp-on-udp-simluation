import socket
import pickle
from dotenv import load_dotenv
import os
import time
from tcp_packet import TCPPacket
from udp_tcp_socket import TCPOverUDPSocket


load_dotenv()
port = int(os.getenv("PORT", 8080))
address = os.getenv("ADDRESS", "localhost")
timeout = int(os.getenv("TIMEOUT", 1))

ADDR = (address, port)


# create a UDP socket
# udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

udp_socket = TCPOverUDPSocket()
udp_socket.settimeout(timeout)
udp_socket.connect(ADDR)

# choose whether to operate in normal mode or in lossy mode
# check if the user entered a valid mode
mode = ""
while (mode != "n" and mode != "l"):
    mode = input("Normal mode or lossy mode? (n/l): ")
udp_socket.set_lossy(mode == "l")

# choose whether to send a file or a message
choice = ""
while (choice != "f" and choice != "m"):
    choice = input("Send file or message? (f/m): ")
# sending a file from the client
if (choice == "f"):
    try:
        # open file
        file = open("./docs/alice.txt", "r")

        # read whole file
        message = file.read()

        udp_socket.send(message)

    except socket.timeout:
        print("Timeout")
        pass
# sending a message from the client
else:
    flag = True
    while flag:
        try:
            message = input("Enter message: ")
            udp_socket.send(message)
            if (message == "exit"):
                flag = False
        except socket.timeout:
            print("Timeout")
            pass

# close the socket
print("Closing client")
udp_socket.close()
print("Client closed")
