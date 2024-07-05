"""Server for multithreaded file host application."""

import socket
from socket import (
    AF_INET,  # mean ipv4
    SOCK_STREAM,  # mean TCP
    SHUT_RDWR,  # stop read write
)
import datetime
from threading import Thread
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import modules.request as req


def handle_incoming_connections():
    """Sets up handling for incoming request."""

    while True:
        try:
            request_socket, (request_host, request_port) = server.accept()
            request_socket.settimeout(30)
            request_thread = Thread(
                target=handle_request, args=(request_socket,), daemon=True
            )
            requests[request_socket] = {
                "address": (request_host, request_port),
                "thread": request_thread,
            }
            request_thread.start()
        except OSError:
            break

    for request, info in requests.copy().items():
        request.shutdown(SHUT_RDWR)
        info["thread"].join()


def handle_request(sock):
    """Handles a single request connection."""
    ip = requests[sock]["address"][0]
    try:
        req.process_request(sock, ip)
    except OSError as e:
        log(f"[WARN]: {ip} OSError occurred: {str(e)}")

    sock.close()
    del requests[sock]


def stop_server():
    "Stop server properly."
    log("[INFO]: Closing server...")
    server.close()
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
    global server, accept_thread
    server = socket.socket(AF_INET, SOCK_STREAM)
    req.set_log_method(log)
    req.set_server_data_path(directory_entry.get())
    server.bind(("", int(port_entry.get())))
    server.listen()
    accept_thread = Thread(target=handle_incoming_connections, daemon=True)
    accept_thread.start()
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
    log_area.insert(tk.END, f"[{current_time}]{message}\n")
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
requests = {}

# Init default window:
root = tk.Tk()
root.title("Server")
root.iconbitmap("icon.ico")
root.minsize(width=500, height=500)

style = ttk.Style(root)
style.theme_use("clam")

main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))

input_frame = ttk.Frame(main_frame)
directory_label = ttk.Label(input_frame, text="Root folder for send and receive files")
browse_button = ttk.Button(input_frame, text="Browse", command=browse_directory)
directory_entry = ttk.Entry(input_frame, width=40, state="readonly")
port_label = ttk.Label(input_frame, text="TCP Port:")
port_entry = ttk.Entry(input_frame, width=13, state="normal")
start_button = ttk.Button(input_frame, text="Start Server", command=start_server)
stop_button = ttk.Button(
    input_frame, text="Stop Server", command=stop_server, state="disabled"
)

scrolltext_frame = ttk.Frame(main_frame)
log_area = tk.Text(
    scrolltext_frame,
    wrap="word",
    state="disabled",
    background="#000000",
    foreground="#20C20E",
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
