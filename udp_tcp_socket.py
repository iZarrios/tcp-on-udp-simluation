import socket
import random
import time
import pickle as pkl
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
        self.socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address


        self.address = None  # Address of the peer
        self.port = None  # Port of the peer

        self.lossy = False

    def __repr__(self):
        return "TCPOverUDPSocket()"

    def __str__(self):
        return f"Connection status: {self.status}\nSocket: {self.socket}\nAddress: {self.address}\nPort: {self.port}"

    # set lossy
    def set_lossy(self, lossy):
        self.lossy = lossy

    def bind(self, address):
        self.address = address[0]
        self.port = address[1]
        self.socket.bind(address)

    def settimeout(self, timeout):
        self.socket.settimeout(timeout)

    # generate random variable 0 or 1 or 2
    def __generate_random(self):
        # Generate a random seed from the current system time
        current_time = time.time()
        # Set the seed
        random.seed(int(current_time*1000))
        # Generate a random number between 0 and 1
        return random.randint(0, 2)

    def send(self, data):
        '''
        Sends a sequence of data over the network by dividing it into packets and
        sending each packet separately.

        Args:
            data: The data to be sent.

        Returns:
            None
        '''
        # divide data into packets
        segments = self.__divide_data(data)
        # send packets
        for segment in segments:
            pkt = TCPPacket()
            pkt.set_data(segment)
            self.send_pkt(pkt)


    def __divide_data(self, data):
        """
        Divide a given data sequence into smaller packets of a fixed length.

        Args:
            data: A sequence of data to be divided into smaller packets.

        Returns:
            A list of segments, where each segment is a packet of length DATA_DIVIDE_LENGTH
            (except possibly the last one, which may be shorter).

        """
        segments = []
        # divide data into packets
        for i in range(0, len(data), DATA_DIVIDE_LENGTH):
            segments.append(data[i:i + DATA_DIVIDE_LENGTH])
        return segments

    def send_pkt(self, pkt):
        return self.__send_normal_pkt(pkt) if not self.lossy else self.__send_lossy_pkt(pkt)

    def __send_normal_pkt(self, pkt):
        self.socket.sendto(pkt.to_bytes(pkt), (self.address, self.port))
        # wait ack
        _ = self.__wait_for_ack_data(pkt)
        print("Ack received")

    def __send_lossy_pkt(self, pkt):
        # generate random number
        if self.__generate_random() == 0:
            self.socket.sendto(pkt.to_bytes(pkt), (self.address, self.port))
        elif self.__generate_random() == 1:
            print("Packet lost")
        else:  # corrupt packet
            print("Packet corrupted")
            pkt.set_checksum(0)
            self.socket.sendto(pkt.to_bytes(pkt), (self.address, self.port))
        # wait ack
        return_val = self.__wait_for_ack_data(pkt)
        if (return_val != None):
            print("Ack received")

    def __wait_for_ack_data(self, original_pkt):
        cnt = 0
        while True:
            try:
                data, address = self.recvfrom(SENT_SIZE)
                pkt = TCPPacket.from_bytes(data)
                if pkt.packet_type() == "ACK":
                    self.port = address[1]
                    return data
            except socket.timeout:
                print("Timeout waiting for DATA")
                original_pkt.set_data(original_pkt.data)
                self.send_pkt(original_pkt)
                return None

     # Client side?

    def rcv(self):
        # wait data
        res = None
        while res == None:
            res = self.__wait_for_data()
        pkt = TCPPacket.from_bytes(res)

        # if data received, send ack

        self.__send_ack()
        # print_packet(TCPPacket.from_bytes(res))
        return pkt

    def __wait_for_data(self):
        cnt = 0
        while True:
            try:
                data, address = self.recvfrom(SENT_SIZE)
                pkt = TCPPacket.from_bytes(data)
                if pkt.packet_type() == "DATA" and pkt.verify_checksum():
                    self.port = address[1]
                    return data
                # if pkt of type FIN send find_ack
                elif pkt.packet_type() == "FIN":
                    self.port = address[1]
                    self.__send_fin_ack()
                    return data

            except socket.timeout:
                print("Timeout waiting for DATA")

    def __send_fin_ack(self):
        pkt = TCPPacket()
        pkt.set_flags(ack=True, fin=True)

        self.send_pkt(pkt)
        self.status = 1

    def recvfrom(self, size):
        data, address = self.socket.recvfrom(size)
        # pkt = TCPPacket.from_bytes(data)
        return data, address

    def sendto(self, data, address):
        self.socket.sendto(data, address)

    def close(self):
        # send FIN
        self.__send_fin()
        # wait for FIN-ACK
        self.__wait_for_fin_ack()
        # send ACK
        self.__send_ack()
        self.status = 1
        self.socket.close()

    def __wait_for_fin_ack(self):
        cnt = 0
        while True:
            try:
                data, address = self.recvfrom(SENT_SIZE)
                pkt = TCPPacket.from_bytes(data)
                if pkt.packet_type() == "FIN-ACK":
                    self.port = address[1]
                    return data
            except socket.timeout:
                cnt += 1
                print("Timeout waiting for FIN-ACK")
                if cnt == 3:
                    print("Connection closed cuz no FIN-ACK")
                    exit(1)

    def __send_fin(self):
        fin = TCPPacket()
        fin.data = "FIN"
        fin.set_flags(fin=True)
        print("Sending FIN")
        self.sendto(fin.to_bytes(fin), (self.address, self.port))

    def connect(self, address):
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
                time.sleep(1)

    def __send_syn_ack(self):
        syn_ack = TCPPacket()
        syn_ack.data = "SYN-ACK"
        syn_ack.set_flags(syn=True, ack=True)
        self.sendto(syn_ack.to_bytes(syn_ack), (self.address, self.port))

    def __wait_for_ack(self):
        while True:
            try:
                data, _ = self.recvfrom(SENT_SIZE)
                pkt = TCPPacket.from_bytes(data)
                print_packet(pkt)
                if pkt.packet_type() == "ACK":
                    return "YES"
            except socket.timeout:
                print("Timeout waiting for ACK")
                exit(1)
