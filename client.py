"""Client demo"""

import time
import os
import shutil
import threading
from threading import Thread
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from queue import Queue
from modules.shared import *
from modules.message import messenger, messengerError
import modules.message as msg
import modules.process as pro

HOST = None
PORT = None
disconnect_event = threading.Event()
directory_lock = threading.Lock()
server_directory = {}
flatten_server_directory = {}
management_msgr = None


def file_progress_ui(file_list, process):
    download_popup = tk.Toplevel(root)
    frame = ttk.Frame(download_popup)
    frame.grid(row=0, column=0, sticky="nwes")
    download_popup.grab_set()
    download_popup.focus_set()
    download_popup.title("Download process")

    btn_frame = ttk.Labelframe(download_popup, text="Button for all files:")
    btn_frame.grid(row=0, column=0, sticky="ew")
    progresses_frame = ttk.Frame(download_popup)
    progresses_frame.grid(row=1, column=0, sticky="nsew")
    canvas = tk.Canvas(progresses_frame)
    scrollbar = ttk.Scrollbar(progresses_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))
    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.bind_all(
        "<MouseWheel>",
        lambda e: canvas.yview_scroll(-1 * int((e.delta / 120)), "units"),
    )
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    download_popup.grid_rowconfigure(1, weight=1)
    download_popup.grid_columnconfigure(0, weight=1)
    progresses_frame.grid_rowconfigure(0, weight=1)
    progresses_frame.grid_columnconfigure(0, weight=1)
    canvas.grid_rowconfigure(0, weight=1)
    canvas.grid_columnconfigure(0, weight=1)
    scrollable_frame.grid_columnconfigure(0, weight=1)
    stop_update = threading.Event()  # tkinter not thread safe
    ui_lock = threading.Lock()

    def update_progress(index, bytes):
        if stop_update.is_set():
            return
        with ui_lock:
            if index not in ui_list:
                return
            ui = ui_list[index]
            ui["progress"]["value"] = bytes
            if bytes == file_list[index][1]:
                progress_frame = ui["frame"]
                del ui_list[index]
                progress_frame.destroy()
            download_popup.update_idletasks()

    manager = process(HOST, PORT, 6, update_progress)

    def cancel(index):
        with ui_lock:
            manager.remove_file(index)
            progress_frame = ui_list[index]["frame"]
            del ui_list[index]
            progress_frame.destroy()

    def toggle_pause(index):
        with ui_lock:
            pause_button = ui_list[index]["pause"]
            if pause_button["text"] == "Pause":
                manager.pause_file(index)
                pause_button.config(text="Resume")
            else:
                manager.resume_file(index)
                pause_button.config(text="Pause")

    def toggle_pause_all():
        with ui_lock:
            if pause_all_button["text"] == "Pause":
                for index, ui in ui_list.items():
                    if ui["pause"]["text"] == "Pause":
                        manager.pause_file(index)
                        ui["pause"].config(text="Resume")
                pause_all_button.config(text="Resume")
            else:
                for index, ui in ui_list.items():
                    if ui["pause"]["text"] == "Resume":
                        manager.resume_file(index)
                        ui["pause"].config(text="Pause")
                pause_all_button.config(text="Pause")

    def cancel_all():
        stop_update.set()
        with ui_lock:
            manager.stop()
            canvas.unbind_all("<MouseWheel>")
            download_popup.destroy()

    ui_list = {}
    for i, file in enumerate(file_list):
        progress_frame = ttk.Labelframe(scrollable_frame, text="From: " + file[0])
        progress_frame.grid(row=i, column=0, pady=5, padx=10, sticky="ew")
        des_label = ttk.Label(progress_frame, text="To: " + file[2])
        des_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        progress_bar = ttk.Progressbar(
            progress_frame, maximum=file[1] + 1, mode="determinate"
        )
        progress_bar.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        total_label = ttk.Label(progress_frame, text="Total: " + format_bytes(file[1]))
        total_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        pause_button = ttk.Button(progress_frame, text="Pause")
        pause_button.config(command=lambda index=i: toggle_pause(index))
        cancel_button = ttk.Button(
            progress_frame,
            text="Cancel",
            command=lambda index=i: cancel(index),
        )
        pause_button.grid(row=2, column=2, padx=5, pady=5, sticky="e")
        cancel_button.grid(row=2, column=3, padx=5, pady=5, sticky="e")
        progress_frame.grid_columnconfigure(0, weight=1)
        ui_list[i] = {
            "frame": progress_frame,
            "progress": progress_bar,
            "pause": pause_button,
            "cancel": cancel_button,
        }

    pause_all_button = ttk.Button(btn_frame, text="Pause", command=toggle_pause_all)
    pause_all_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    cancel_all_button = ttk.Button(btn_frame, text="Cancel", command=cancel_all)
    cancel_all_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    download_popup.update_idletasks()
    width = download_popup.winfo_width()
    height = download_popup.winfo_height()
    rootWidth = root.winfo_width()
    rootHeight = root.winfo_height()
    rootX = root.winfo_x()
    rootY = root.winfo_y()
    x = rootX + (rootWidth // 2) - (width // 2)
    y = rootY + (rootHeight // 2) - (height // 2)
    download_popup.geometry(f"+{x}+{y}")
    download_popup.update_idletasks()
    download_popup.protocol("WM_DELETE_WINDOW", cancel_all)
    manager.add_files(file_list)
    manager.start()

    root.wait_window(download_popup)


def download():
    if not treeview.selection():
        return
    download_dir = tk.filedialog.askdirectory()
    if not download_dir:
        return
    download_set = set()
    download_list = []

    def download_siever(item, parent=download_dir):
        if item["path"] not in download_set:
            download_set.add(item["path"])
            local_path = os.path.normpath(os.path.join(parent, item["name"]))
            file_exist = os.path.exists(local_path)
            if not file_exist or tk.messagebox.askyesno(
                title=f'Replace or Skip {item["type"]}',
                message=f'The destination already has a {"folder" if os.path.isfile(local_path) else "file"} named "{item["name"]}".\nDo you wish to replace it? (no will skip it.)',
            ):  # short-circuit logic
                if item["type"] == "file":
                    if file_exist:
                        os.remove(local_path)
                    download_list.append((item["path"], item["size"], local_path))
                else:
                    if file_exist:
                        shutil.rmtree(local_path)
                    os.mkdir(local_path)
                    for child in item.get("children", []):
                        download_siever(child, local_path)

    for path in treeview.selection():
        download_siever(flatten_server_directory[path])

    file_progress_ui(download_list, pro.DownloadManager)


def upload_files():
    if not treeview.selection():
        return
    file_list = tk.filedialog.askopenfilenames()
    if not file_list:
        return
    destination = treeview.selection()[0]
    if flatten_server_directory[destination]["type"] == "file":
        destination = os.path.dirname(destination)
    upload_list = []
    delete_list = []
    for file in file_list:
        file_name = os.path.basename(file)
        server_path = os.path.normpath(os.path.join(destination, file_name))
        file_exist = server_path in flatten_server_directory
        if not file_exist or tk.messagebox.askyesno(
            title=f"Replace or Skip file",
            message=f'The destination already has a {flatten_server_directory[server_path]["type"]} named "{file_name}".\nDo you wish to replace it? (no will skip it.)',
        ):
            if file_exist:
                delete_list.append(server_path)
            upload_list.append(
                (os.path.normpath(file), os.path.getsize(file), server_path)
            )
    try:
        for path in delete_list:
            management_msgr.send_DRQ(path)
        for file in upload_list:
            management_msgr.send_WRQ(file[2], file[1])
    except (OSError, messengerError) as e:
        tk.messagebox.showerror("Error", str(e))
        return
    file_progress_ui(upload_list, pro.UploadManager)


def upload_folder():
    if not treeview.selection():
        return
    folder = tk.filedialog.askdirectory()
    if not folder:
        return
    destination = treeview.selection()[0]
    if flatten_server_directory[destination]["type"] == "file":
        destination = os.path.dirname(destination)
    upload_list = []
    delete_list = []
    make_list = []

    def upload_siever(root_dir, current_path):
        with os.scandir(root_dir) as it:
            for entry in it:
                server_path = os.path.join(current_path, entry.name)
                if not entry.is_dir(follow_symlinks=False):
                    upload_list.append(
                        (
                            # python module maker need to agree on the path like tkinter give / os.path give \\ scandir path give / MAKE UP UR MIND!
                            os.path.normpath(entry.path),
                            entry.stat().st_size,
                            server_path,
                        )
                    )
                else:
                    make_list.append(server_path)
                    upload_siever(entry.path, server_path)

    folder_name = os.path.basename(folder)
    server_path = os.path.normpath(os.path.join(destination, folder_name))
    entry_exist = server_path in flatten_server_directory
    if not entry_exist or tk.messagebox.askyesno(
        title=f"Replace or Skip folder",
        message=f'The destination already has a {flatten_server_directory[server_path]["type"]} named "{folder_name}".\nDo you wish to replace it? (no will skip it.)',
    ):
        if entry_exist:
            delete_list.append(server_path)
        make_list.append(server_path)
        upload_siever(folder, server_path)
    try:
        for path in delete_list:
            management_msgr.send_DRQ(path)
        for directory in make_list:
            management_msgr.send_FRQ(directory)
        for file in upload_list:
            management_msgr.send_WRQ(file[2], file[1])
    except (OSError, messengerError) as e:
        tk.messagebox.showerror("Error", str(e))
        return

    file_progress_ui(upload_list, pro.UploadManager)


def flatten_directory():
    flat_dict = {}

    def _flatten(item):
        flat_dict[item["path"]] = item
        if item["type"] == "folder":
            for child in item.get("children", []):
                _flatten(child)

    _flatten(server_directory)
    return flat_dict


def normalize_directory(dir):
    dir["path"] = os.path.normpath(dir["path"])
    if dir["type"] == "folder":
        for child in dir.get("children", []):
            normalize_directory(child)


def monitor_directory(msgr):
    try:
        msgr.sub_DTRQ()
        global server_directory, flatten_server_directory
        while not disconnect_event.is_set():
            data = msgr.recv_DTRQ()
            with directory_lock:
                normalize_directory(data)
                server_directory = data
                flatten_server_directory = flatten_directory()
                update_directory()
    except (OSError, messengerError) as e:
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
    global HOST, PORT, management_msgr
    HOST = host_entry.get()
    PORT = int(port_entry.get())
    try:
        dir_msgr = messenger(HOST, PORT)
        management_msgr = messenger(HOST, PORT)
    except (OSError, messengerError) as e:
        tk.messagebox.showerror("Error", str(e))
        return
    disconnect_event.clear()
    directory_thread = Thread(target=monitor_directory, args=(dir_msgr,), daemon=True)
    directory_thread.start()

    connect_button.config(state="disabled")
    upload_files_button.config(state="normal")
    upload_folder_button.config(state="normal")
    download_button.config(state="normal")
    folder_button.config(state="normal")
    delete_button.config(state="normal")
    disconnect_button.config(state="normal")
    host_entry.config(state="disabled")
    port_entry.config(state="disabled")
    search_entry.config(state="normal")


def disconnect():
    if directory_lock.locked():
        return
    disconnect_event.set()
    msg.disconnect_all()
    treeview.delete(*treeview.get_children())
    connect_button.config(state="normal")
    upload_files_button.config(state="disabled")
    upload_folder_button.config(state="disabled")
    download_button.config(state="disabled")
    folder_button.config(state="disabled")
    delete_button.config(state="disabled")
    disconnect_button.config(state="disabled")
    host_entry.config(state="normal")
    port_entry.config(state="normal")
    search_entry.config(state="disabled")


def delete():
    if not treeview.selection():
        return
    try:
        for path in treeview.selection():
            management_msgr.send_DRQ(path)
    except (OSError, messengerError) as e:
        tk.messagebox.showerror("Error", str(e))


def ask_string(title, prompt):
    def on_ok():
        result.set(entry.get())
        popup.destroy()

    result = tk.StringVar()
    result.set(None)
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.grid_rowconfigure(0, weight=1)
    popup.grid_columnconfigure(0, weight=1)
    frame = ttk.Frame(popup)
    frame.grid(row=0, column=0, sticky="nwes")
    label = ttk.Label(frame, text=prompt)
    label.grid(row=0, column=0, padx=0, pady=5, columnspan=2)
    entry = ttk.Entry(frame)
    entry.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
    entry.focus_set()
    ok_button = ttk.Button(frame, text="OK", command=on_ok)
    ok_button.grid(row=2, column=0, padx=5, pady=5)
    cancel_button = ttk.Button(frame, text="Cancel", command=popup.destroy)
    cancel_button.grid(row=2, column=1, padx=5, pady=5)
    popup.resizable(False, False)
    popup.transient(root)
    popup.grab_set()
    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    rootWidth = root.winfo_width()
    rootHeight = root.winfo_height()
    rootX = root.winfo_x()
    rootY = root.winfo_y()
    x = rootX + (rootWidth // 2) - (width // 2)
    y = rootY + (rootHeight // 2) - (height // 2)
    popup.geometry(f"+{x}+{y}")
    root.wait_window(popup)
    return result.get()


def folder():
    if not treeview.selection():
        return
    last_path = treeview.selection()[0]
    name = ask_string("Input", "Please enter folder name:")
    if not name:
        return
    try:
        if flatten_server_directory[last_path]["type"] == "folder":
            management_msgr.send_FRQ(os.path.join(last_path, name))
        else:
            management_msgr.send_FRQ(os.path.join(os.path.dirname(last_path), name))
    except (OSError, messengerError) as e:
        tk.messagebox.showerror("Error", str(e))


def highlight_row(event):
    tree = event.widget
    item = tree.identify_row(event.y)
    tree.tk.call(tree, "tag", "remove", "highlight")
    if item:
        tree.item(item, tags=("highlight",))


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


root = tk.Tk()
root.title("Client")
root.minsize(width=600, height=600)

style = ttk.Style(root)

main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))

popup = tk.Menu(root, tearoff=0)
popup.add_command(label="Delete", command=delete)
popup.add_command(label="Make folder", command=folder)
popup.add_command(label="Download", command=download)
popup.add_command(label="Upload files", command=upload_files)
popup.add_command(label="Upload folder", command=upload_folder)

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
upload_files_button = ttk.Button(
    operation_frame, text="Upload files", state="disabled", command=upload_files
)
upload_folder_button = ttk.Button(
    operation_frame, text="Upload folder", state="disabled", command=upload_folder
)
search_frame = ttk.Frame(input_frame)
search_var = tk.StringVar()
search_var.trace("w", search_dir)
search_label = ttk.Label(search_frame, text="Query name:")
search_entry = ttk.Entry(search_frame, textvariable=search_var, state="disabled")
dir_frame = ttk.Frame(main_frame)

treeview = ttk.Treeview(dir_frame)
treeview["columns"] = ("mtime", "size")
treeview.heading("#0", text="Server's directory", anchor="w")
treeview.heading("mtime", text="Data modified", anchor="w")
treeview.heading("size", text="Size", anchor="w")
treeview.tag_configure("highlight", background="lightblue")
treeview.bind("<Motion>", highlight_row)
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
upload_files_button.grid(row=0, column=3, padx=4, pady=4, sticky="w")
upload_folder_button.grid(row=0, column=4, padx=4, pady=4, sticky="w")
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
