"""Server for multithreaded file host application."""

import socket
from socket import (
    AF_INET,  # mean ipv4
    SOCK_STREAM,  # mean TCP
    SHUT_RDWR,  # stop read write
)
import datetime
import threading
from threading import Thread
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import struct
import time
import modules.request as req
import modules.shared as shared

# settings:
server_default_port = shared.DEFAULT_SERVER_PORT
client_timeout = None  # seconds
directory_refresh_rate = 1  # seconds


def handle_incoming_connections():
    """Sets up handling for incoming request."""
    while not stop_event.is_set():
        try:
            request_socket, (request_host, request_port) = server.accept()
            request_socket.settimeout(client_timeout)
            request_thread = Thread(
                target=handle_request,
                args=(request_socket, f"{request_host}:{str(request_port)}"),
                daemon=True,
            )
            requests[request_socket] = {"thread": request_thread, "type": None}
            request_thread.start()
        except OSError:
            break

    for request, info in requests.copy().items():
        request.shutdown(SHUT_RDWR)
        request.close()
        info["thread"].join()


def handle_request(sock, ip):
    """Handles a single request connection."""
    try:
        while not stop_event.is_set():
            opcode = struct.unpack(">B", shared.recv_all(sock, 1))[0]
            requests[sock]["type"] = opcode
            match opcode:
                case shared.RRQ:
                    req.process_RRQ(sock, ip)
                case shared.WRQ:
                    req.process_WRQ(sock, ip)
                case shared.DRRQ:
                    req.process_DRRQ(sock, ip)
                case shared.DWRQ:
                    req.process_DWRQ(sock, ip)
                case shared.FWRQ:
                    req.process_FWRQ(sock, ip)
                case shared.DRQ:
                    req.process_DRQ(sock, ip)
                case shared.DTRQ:
                    req.process_DTRQ(sock, ip)
                    break  # no reuse
                case shared.FRQ:
                    req.process_FRQ(sock, ip)
                case _:
                    log(f"[INFO]: {ip} sent an unknown.")
                    req.send_error(sock, ip, "unknown request.")
            requests[sock]["type"] = None
    except ConnectionAbortedError:
        log(f"[INFO]: {ip} disconnected.")
    except OSError as e:
        if not stop_event.is_set():
            log(f"[INFO]: {ip} {str(e)}")
    sock.close()
    del requests[sock]


def stop_server():
    "Stop server properly."
    log("[INFO]: Closing server...")
    root.update_idletasks()
    stop_event.set()
    try:
        server.shutdown(SHUT_RDWR)
    except OSError:
        pass
    server.close()
    directory_thread.join()
    accept_thread.join()
    log("[INFO]: Done.")
    start_button.config(state="normal")
    stop_button.config(state="disabled")
    browse_button.config(state="normal")
    port_entry.config(state="normal")
    directory_entry.config(state="readonly")


def start_server():
    """Start the server and thread."""
    if not validate_input():
        return
    stop_event.clear()
    global server, accept_thread, directory_thread
    server = socket.socket(AF_INET, SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for POSIX systems
    req.set_log_method(log)
    req.set_server_data_path(directory_entry.get())
    req.set_directory_refresh_rate(directory_refresh_rate)
    req.set_stop_event(stop_event)
    try:
        server.bind(("", int(port_entry.get())))
    except OSError as e:
        log(str(e))
        return
    server.listen()
    accept_thread = Thread(target=handle_incoming_connections, daemon=True)
    accept_thread.start()
    directory_thread = Thread(target=req.monitor_directory, daemon=True)
    directory_thread.start()
    log_clear()
    log(f"[INFO]: Listening on port {port_entry.get()}")
    start_button.config(state="disabled")
    stop_button.config(state="normal")
    browse_button.config(state="disabled")
    port_entry.config(state="disabled")
    directory_entry.config(state="disabled")


def log_clear():
    log_area.config(state="normal")
    log_area.delete(1.0, tk.END)
    log_area.config(state="disabled")


def log(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d|%H:%M:%S")
    log_area.config(state="normal")
    log_area.insert(
        tk.END, f"[{current_time}][Threads:{threading.active_count()}]{message}\n"
    )
    log_area.yview(tk.END)
    log_area.config(state="disabled")


def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_entry.config(state="normal")
        directory_entry.delete(0, tk.END)  # Clear any previous text
        directory_entry.insert(0, directory)  # Insert new directory path
        directory_entry.config(state="readonly")


def validate_input():
    if not directory_entry.get():
        tk.messagebox.showerror("Error", "Please choose directory")
        return False
    try:
        port = int(port_entry.get())
    except ValueError:
        tk.messagebox.showerror("Error", "Please enter port number")
        return False
    if port < 0 or port > 65535:
        tk.messagebox.showerror("Error", "Port must be between 0 and 65535")
        return False
    return True


# global variables: (should have use class but server is a singleton anyway.)
server = None
accept_thread = None
directory_thread = None
stop_event = threading.Event()
requests = {}

# Init default window:
root = tk.Tk()
root.title("Server")
root.minsize(width=600, height=600)

style = ttk.Style(root)

main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))

input_frame = ttk.Frame(main_frame)
directory_label = ttk.Label(input_frame, text="Root folder for send and receive files")
browse_button = ttk.Button(input_frame, text="Browse", command=browse_directory)
directory_entry = ttk.Entry(input_frame, width=40, state="readonly")
port_label = ttk.Label(input_frame, text="TCP Port:")
port_entry = ttk.Entry(input_frame, width=13, state="normal")
port_entry.insert(tk.END, str(server_default_port))
start_button = ttk.Button(input_frame, text="Start Server", command=start_server)
stop_button = ttk.Button(
    input_frame, text="Stop Server", command=stop_server, state="disabled"
)

scrolltext_frame = ttk.Frame(main_frame)
log_area = tk.Text(
    scrolltext_frame,
    wrap="word",
    state="disabled",
)
vsb = ttk.Scrollbar(scrolltext_frame, command=log_area.yview, orient="vertical")
log_area.configure(yscrollcommand=vsb.set)

# grid positioning
main_frame.grid(row=0, column=0, sticky="nwes")
input_frame.grid(row=0, column=0, stick="nwes")
directory_label.grid(row=0, column=1, sticky="w")
browse_button.grid(row=1, column=0, padx=4, pady=(0, 4), sticky="w")
directory_entry.grid(row=1, column=1, padx=4, pady=(0, 4), sticky="we")
port_label.grid(row=2, column=0, padx=4, pady=4, stick="e")
port_entry.grid(row=2, column=1, padx=4, pady=4, sticky="w")
start_button.grid(row=3, column=0, padx=4, pady=4, sticky="w")
stop_button.grid(row=3, column=1, padx=4, pady=4, sticky="w")
scrolltext_frame.grid(row=1, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")
log_area.grid(row=0, column=0, sticky="nsew")

# resize weight
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
input_frame.grid_columnconfigure(1, weight=1)
scrolltext_frame.grid_columnconfigure(0, weight=1)
scrolltext_frame.grid_rowconfigure(0, weight=1)

root.mainloop()
