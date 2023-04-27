import random
from pickle import loads, dumps


DATA_DIVIDE_LENGTH = 1024
TCP_PACKET_SIZE = 32
DATA_LENGTH = DATA_DIVIDE_LENGTH
SENT_SIZE = TCP_PACKET_SIZE + DATA_LENGTH + 5000  # Pickled objects take a lot of space
LAST_CONNECTION = -1
FIRST = 0


cnt = 0
import threading
lock = threading.Lock()

class TCPPacket:
    SMALLEST_STARTING_SEQ = 0
    HIGHEST_STARTING_SEQ = 2**32 - 1
    def __init__(self): 
        global cnt
        # self.seq = TCPPacket.gen_starting_seq_num()
        lock.acquire()
        self.seq = cnt
        self.ack = cnt
        cnt +=1
        lock.release()
        self.data_offset = 0
        self.reserved_field = 0
        self.flag_ns = 0
        self.flag_cwr = 0
        self.flag_ece = 0
        self.flag_urg = 0
        self.flag_ack = 0
        self.flag_psh = 0
        self.flag_rst = 0
        self.flag_syn = 0
        self.flag_fin = 0
        self.window_size = 0
        self.checksum = 0
        self.urgent_pointer = 0
        self.options = 0
        self.padding = 0
        self.data = ''

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
    @staticmethod
    def from_bytes(byte_string) -> 'TCPPacket':
        return loads(byte_string)
    @staticmethod
    def to_bytes(packet) -> bytes:
        return dumps(packet)
