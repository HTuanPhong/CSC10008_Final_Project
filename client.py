"""Client main"""

import os
from socket import AF_INET, socket, SOCK_STREAM, SHUT_RDWR  # Stream mean TCP
from modules.message import recv_msg, send_msg, recv_file, send_file


HOST = "127.0.0.1"  # IP adress server
PORT = 2024  # Port is used by the server
FORMAT = "utf-8"

CLIENT = socket(AF_INET, SOCK_STREAM)

print("[c] Connecting...")
CLIENT.connect((HOST, PORT))


MSG = "UPLOAD"
send_msg(CLIENT, MSG.encode(FORMAT))

FILE_NAME = "Sega Genesis (Mega Drive) & Sega 32X Complete Romset.zip"
send_msg(CLIENT, FILE_NAME.encode(FORMAT))

file_path = os.path.join("client", FILE_NAME)
send_file(CLIENT, file_path)

print("[c] Quitting...")
CLIENT.close()
