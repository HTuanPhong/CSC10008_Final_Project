"""Client demo"""

import time
import os
import threading
from threading import Thread
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from queue import Queue
from modules.shared import *
from modules.message import messenger, messengerError
import modules.message as msg

HOST = None
PORT = None
disconnect_event = threading.Event()
directory_lock = threading.Lock()
server_directory = {}
flatten_server_directory = {}


def download():
    if not treeview.selection():
        return
    download_dir = tk.filedialog.askdirectory()
    if not download_dir:
        return
    for path in treeview.selection():
        print(path)


def upload():
    if not treeview.selection():
        return
    file_list = tk.filedialog.askopenfilenames()
    if not file_list:
        return
    for path in file_list:
        print(path)


def flatten_directory():
    flat_dict = {}

    def _flatten(item):
        flat_dict[item["path"]] = item
        if item["type"] == "folder":
            for child in item.get("children", []):
                _flatten(child)

    _flatten(server_directory)
    return flat_dict


def monitor_directory(msgr):
    try:
        msgr.sub_DTRQ()
        global server_directory, flatten_server_directory
        while not disconnect_event.is_set():
            data = msgr.recv_DTRQ()
            with directory_lock:
                server_directory = data
                flatten_server_directory = flatten_directory()
                update_directory()
    except (OSError, msg.messengerError) as e:
        if not disconnect_event.is_set():
            tk.messagebox.showerror("Error", str(e))
        disconnect()


def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    while size >= power and n < len(units) - 1:
        size /= power
        n += 1
    formatted_size = f"{size:.2f}".rstrip("0").rstrip(".")
    return f"{formatted_size} {units[n]}"


def update_directory(query=""):
    def process_directory(
        item,
        query="",
        parent="",
    ):
        if item["type"] == "folder":
            if not treeview.exists(item["path"]):
                treeview.insert(
                    parent,
                    0,
                    item["path"],
                    text=item["name"],
                    image=folder_image,
                )
            else:
                children = treeview.get_children(item["path"])
                for child in children:
                    if child not in flatten_server_directory or query not in child:
                        treeview.delete(child)
            for child in item.get("children", []):
                process_directory(child, query, item["path"])
        elif item["type"] == "file":
            if query in item["name"] and not treeview.exists(item["path"]):
                treeview.insert(
                    parent,
                    0,
                    item["path"],
                    text=item["name"],
                    image=file_image,
                    values=(
                        time.strftime(
                            "%Y-%m-%d %H:%M:%S", time.localtime(item["mtime"])
                        ),
                        format_bytes(item["size"]),
                    ),
                )

    process_directory(server_directory, query.lower())


def validate_input():
    try:
        port = int(port_entry.get())
    except ValueError:
        tk.messagebox.showerror("Error", "Please enter port number")
        return False
    if port < 0 or port > 65535:
        tk.messagebox.showerror("Error", "Port must be between 0 and 65535")
        return False
    return True


def connect():
    if not validate_input():
        return
    global HOST, PORT
    HOST = host_entry.get()
    PORT = int(port_entry.get())
    try:
        dir_msg = messenger(HOST, PORT)
    except (OSError, msg.messengerError) as e:
        tk.messagebox.showerror("Error", str(e))
        return
    disconnect_event.clear()
    directory_thread = Thread(target=monitor_directory, args=(dir_msg,), daemon=True)
    directory_thread.start()

    connect_button.config(state="disabled")
    upload_button.config(state="normal")
    download_button.config(state="normal")
    folder_button.config(state="normal")
    delete_button.config(state="normal")
    disconnect_button.config(state="normal")
    host_entry.config(state="disabled")
    port_entry.config(state="disabled")


def disconnect():
    if directory_lock.locked():
        return
    disconnect_event.set()
    msg.disconnect_all()
    treeview.delete(*treeview.get_children())
    connect_button.config(state="normal")
    upload_button.config(state="disabled")
    download_button.config(state="disabled")
    folder_button.config(state="disabled")
    delete_button.config(state="disabled")
    disconnect_button.config(state="disabled")
    host_entry.config(state="normal")
    port_entry.config(state="normal")


def delete():
    if not treeview.selection():
        return
    try:
        mes = messenger(HOST, PORT)
        for path in treeview.selection():
            mes.send_DRQ(path)
    except (OSError, msg.messengerError) as e:
        tk.messagebox.showerror("Error", str(e))
    finally:
        mes.close()


