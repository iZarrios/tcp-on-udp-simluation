import struct

def pack_msg(struct_fmt="!I%ds", *args):
    return struct.pack(struct_fmt, *args)

def unpack_msg(struct_fmt="!I%ds", data=None):
    return struct.unpack(struct_fmt, data)
