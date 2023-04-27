import socket
import random
import pickle
import threading
from tcp_packet import TCPPacket



DATA_DIVIDE_LENGTH = 1024
TCP_PACKET_SIZE = 32
DATA_LENGTH = DATA_DIVIDE_LENGTH
SENT_SIZE = TCP_PACKET_SIZE + DATA_LENGTH + 5000  # Pickled objects take a lot of space
LAST_CONNECTION = -1
FIRST = 0

MIN_SEQUENCE_NUMBER = 0
MAX_SEQUENCE_NUMBER = 2**32 - 1

def print_packet(packet):
    packet_type = packet.packet_type()
    if packet_type == "SYN":
        print("\033[43m" + str(packet) + "\033[0m")  # yellow background
    elif packet_type == "ACK":
        print("\033[44m" + str(packet) + "\033[0m")  # blue background
    elif packet_type == "SYN-ACK":
        print("\033[45m" + str(packet) + "\033[0m")  # magenta background
    elif packet_type == "FIN":
        print("\033[41m" + str(packet) + "\033[0m")  # red background
    elif packet_type == "FIN-ACK":
        print("\033[41;1m" + str(packet) + "\033[0m")  # red bold background
    else:
        print(str(packet))  # default color

class TCPOverUDPSocket:
    def __init__(self) -> None:
        self.status = 1  # 1 = open , 0 = closed
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address

        self.connections = {}
        self.connection_queue = []
        self.connection_lock = threading.Lock()
        self.queue_lock = threading.Lock()
        # each condition will have a dictionary of an address and it's corresponding packet.
        self.packets_received = {"SYN": {}, "ACK": {}, "SYN-ACK": {}, "DATA or FIN": {}, "FIN-ACK": {}}


        self.address = None  # Address of the peer
        self.port = None  # Port of the peer

    def __repr__(self):
        return "TCP()"

    def __str__(self):
        return f"Connection status: {self.status}\nSocket: {self.socket}\nAddress: {self.address}\nPort: {self.port} \
        \nConnections: {self.connections}\nConnection queue: {self.connection_queue}"

    def bind(self, address):
        self.address = address[0]
        self.port = address[1]
        self.socket.bind(address)

    def settimeout(self, timeout):
        self.socket.settimeout(timeout)

    def send(self, data):
        self.socket.sendto(data, (self.address, self.port))

        # wait ack
        # res = self.__wait_for_ack(handshake=False)
        # # if ack not received, resend packet
        #     self.socket.sendto(data, (self.address, self.port))
        #     res = self.__wait_for_ack(handshake=False)
        #             return
        # self.socket.close()
        # exit(1)



    def recvfrom(self, size):
        data, address = self.socket.recvfrom(size)
        pkt = TCPPacket.from_bytes(data)
        print_packet(pkt)
        return data, address

    def sendto(self, data, address):
        self.socket.sendto(data, address)

    def close(self):
        self.socket.close()

    def connect(self,address):
        # Send SYN
        self.address = address[0]
        self.port = address[1]
        self.__send_syn()
        # # Wait for SYN-ACK
        self.__wait_for_syn_ack()
        # # Send ACK
        self.__send_ack()
        # # Connection established
        self.status = 0


    def __send_syn(self):
        global cnt
        syn = TCPPacket()
        syn.data = "SYN"
        syn.set_flags(syn=True)
        self.sendto(syn.to_bytes(syn), (self.address, self.port))

    def __send_ack(self):
        ack = TCPPacket()
        ack.data = "ACK"
        ack.set_flags(ack=True)
        self.sendto(ack.to_bytes(ack), (self.address, self.port))

    def __wait_for_syn_ack(self):
        while True:
            try:
                data, address = self.recvfrom(SENT_SIZE)
                pkt = TCPPacket.from_bytes(data)
                print_packet(pkt)
                if pkt.packet_type() == "SYN-ACK":
                    self.port = address[1]
                    return
            except socket.timeout:
                print("Timeout waiting for SYN-ACK")
                exit(1)
    def listen(self):
        pass

    def accept(self):
        # Wait for SYN
        self.__wait_for_syn()
        # Send SYN-ACK
        self.__send_syn_ack()
        # Wait for ACK
        self.__wait_for_ack()

        # Connection established
        self.status = 0
        return self.address, self.port

    def __wait_for_syn(self):
        while True:
            try:
                data, address = self.recvfrom(SENT_SIZE)
                pkt = TCPPacket.from_bytes(data)
                if pkt.packet_type() == "SYN":
                    print_packet(pkt)
                    self.port = address[1]
                    return
            except socket.timeout:
                print("Timeout waiting for SYN")

    def __send_syn_ack(self):
        syn_ack = TCPPacket()
        syn_ack.data = "SYN-ACK"
        syn_ack.set_flags(syn=True, ack=True)
        self.sendto(syn_ack.to_bytes(syn_ack), (self.address, self.port))

    def __wait_for_ack(self,handshake=True):
        while True:
            try:
                data, _= self.recvfrom(SENT_SIZE)
                pkt = TCPPacket.from_bytes(data)
                print_packet(pkt)
                if pkt.packet_type() == "ACK":
                    return "YES"
            except socket.timeout:
                if not handshake:
                    return "NO"
                print("Timeout waiting for ACK")
                exit(1)
