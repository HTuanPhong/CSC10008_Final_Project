"""Server for multithreaded file host application."""

import os
import socket
from socket import (
    AF_INET,  # mean ipv4
    SOCK_STREAM,  # mean TCP
    SHUT_RDWR,  # stop read write
)
from threading import Thread
import tkinter as tk
from tkinter import ttk
import modules.request as req


def handle_incoming_connections():
    """Sets up handling for incoming clients."""

    while True:
        try:
            request_socket, (request_host, request_port) = server.accept()
            request_socket.settimeout(30)
            print(f"[INFO] {request_host}:{request_port} has connected.")
            request_thread = Thread(
                target=handle_request, args=(request_socket,), daemon=True
            )
            requests[request_socket] = {
                # "address": (request_host, request_port),
                "thread": request_thread,
                "name": f"{request_host}:{request_port}",
            }
            request_thread.start()
        except OSError:
            break

    for request, info in requests.copy().items():
        request.shutdown(SHUT_RDWR)
        info["thread"].join()


def handle_request(sock):
    """Handles a single request connection."""
    name = requests[sock]["name"]
    try:
        req.process_request(sock)
    except OSError as e:
        print(f"[WARNING] {name} OSError occurred:", e)

    sock.close()
    print(f"[INFO] {name} has finished.")
    del requests[sock]


def stop_server():
    "Stop server properly."
    print("[INFO] Closing server...")
    server.close()
    accept_thread.join()


def start_server():
    """Start the server and thread."""
    server.bind(("", PORT))
    server.listen()
    print(f"[INFO] Listening on port {PORT}")
    accept_thread.start()


# global variables: (should have use class but server is a singleton anyway.)
SERVER_DATA_PATH = "server"
PORT = 2024
server = socket.socket(AF_INET, SOCK_STREAM)
accept_thread = Thread(target=handle_incoming_connections, daemon=True)
requests = {}

if __name__ == "__main__":
    # program flow:
    MainWindow = tk.Tk()
    MainWindow.title("Server")
    MainWindow.minsize(width=500, height=400)

    top_frame = ttk.Frame(MainWindow)
    top_frame.grid(column=0, row=0)

    ttk.Label(top_frame, text="Name:").grid(column=0, row=0, padx=5, pady=5)

    start_server()
    MainWindow.mainloop()
    stop_server()

    print("[INFO] Finished")
