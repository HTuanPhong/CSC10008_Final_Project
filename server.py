"""Server for multithreaded file host application."""

import os
import socket
from socket import (
    AF_INET,  # INER mean ipv4
    SOCK_STREAM,  # Stream mean TCP
    SHUT_RDWR,  # stop read write
)
from threading import Thread
import tkinter as tk
from tkinter import ttk
from modules.message import recv_msg, send_msg, recv_file, send_file


def handle_incoming_connections():
    """Sets up handling for incoming clients."""

    while True:
        try:
            client_socket, (client_host, client_port) = server.accept()
            print(f"[INFO] {client_host}:{client_port} has connected.")
            client_thread = Thread(target=handle_client, args=(client_socket,))
            clients[client_socket] = {
                "address": (client_host, client_port),
                "thread": client_thread,
                "name": f"{client_host}_{client_port}",  # maybe let client choose own name
            }
            client_thread.start()
        except OSError:
            break

    for client, info in clients.copy().items():
        client.shutdown(SHUT_RDWR)
        info["thread"].join()


def handle_upload(sock):
    """Handles the upload request from client."""
    file_path = recv_msg(sock).decode("utf-8")
    local_file_path = os.path.join(SERVER_DATA_PATH, file_path)
    recv_file(sock, local_file_path)


def handle_download(sock):
    """Handles the upload request from client."""
    file_path = recv_msg(sock).decode("utf-8")
    local_file_path = os.path.join(SERVER_DATA_PATH, file_path)
    if os.path.isfile(local_file_path):
        send_file(sock, local_file_path)


def handle_delete(sock):
    """Handles the delete request from client."""
    file_path = recv_msg(sock).decode("utf-8")
    local_file_path = os.path.join(SERVER_DATA_PATH, file_path)
    if os.path.isfile(local_file_path):
        os.remove(local_file_path)


def handle_list(sock):
    """Handles the list request from client."""
    files = os.listdir(SERVER_DATA_PATH)
    send_msg(sock, "\n".join(f for f in files).encode("utf-8"))  # consider os.walk()


def handle_client(sock):
    """Handles a single client connection."""
    name = clients[sock]["name"]
    while True:
        try:
            req = recv_msg(sock).decode("utf-8")
            if req == "LIST":
                handle_list(sock)
            elif req == "UPLOAD":
                handle_upload(sock)
            elif req == "DOWNLOAD":
                handle_download(sock)
            elif req == "DELETE":
                handle_delete(sock)
            elif req == "QUIT":
                break
            else:
                send_msg(sock, "unknown request".encode("utf-8"))
        except OSError as e:
            print(f"[WARNING] {name} OSError occurred:", e)
            break

    sock.close()
    print(f"[INFO] {name} has disconnected.")
    del clients[sock]


def stop_server():
    "Stop server properly."
    server.close()
    accept_thread.join()


def start_server(host, port):
    """Start the server and thread."""
    server.bind((host, port))
    server.listen()
    print(f"[INFO] Listening on {socket.gethostbyname(socket.gethostname())}:{port}")
    accept_thread.start()


# global constants:
SERVER_DATA_PATH = "server"

# global variable: (python have no c like struct imagine.....)
server = socket.socket(AF_INET, SOCK_STREAM)
accept_thread = Thread(target=handle_incoming_connections)
clients = {}

# program flow:
window = tk.Tk()
window.title("Server")


start_server("localhost", 2024)
window.mainloop()
stop_server()
print("[INFO] Finished")
