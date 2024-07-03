"""Client main"""

import os
import struct
from socket import AF_INET, socket, SOCK_STREAM, SHUT_RDWR  # Stream mean TCP
import modules.request as req

HOST = "127.0.0.1"  # IP adress server
PORT = 2024  # Port is used by the server
FORMAT = "utf-8"

CLIENT = socket(AF_INET, SOCK_STREAM)

print("[c] Connecting...")
CLIENT.connect((HOST, PORT))

file_name = "bigo.png"
MSG = (
    struct.pack(">B", 6)  # , len(file_name))
    # + file_name.encode("utf-8")
    # + struct.pack(">QQ", 0, 1364554)
    # + "LMAO!".encode("utf-8")
)
CLIENT.sendall(MSG)
# with open("client/bigo.png", "rb") as f:
#     CLIENT.sendfile(f)

REC = req.recv_all(CLIENT, 1)
a = struct.unpack(">B", REC)[0]
print(a)
REC = req.recv_all(CLIENT, 4)
a = struct.unpack(">I", REC)[0]
print(a)
REC = req.recv_all(CLIENT, a)
print(REC.decode("utf-8"))

print("[c] Quitting...")
CLIENT.close()
