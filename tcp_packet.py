import random
import pickle as pkl


DATA_DIVIDE_LENGTH = 1024
TCP_PACKET_SIZE = 32
DATA_LENGTH = DATA_DIVIDE_LENGTH
SENT_SIZE = TCP_PACKET_SIZE + DATA_LENGTH + 5000  # Pickled objects take a lot of space
LAST_CONNECTION = -1
FIRST = 0



class TCPPacket:
    SMALLEST_STARTING_SEQ = 0
    HIGHEST_STARTING_SEQ = 2**32 - 1
    def __init__(self): 
        global cnt
        self.seq = TCPPacket.generate_starting_seq_num()
        self.ack = 0
        # self.ack = TCPPacket.generate_starting_seq_num()
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
        self.checksum = 0

    def __repr__(self):
        return "TCPpacket()"

    def __str__(self):
        return f"SEQ Number: {self.seq}, ACK Number: {self.ack}, ACK: {self.flag_ack},\
                SYN: {self.flag_syn}, FIN: {self.flag_fin}, \
                TYPE: {self.packet_type()}, DATA: {self.data}, checksum: {self.checksum}"

    def __cmp__(self, other):
        # Fix 
        if self.seq == other.seq:
            return 0
        return 1
    def set_data(self, data):
        self.data = data
        self.checksum = self.__calc_checksum()

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

    def __calc_checksum(self):
        # Get the message as bytes from string
        message = pkl.dumps(self.data)
        # If the message length is odd, add a zero byte at the end
        if len(message) % 2 == 1:
            message += b'\x00' # Pad the message with a null byte

        # Split the message into 16-bit words and add them together
        words = [int.from_bytes(message[i:i+2], byteorder='big') for i in range(0, len(message), 2)]
        total = sum(words)

        # Fold the total into 16 bits by adding the carry to the least significant 16 bits
        while total >> 16:
            total = (total & 0xFFFF) + (total >> 16)

        # Take the one's complement of the result
        result = (~total) & 0xFFFF

        # Return the checksum as a 16-bit integer
        return result

    def verify_checksum(self):
        return self.checksum == self.__calc_checksum()
    @staticmethod
    def generate_starting_seq_num():
        return random.randint(TCPPacket.SMALLEST_STARTING_SEQ, TCPPacket.HIGHEST_STARTING_SEQ)
    @staticmethod
    def from_bytes(byte_string) -> 'TCPPacket':
        return pkl.loads(byte_string)
    @staticmethod
    def to_bytes(packet) -> bytes:
        return pkl.dumps(packet)
