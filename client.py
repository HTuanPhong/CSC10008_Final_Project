"""Client main"""

from socket import AF_INET, socket, SOCK_STREAM  # Stream mean TCP
import modules.message as msg

HOST = "192.168.1.11"  # IP adress server
PORT = 1234  # Port is used by the server
FORMAT = "utf-8"

CLIENT = socket(AF_INET, SOCK_STREAM)

print("[c] Connecting...")
CLIENT.connect((HOST, PORT))

msg.send_DRQ(CLIENT, "bigo.png")


print("[c] Quitting...")
CLIENT.close()
