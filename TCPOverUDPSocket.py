import socket
import random
import pickle


DATA_DIVIDE_LENGTH = 1024
TCP_PACKET_SIZE = 32
DATA_LENGTH = DATA_DIVIDE_LENGTH
SENT_SIZE = TCP_PACKET_SIZE + DATA_LENGTH + 5000  # Pickled objects take a lot of space
LAST_CONNECTION = -1
FIRST = 0

MIN_SEQUENCE_NUMBER = 0
MAX_SEQUENCE_NUMBER = 2**32 - 1

class TCPPacket:
    SMALLEST_STARTING_SEQ = 0
    HIGHEST_STARTING_SEQ = 4294967295

    def __init__(self):
        self.seq = TCPPacket.gen_starting_seq_num() 
        self.ack = 0
        self.data_offset = 0
        self.reserved_field = 0

        # flags 
        self.flag_ns = 0  # 1bit
        self.flag_cwr = 0  # 1bit
        self.flag_ece = 0  # 1bit
        self.flag_urg = 0  # 1bit
        self.flag_ack = 0  # 1bit
        self.flag_psh = 0  # 1bit
        self.flag_rst = 0  # 1bit
        self.flag_syn = 0  # 1bit
        self.flag_fin = 0  # 1bit


        # window size
        self.window_size = 0  # 16bit
        # checksum
        self.checksum = 0  # 16bit
        # urgent pointer
        self.urgent_pointer = 0  # 16bit
        # options
        self.options = 0  # 0-320bits, divisible by 32
        # padding - TCP packet must be on a 32bit boundary this ensures that it is the padding is filled with 0's
        self.padding = 0
        self.data = ""

    def __repr__(self):
        return "TCPpacket()"

    def __str__(self):
        return f"SEQ Number: {self.seq}, ACK Number: {self.ack}, ACK: {self.flag_ack}, SYN: {self.flag_syn}, FIN: {self.flag_fin}, TYPE: {self.packet_type()}, DATA: {self.data}"

    def __cmp__(self, other):
        # Fix 
        if self.seq == other.seq:
            return 0
        return 1

    def packet_type(self):
        packet_type = ""
        if self.flag_syn == 1 and self.flag_ack == 1:
            packet_type = "SYN-ACK"
        elif self.flag_ack == 1 and self.flag_fin == 1:
            packet_type = "FIN-ACK"
        elif self.flag_syn == 1:
            packet_type = "SYN"
        elif self.flag_ack == 1:
            packet_type = "ACK"
        elif self.flag_fin == 1:
            packet_type = "FIN"
        elif self.data != "":
            packet_type = "DATA"
        return packet_type

    def set_flags(self, ack=False, syn=False, fin=False):
        if ack:
            self.flag_ack = 1
        else:
            self.flag_ack = 0
        if syn:
            self.flag_syn = 1
        else:
            self.flag_syn = 0
        if fin:
            self.flag_fin = 1
        else:
            self.flag_fin = 0

    @staticmethod
    def gen_starting_seq_num():
        return random.randint(TCPPacket.SMALLEST_STARTING_SEQ, TCPPacket.HIGHEST_STARTING_SEQ)


class TCPOverUDPSocket:
    def __init__(self,timeout=5) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address
        self.socket.settimeout(timeout)  # Timeout for receiving data

        self.connection = None

        self.seq_num = random.randint(0, MAX_SEQUENCE_NUMBER)  # Initial sequence number
        self.ack_num = 0  # Initial ack number

        self.buffer = []  # Buffer for received packets
        self.last_packet_received = None  # Last packet received from the peer
        self.last_packet_sent = None  # Last packet sent to the peer
        self.last_packet_acked = None  # Last packet acknowledged by the peer
        self.send_queue = []  # Queue of packets to send
        self.recv_queue = []  # Queue of received data

        self.address = None  # Address of the peer
        self.port = None  # Port of the peer

    def bind(self, address,port):
        self.socket.bind((address,port))

    def listen(self, max_connections=1):
        self.socket.listen(max_connections)

    def send_syn(self):
        packet = TCPPacket()
        packet.set_flags(syn=True)
        packet.seq = self.seq_num
        packet.ack = self.ack_num
        self.last_packet_sent = packet
        self.send_queue.append(packet)
        self.seq_num += 1

    def recv_syn_ack(self):
        packet = self.recv_packet()
        if packet.flag_syn == 1 and packet.flag_ack == 1:
            self.last_packet_received = packet
            self.ack_num = packet.seq + 1
            self.seq_num += 1
        else:
            raise Exception("Received packet is not a SYN-ACK packet")
    def recv_packet(self):
        try:
            # data, address = self.socket.recvfrom(DATA_LENGTH)
            data, _= self.socket.recvfrom(DATA_LENGTH)
            packet = TCPPacket()
            packet = pickle.loads(data)
            self.last_packet_received = packet
            return packet
        except socket.timeout:
            raise Exception("Timeout")

    def send_ack(self):
        packet = TCPPacket()
        packet.set_flags(ack=True)
        packet.seq = self.seq_num
        packet.ack = self.ack_num
        self.last_packet_sent = packet
        self.send_queue.append(packet)
        self.seq_num += 1

    def connect(self, address, port):
        self.address = address
        self.port = port
        self.seq_num = random.randint(0, MAX_SEQUENCE_NUMBER)
        self.ack_num = 0
        self.send_syn()
        self.recv_syn_ack()
        self.send_ack()

    def accept(self):
        self.connection, addr = self.socket.accept()
        self.address = addr[0]
        self.port = addr[1]
        self.seq_num = random.randint(0, MAX_SEQUENCE_NUMBER)
        self.ack_num = 0
        self.recv_syn_ack()
        self.send_syn()
        self.recv_ack()

        return self.connection, addr

    def recv_ack(self):
        packet = self.recv_packet()
        if packet.flag_ack == 1:
            self.last_packet_received = packet
            self.ack_num = packet.seq + 1
        else:
            raise Exception("Received packet is not an ACK packet")
    def close(self):
        self.socket.close()

    def send(self,data):
        chunks = [data[i:i + DATA_LENGTH] for i in range(0, len(data), DATA_LENGTH)]
        # Send packets with PSH flag for each chunk
        for _, chunk in enumerate(chunks):
            packet = self.make_packet(data=chunk, ack=True, psh=True)
            self.send_packet(packet)

    def make_packet(self, data="", ack=False, syn=False, fin=False):
        packet = TCPPacket()
        packet.set_flags(ack=ack, syn=syn, fin=fin)
        packet.seq = self.seq_num
        packet.ack = self.ack_num
        packet.data = data
        return packet

    def send_packet(self, packet):
        """Send a TCP packet over a UDP socket"""
        # Serialize the packet using pickle
        serialized_packet = pickle.dumps(packet)

        # Send the packet with a fixed size of SENT_SIZE
        self.socket.sendto(serialized_packet.ljust(SENT_SIZE, b'\0'), self.connection)