def folder():
    if not treeview.selection():
        return
    try:
        mes = messenger(HOST, PORT)
        last_path = treeview.selection()[-1]
        name = tk.simpledialog.askstring("Input", "Please enter folder name:")
        if not name:
            return
        if flatten_server_directory[last_path]["type"] == "folder":
            mes.send_FRQ(os.path.join(last_path, name))
        else:
            mes.send_FRQ(os.path.join(os.path.dirname(last_path), name))
    except (OSError, msg.messengerError) as e:
        tk.messagebox.showerror("Error", str(e))
    finally:
        mes.close()


def popup_menu(event):
    selected_item = treeview.identify_row(event.y)
    if selected_item not in treeview.selection():
        treeview.selection_set(selected_item)

    popup.tk_popup(event.x_root, event.y_root)


def search_dir(*args):
    if directory_lock.locked():
        return
    with directory_lock:
        update_directory(search_var.get())


explorer_objects = {}

root = tk.Tk()
root.title("Client")
root.minsize(width=600, height=600)

style = ttk.Style(root)
style.theme_use("clam")

main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))

popup = tk.Menu(root, tearoff=0)
popup.add_command(label="Delete", command=delete)
popup.add_command(label="Make folder", command=folder)
popup.add_command(label="Download", command=download)
popup.add_command(label="Upload", command=upload)

input_frame = ttk.Frame(main_frame)
connection_frame = ttk.Frame(input_frame)
host_label = ttk.Label(connection_frame, text="IPv4 host:")
host_entry = ttk.Entry(connection_frame, width=26, state="normal")
host_entry.insert(tk.END, "127.0.0.1")
port_label = ttk.Label(connection_frame, text="TCP port:")
port_entry = ttk.Entry(connection_frame, width=13, state="normal")
port_entry.insert(tk.END, str(DEFAULT_SERVER_PORT))
connect_button = ttk.Button(connection_frame, text="Connect", command=connect)
disconnect_button = ttk.Button(
    connection_frame, text="Disconnect", state="disabled", command=disconnect
)
operation_frame = ttk.Frame(input_frame)
delete_button = ttk.Button(
    operation_frame, text="Delete", state="disabled", command=delete
)
folder_button = ttk.Button(
    operation_frame, text="Make folder", state="disabled", command=folder
)
download_button = ttk.Button(
    operation_frame, text="Download", state="disabled", command=download
)
upload_button = ttk.Button(
    operation_frame, text="Upload", state="disabled", command=upload
)
search_frame = ttk.Frame(input_frame)
search_var = tk.StringVar()
search_var.trace("w", search_dir)
search_label = ttk.Label(search_frame, text="Query name:")
search_entry = ttk.Entry(search_frame, textvariable=search_var)
dir_frame = ttk.Frame(main_frame)

treeview = ttk.Treeview(dir_frame)
treeview["columns"] = ("mtime", "size")
treeview.heading("#0", text="Server's directory", anchor="w")
treeview.heading("mtime", text="Data modified", anchor="w")
treeview.heading("size", text="Size", anchor="w")
treeview.bind("<Button-3>", popup_menu)
vsb = ttk.Scrollbar(dir_frame, orient="vertical", command=treeview.yview)
treeview.configure(yscrollcommand=vsb.set)

main_frame.grid(row=0, column=0, sticky="nwes")
input_frame.grid(row=0, column=0, stick="nwes")
connection_frame.grid(row=0, column=0, sticky="w")
search_frame.grid(row=3, column=0, sticky="ew")
search_label.grid(row=0, column=0, padx=4, pady=4, sticky="w")
search_entry.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
host_label.grid(row=0, column=0, padx=4, pady=4, sticky="w")
host_entry.grid(row=0, column=1, padx=4, pady=4, sticky="w")
port_label.grid(row=0, column=2, padx=4, pady=4, sticky="w")
port_entry.grid(row=0, column=3, padx=4, pady=4, sticky="w")
connect_button.grid(row=0, column=4, padx=4, pady=4, sticky="w")
disconnect_button.grid(row=0, column=5, padx=4, pady=4, sticky="w")
operation_frame.grid(row=1, column=0, sticky="w")
delete_button.grid(row=0, column=0, padx=4, pady=4, sticky="w")
folder_button.grid(row=0, column=1, padx=4, pady=4, sticky="w")
download_button.grid(row=0, column=2, padx=4, pady=4, sticky="w")
upload_button.grid(row=0, column=3, padx=4, pady=4, sticky="w")
dir_frame.grid(row=1, column=0, sticky="nsew")
treeview.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
search_frame.grid_columnconfigure(1, weight=1)
# input_frame.grid_columnconfigure(1, weight=1)
dir_frame.grid_rowconfigure(0, weight=1)
dir_frame.grid_columnconfigure(0, weight=1)

file_image = tk.PhotoImage(file="file.png")
folder_image = tk.PhotoImage(file="folder.png")

root.mainloop()
