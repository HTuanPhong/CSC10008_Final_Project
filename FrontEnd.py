import customtkinter
import tkinter
from tkinter import filedialog, Menu, ttk
from PIL import Image, ImageTk

import socket
import time
import os
import shutil
import threading
from threading import Thread
from queue import Queue
from modules.shared import *
from modules.message import Messenger, MessengerError
import modules.message as msg
import modules.process as pro


HOST = None
PORT = None
SEGMENT = 65536
THREAD = 8
disconnect_event = threading.Event()
directory_lock = threading.Lock()
server_directory = {}
flatten_server_directory = {}
management_msgr = None
hostname = socket.gethostname()
hostip = socket.gethostbyname(hostname)

# ============================================================={{ configure WINDOW }}===========================================================
# Set mode and default theme
customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("blue")

# Define constant
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 1000
MENU_COLLAPSED_WIDTH = 45
MENU_EXPANDED_WIDTH = 167
DELTA_WIDTH = 10
FILE_ITEM_WIDTH = 75
FILE_ITEM_HEIGHT = 100
SPACE_X = 20
SPACE_Y = 20
SCROLL_FRAME_WIDTH = 700
SCROLL_FRAME_HEIGHT = 500

# Initialize the main window
window = customtkinter.CTk()
window.title("File Transfer")
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
# window.minsize(940, 500)
bold_font = customtkinter.CTkFont(weight="bold", size=14)

# ============================================================={{ MENU }}===========================================================
# region Expand/Collapse Function
# --------------------------------------------------// Image - Icon \\ --------------------------------------------------
toggle_icon = customtkinter.CTkImage(
    dark_image=Image.open("Image/menu.png"),
    light_image=Image.open("Image/menu.png"),
    size=(20, 20),
)
close_icon = customtkinter.CTkImage(
    dark_image=Image.open("Image/close.png"),
    light_image=Image.open("Image/close.png"),
    size=(18, 18),
)

# --------------------------------------------------// Function \\ --------------------------------------------------
ANIMATION_DELAY = 8  # ms


def update_content_frame(menu_width):
    content_width = WINDOW_WIDTH - menu_width
    content_frame.configure(width=content_width)
    content_frame.place(relwidth=1.0, relheight=1.0, x=menu_width, y=0)


def update_menu_frame(width: int):
    menu_frame.configure(width=width)
    explorer_icon_button.configure(width=width - 2)
    setting_icon_button.configure(width=width - 2)


def extending_amination():
    startFrame = time.time()
    current_width = menu_frame.cget("width")
    if current_width < MENU_EXPANDED_WIDTH:
        if current_width < (MENU_EXPANDED_WIDTH - DELTA_WIDTH):
            current_width += DELTA_WIDTH
        else:
            current_width = MENU_EXPANDED_WIDTH
        update_menu_frame(current_width)
        update_content_frame(current_width)
        if not is_folding:
            currentTime = currentTime = int((time.time() - startFrame) * 1000)
            window.after(ms=max(8 - currentTime, 0), func=extending_amination)


def folding_amination():
    startFrame = time.time()
    current_width = menu_frame.cget("width")
    if current_width > MENU_COLLAPSED_WIDTH:
        if current_width > (MENU_COLLAPSED_WIDTH + DELTA_WIDTH):
            current_width -= DELTA_WIDTH
        else:
            current_width = MENU_COLLAPSED_WIDTH
        update_menu_frame(current_width)
        update_content_frame(current_width)
        if is_folding:
            currentTime = int((time.time() - startFrame) * 1000)
            window.after(ms=max(8 - currentTime, 0), func=folding_amination)


def extending_menu():
    global is_folding
    is_folding = False
    extending_amination()
    toggle_button.configure(image=close_icon)
    toggle_button.configure(command=folding_menu)


def folding_menu():
    global is_folding
    is_folding = True
    folding_amination()
    toggle_button.configure(image=toggle_icon)
    toggle_button.configure(command=extending_menu)


def deactivate():
    explorer_indicate.configure(fg_color="lightblue")
    setting_indicate.configure(fg_color="lightblue")

    explorer_icon_button.configure(fg_color="lightblue")
    setting_icon_button.configure(fg_color="lightblue")


def raise_frame(frame):
    frame.tkraise()


# --------------------------------------------------// Frame \\ --------------------------------------------------
menu_frame = customtkinter.CTkFrame(
    window, height=WINDOW_HEIGHT, width=MENU_COLLAPSED_WIDTH, fg_color="lightblue"
)
menu_frame.place(relheight=1.0, x=0, y=0)

content_frame = customtkinter.CTkFrame(
    window,
    fg_color="white",
)
content_frame.place(relwidth=1.0, relheight=1.0, x=MENU_COLLAPSED_WIDTH, y=0)

explorer_frame = customtkinter.CTkFrame(content_frame, fg_color="white")
explorer_frame.place(relwidth=1.0, relheight=1.0)

setting_frame = customtkinter.CTkFrame(content_frame, fg_color="white")
setting_frame.place(relwidth=1.0, relheight=1.0)


# --------------------------------------------------// Object \\ --------------------------------------------------
is_folding = False
toggle_button = customtkinter.CTkButton(
    menu_frame,
    image=toggle_icon,
    width=10,
    fg_color="lightblue",
    hover_color="#CCFFFF",
    text="",
    command=extending_menu,
)
toggle_button.place(x=5, y=10)

# endregion


# --------------------------------------------------// Image - Icon \\ --------------------------------------------------
explorer_icon = customtkinter.CTkImage(
    dark_image=Image.open("Image/explorer.png"),
    light_image=Image.open("Image/explorer.png"),
    size=(25, 25),
)
setting_icon = customtkinter.CTkImage(
    dark_image=Image.open("Image/setting-lines.png"),
    light_image=Image.open("Image/setting-lines.png"),
    size=(25, 25),
)


# --------------------------------------------------// Function \\ --------------------------------------------------
def indicate_explorer():
    deactivate()
    explorer_indicate.configure(fg_color="#0033FF")
    explorer_icon_button.configure(fg_color="#CCFFFF")

    if menu_frame.cget("width") > 45:
        folding_menu()

    raise_frame(explorer_frame)


def indicate_setting():
    deactivate()
    setting_indicate.configure(fg_color="#0033FF")
    setting_icon_button.configure(fg_color="#CCFFFF")

    if menu_frame.cget("width") > 45:
        folding_menu()

    raise_frame(setting_frame)


# --------------------------------------------------// Object \\ --------------------------------------------------

explorer_icon_button = customtkinter.CTkButton(
    menu_frame,
    image=explorer_icon,
    width=165,
    height=32,
    fg_color="lightblue",
    hover_color="#CCFFFF",
    text=" Explorer",
    font=("Helvetica", 18),
    text_color="black",
    anchor="w",
    command=indicate_explorer,
)
explorer_icon_button.place(x=1, y=100)


explorer_indicate = customtkinter.CTkLabel(
    menu_frame, text=" ", fg_color="lightblue", height=31, bg_color="lightblue"
)
explorer_indicate.place(x=0, y=100)


setting_icon_button = customtkinter.CTkButton(
    menu_frame,
    image=setting_icon,
    width=165,
    height=32,
    fg_color="lightblue",
    hover_color="#CCFFFF",
    text=" Setting",
    font=("Helvetica", 18),
    text_color="black",
    anchor="w",
    command=indicate_setting,
)
setting_icon_button.place(x=1, y=150)


setting_indicate = customtkinter.CTkLabel(
    menu_frame, text=" ", fg_color="#0033FF", height=31, bg_color="lightblue"
)
setting_indicate.place(x=0, y=150)


raise_frame(setting_frame)

# -------------------------------------------------------------- // Function \\ --------------------------------------------------------------


def file_progress_ui(file_list, process):

    style = ttk.Style()
    style.configure("White.TFrame", background="white")
    style.configure("White.TLabelframe", background="white", font=("Arial", 15))
    style.configure("White.TLabel", background="white", font=("Arial", 10))
    style.configure("White.TButton", font=("Arial", 10))

    download_popup = customtkinter.CTkToplevel(window)
    frame = ttk.Frame(download_popup, style="White.TFrame")
    frame.grid(row=0, column=0, sticky="nwes")
    download_popup.grab_set()
    download_popup.focus_set()
    download_popup.title("Process")

    btn_frame = ttk.Labelframe(
        download_popup, text="Button for all files:", style="White.TLabelframe"
    )
    btn_frame.grid(row=0, column=0, sticky="ew")
    progresses_frame = ttk.Frame(download_popup, style="White.TFrame")
    progresses_frame.grid(row=1, column=0, sticky="nsew")

    canvas = tkinter.Canvas(progresses_frame, bg="white")
    scrollbar = ttk.Scrollbar(progresses_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, style="White.TFrame")
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
    ui_lock = threading.Lock()
    cancel_event = threading.Event()
    cancel_event.clear()
    not_pause = threading.Event()
    not_pause.set()

    def update_progress(index, bytes):
        if cancel_event.is_set():
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
        if bytes == file_list[index][1]:
            not_pause.wait()
            with ui_lock:
                add_next_file()

    manager = process(HOST, PORT, THREAD, SEGMENT, update_progress)

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
                not_pause.clear()
                for index, ui in ui_list.items():
                    if ui["pause"]["text"] == "Pause":
                        manager.pause_file(index)
                        ui["pause"].config(text="Resume")
                pause_all_button.config(text="Resume")
            else:
                not_pause.set()
                for index, ui in ui_list.items():
                    if ui["pause"]["text"] == "Resume":
                        manager.resume_file(index)
                        ui["pause"].config(text="Pause")
                pause_all_button.config(text="Pause")

    def pause_all():
        t = threading.Thread(target=toggle_pause_all, daemon=True)
        t.start()

    def cancel_all_thread():
        not_pause.set()
        cancel_event.set()
        manager.stop()
        canvas.unbind_all("<MouseWheel>")
        download_popup.destroy()

    def cancel_all():
        t = threading.Thread(target=cancel_all_thread, daemon=True)
        t.start()

    ui_list = {}
    index = 0

    def add_next_file():
        nonlocal index, ui_list
        if index >= len(file_list):
            return
        file = file_list[index]
        progress_frame = ttk.Labelframe(
            scrollable_frame, text="From: " + file[0], style="White.TLabelframe"
        )
        progress_frame.grid(row=index, column=0, pady=5, padx=10, sticky="ew")
        des_label = ttk.Label(
            progress_frame, text="To: " + file[2], style="White.TLabel"
        )
        des_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        progress_bar = ttk.Progressbar(
            progress_frame, maximum=file[1] + 1, mode="determinate"
        )
        progress_bar.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        total_label = ttk.Label(
            progress_frame, text="Total: " + format_bytes(file[1]), style="White.TLabel"
        )
        total_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        pause_button = ttk.Button(progress_frame, text="Pause", style="White.TButton")
        pause_button.config(command=lambda index=index: toggle_pause(index))
        cancel_button = ttk.Button(
            progress_frame,
            text="Cancel",
            style="White.TButton",
            command=lambda index=index: cancel(index),
        )
        pause_button.grid(row=2, column=2, padx=5, pady=5, sticky="e")
        cancel_button.grid(row=2, column=3, padx=5, pady=5, sticky="e")
        progress_frame.grid_columnconfigure(0, weight=1)
        ui_list[index] = {
            "frame": progress_frame,
            "progress": progress_bar,
            "pause": pause_button,
            "cancel": cancel_button,
        }
        manager.add_file(*(file_list[index]))
        index += 1

    pause_all_button = ttk.Button(
        btn_frame, text="Pause", style="White.TButton", command=pause_all
    )
    pause_all_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    cancel_all_button = ttk.Button(
        btn_frame, text="Cancel", style="White.TButton", command=cancel_all
    )
    cancel_all_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    download_popup.update_idletasks()
    width = download_popup.winfo_width() + 330
    height = download_popup.winfo_height() + 140
    rootWidth = window.winfo_width()
    rootHeight = window.winfo_height()
    rootX = window.winfo_x()
    rootY = window.winfo_y()
    x = rootX + (rootWidth // 2) - (width // 2)
    y = rootY + (rootHeight // 2) - (height // 2)
    download_popup.geometry(f"{width}x{height}+{x}+{y}")
    download_popup.update_idletasks()
    download_popup.protocol("WM_DELETE_WINDOW", cancel_all)
    for i in range(THREAD + 2):
        add_next_file()
    manager.start()

    window.wait_window(download_popup)


def download():
    if not treeview.selection():
        return
    download_dir = tkinter.filedialog.askdirectory()
    if not download_dir:
        return
    download_set = set()
    download_list = []

    def download_siever(item, parent=download_dir):
        if item["path"] not in download_set:
            download_set.add(item["path"])
            local_path = os.path.normpath(os.path.join(parent, item["name"]))
            if os.path.exists(local_path):
                unique_path = get_unique_filepath(local_path, os.path.exists)
                prompt = tkinter.messagebox.askyesnocancel(
                    title=f"Rename, Replace or Skip ?",
                    message=f'The destination already has a {"folder" if os.path.isfile(local_path) else "file"} named "{item["name"]}".\nDo you wish to rename it to "{os.path.basename(unique_path)}"?\n(no will replace it, cancel will skip this download)',
                )
                if prompt:
                    if item["type"] == "file":
                        download_list.append((item["path"], item["size"], unique_path))
                    else:
                        os.mkdir(unique_path)
                        for child in item.get("children", []):
                            download_siever(child, unique_path)
                elif prompt == False:
                    if item["type"] == "file":
                        os.remove(local_path)
                        download_list.append((item["path"], item["size"], local_path))
                    else:
                        shutil.rmtree(local_path)
                        os.mkdir(local_path)
                        for child in item.get("children", []):
                            download_siever(child, local_path)
            else:
                if item["type"] == "file":
                    download_list.append((item["path"], item["size"], local_path))
                else:
                    os.mkdir(local_path)
                    for child in item.get("children", []):
                        download_siever(child, local_path)

    for path in treeview.selection():
        download_siever(flatten_server_directory[path])

    file_progress_ui(download_list, pro.DownloadManager)


def upload_files():
    if not treeview.selection():
        return
    file_list = tkinter.filedialog.askopenfilenames()
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
        if server_path in flatten_server_directory:
            unique_path = get_unique_filepath(
                server_path, lambda path: path in flatten_server_directory
            )
            prompt = tkinter.messagebox.askyesnocancel(
                title=f"Rename, Replace or Skip ?",
                message=f'The destination already has a {flatten_server_directory[server_path]["type"]} named "{file_name}".\nDo you wish to rename it to "{os.path.basename(unique_path)}"?\n(no will replace it, cancel will skip this download)',
            )
            if prompt:
                upload_list.append(
                    (os.path.normpath(file), os.path.getsize(file), unique_path)
                )
            elif prompt == False:
                delete_list.append(server_path)
                upload_list.append(
                    (os.path.normpath(file), os.path.getsize(file), server_path)
                )
        else:
            upload_list.append(
                (os.path.normpath(file), os.path.getsize(file), server_path)
            )
    try:
        for path in delete_list:
            management_msgr.send_DRQ(path)
        for file in upload_list:
            management_msgr.send_WRQ(file[2], file[1])
    except (OSError, MessengerError) as e:
        tkinter.messagebox.showerror("Error", str(e))
        return
    file_progress_ui(upload_list, pro.UploadManager)
    for _, _, path in upload_list:
        temp = path + ".uploading"
        if temp in flatten_server_directory:
            management_msgr.send_DRQ(temp)


def upload_folder():
    if not treeview.selection():
        return
    folder = tkinter.filedialog.askdirectory()
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
    if server_path in flatten_server_directory:
        unique_path = get_unique_filepath(
            server_path, lambda path: path in flatten_server_directory
        )
        prompt = tkinter.messagebox.askyesnocancel(
            title=f"Rename, Replace or Skip ?",
            message=f'The destination already has a {flatten_server_directory[server_path]["type"]} named "{folder_name}".\nDo you wish to rename it to "{os.path.basename(unique_path)}"?\n(no will replace it, cancel will skip this download)',
        )
        if prompt:
            make_list.append(unique_path)
            upload_siever(folder, unique_path)
        elif prompt == False:
            delete_list.append(server_path)
            make_list.append(server_path)
            upload_siever(folder, server_path)
    else:
        make_list.append(server_path)
        upload_siever(folder, server_path)

    try:
        for path in delete_list:
            management_msgr.send_DRQ(path)
        for directory in make_list:
            management_msgr.send_FRQ(directory)
        for file in upload_list:
            management_msgr.send_WRQ(file[2], file[1])
    except (OSError, MessengerError) as e:
        tkinter.messagebox.showerror("Error", str(e))
        return

    file_progress_ui(upload_list, pro.UploadManager)
    for _, _, path in upload_list:
        temp = path + ".uploading"
        if temp in flatten_server_directory:
            management_msgr.send_DRQ(temp)


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
    except (OSError, MessengerError) as e:
        if not disconnect_event.is_set():
            tkinter.messagebox.showerror("Error", str(e))
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
                    if (
                        child not in flatten_server_directory
                        or query not in child.lower()
                    ):
                        treeview.delete(child)
            for child in item.get("children", []):
                process_directory(child, query, item["path"])
        elif item["type"] == "file":
            icon_file = find_image_file(item["name"])
            if query in item["name"].lower() and not treeview.exists(item["path"]):
                treeview.insert(
                    parent,
                    0,
                    item["path"],
                    text=item["name"],
                    image=icon_file,
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
        port = int(set_port_entry.get())
    except ValueError:
        tkinter.messagebox.showerror("Error", "Please enter port number")
        return False
    if port < 0 or port > 65535:
        tkinter.messagebox.showerror("Error", "Port must be between 0 and 65535")
        return False
    return True


def apply_setting():
    try:
        thread = int(number_thread_default.get())
        segment = int(segment_size_default.get())
    except ValueError:
        tkinter.messagebox.showerror("Error", "Please enter settings correctly")
        return
    if thread < 1 or thread > 20:
        tkinter.messagebox.showerror("Error", "Connection must be between 1 and 20")
        return
    if segment < 1:
        tkinter.messagebox.showerror("Error", "Min segment size must be greater than 0")
        return
    global SEGMENT, THREAD
    SEGMENT = segment
    THREAD = thread


def connect():
    if not validate_input():
        return
    global HOST, PORT, management_msgr
    HOST = set_ip_server_entry.get()
    PORT = int(set_port_entry.get())
    try:
        dir_msgr = Messenger(HOST, PORT)
        management_msgr = Messenger(HOST, PORT)
    except (OSError, MessengerError) as e:
        tkinter.messagebox.showerror("Error", str(e))
        return
    disconnect_event.clear()
    directory_thread = Thread(target=monitor_directory, args=(dir_msgr,), daemon=True)
    directory_thread.start()

    connect_button.configure(state="disabled")
    upload_button.configure(state="normal")
    upload_folder_button.configure(state="normal")
    download_button.configure(state="normal")
    folder_button.configure(state="normal")
    delete_button.configure(state="normal")
    disconnect_button.configure(state="normal")
    set_ip_server_entry.configure(state="disabled")
    set_port_entry.configure(state="disabled")
    search_entry.configure(state="normal")
    change_ip_sever()
    change_port_sever()


def disconnect():
    if directory_lock.locked():
        return
    disconnect_event.set()
    msg.disconnect_all()
    treeview.delete(*treeview.get_children())
    connect_button.configure(state="normal")
    upload_button.configure(state="disabled")
    upload_folder_button.configure(state="disabled")
    download_button.configure(state="disabled")
    folder_button.configure(state="disabled")
    delete_button.configure(state="disabled")
    disconnect_button.configure(state="disabled")
    set_ip_server_entry.configure(state="normal")
    set_port_entry.configure(state="normal")
    search_entry.configure(state="disabled")


def delete():
    if not treeview.selection():
        return
    try:
        for path in treeview.selection():
            management_msgr.send_DRQ(path)
    except (OSError, MessengerError) as e:
        tkinter.messagebox.showerror("Error", str(e))


def ask_string(title, prompt):
    def on_ok():
        result.set(entry.get())
        popup.destroy()

    result = tkinter.StringVar()
    result.set(None)
    popup = tkinter.Toplevel(window)
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
    popup.transient(window)
    popup.grab_set()
    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    rootWidth = window.winfo_width()
    rootHeight = window.winfo_height()
    rootX = window.winfo_x()
    rootY = window.winfo_y()
    x = rootX + (rootWidth // 2) - (width // 2)
    y = rootY + (rootHeight // 2) - (height // 2)
    popup.geometry(f"+{x}+{y}")
    window.wait_window(popup)
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
    except (OSError, MessengerError) as e:
        tkinter.messagebox.showerror("Error", str(e))


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


file_extension = {
    "PDF": ["pdf"],
    "Text": ["txt"],
    "Picture": ["jpg", "png", "svg", "gif", "raw"],
    "Code": ["cpp", "py", "css", "html", "js", "cs", "c", "json"],
}


def find_image_file(filename):
    dot_index = filename.rfind(".")

    if dot_index == -1:
        return indefinite_image

    extension = filename[dot_index + 1 :].lower()
    for key, extensions in file_extension.items():
        if extension in extensions:
            if key == "PDF":
                return pdf_image
            elif key == "Text":
                return txt_image
            elif key == "Picture":
                return pictureFile_image
            elif key == "Code":
                return coding_image

    return indefinite_image


explorer_objects = {}

# --------------------------------------------------- // Icon - Image \\ ----------------------------------------------------
folder_image = Image.open("Image/folder.png")
folder_image = ImageTk.PhotoImage(folder_image.resize((22, 22), Image.LANCZOS))

pdf_image = Image.open("Image/pdfOnTree.png")
pdf_image = ImageTk.PhotoImage(pdf_image.resize((20, 20), Image.LANCZOS))

txt_image = Image.open("Image/txtFile.png")
txt_image = ImageTk.PhotoImage(txt_image.resize((16, 16), Image.LANCZOS))

pictureFile_image = Image.open("Image/picture.png")
pictureFile_image = ImageTk.PhotoImage(
    pictureFile_image.resize((20, 20), Image.LANCZOS)
)

coding_image = Image.open("Image/coding.png")
coding_image = ImageTk.PhotoImage(coding_image.resize((24, 24), Image.LANCZOS))

indefinite_image = Image.open("Image/new-document.png")
indefinite_image = ImageTk.PhotoImage(indefinite_image.resize((24, 24), Image.LANCZOS))

recycle_bin_icon = Image.open("Image/recycle-bin.png")
recycle_bin_icon = customtkinter.CTkImage(
    recycle_bin_icon.resize((22, 22), Image.LANCZOS)
)

new_folder_icon = Image.open("Image/new-folder.png")
new_folder_icon = customtkinter.CTkImage(
    new_folder_icon.resize((24, 24), Image.LANCZOS)
)

download_file_icon = Image.open("Image/download.png")
download_file_icon = customtkinter.CTkImage(
    download_file_icon.resize((24, 24), Image.LANCZOS)
)

upload_file_icon = Image.open("Image/upload_file.png")
upload_file_icon = customtkinter.CTkImage(
    upload_file_icon.resize((24, 24), Image.LANCZOS)
)

upload_folder_icon = Image.open("Image/upload_folder.png")
upload_folder_icon = customtkinter.CTkImage(
    upload_folder_icon.resize((24, 24), Image.LANCZOS)
)

search_icon = Image.open("Image/search.png")
search_icon = customtkinter.CTkImage(search_icon.resize((24, 24), Image.LANCZOS))

# ---------------------------------------------- // Frame \\ -----------------------------------------------------
style = ttk.Style(explorer_frame)

main_frame = customtkinter.CTkFrame(explorer_frame, fg_color="white")
tool_frame = customtkinter.CTkFrame(main_frame, fg_color="white", height=75)
dir_frame = customtkinter.CTkFrame(main_frame, fg_color="white")
main_frame.grid(row=0, column=0, sticky="nwes")
tool_frame.grid(row=0, column=0, stick="nwes")
dir_frame.grid(row=1, column=0, sticky="nwes")

# Popup
popup = Menu(explorer_frame, tearoff=0)
popup.add_command(label="Delete", command=delete)
popup.add_command(label="New folder", command=folder)
popup.add_command(label="Download", command=download)
popup.add_command(label="Upload file", command=upload_files)
popup.add_command(label="Upload folder", command=upload_folder)


# ---------------------------------------------- // Object \\ -----------------------------------------------------
# customtkinter.CTkLabel(tool_frame, text="Server's Directory", font=customtkinter.CTkFont(weight="bold", size=18)).grid(row=0, column=0, stick="we")

""" FUNCTION BUTTONS """
delete_button = customtkinter.CTkButton(
    tool_frame,
    text="Delete",
    state="normal",
    image=recycle_bin_icon,
    fg_color="white",
    text_color="black",
    width=25,
    hover_color="#CCFFFF",
    command=delete,
)


folder_button = customtkinter.CTkButton(
    tool_frame,
    text="New folder",
    image=new_folder_icon,
    fg_color="white",
    text_color="black",
    state="normal",
    width=25,
    hover_color="#CCFFFF",
    command=folder,
)

download_button = customtkinter.CTkButton(
    tool_frame,
    text="Download",
    width=25,
    state="normal",
    text_color="black",
    fg_color="white",
    image=download_file_icon,
    hover_color="#CCFFFF",
    command=download,
)

upload_button = customtkinter.CTkButton(
    tool_frame,
    text="Upload file",
    fg_color="white",
    text_color="black",
    image=upload_file_icon,
    width=25,
    state="normal",
    hover_color="#CCFFFF",
    command=upload_files,
)

upload_folder_button = customtkinter.CTkButton(
    tool_frame,
    text="Upload folder",
    fg_color="white",
    text_color="black",
    image=upload_folder_icon,
    width=25,
    state="normal",
    hover_color="#CCFFFF",
    command=upload_folder,
)


""" SEARCH """
search_icon = customtkinter.CTkLabel(tool_frame, image=search_icon, text="")
search_var = customtkinter.StringVar()
search_var.trace("w", search_dir)
search_entry = customtkinter.CTkEntry(
    tool_frame,
    placeholder_text="Search file",
    textvariable=search_var,
    width=300,
    height=25,
    corner_radius=9,
    font=("", 14),
)

delete_button.grid(row=0, column=0, padx=4, pady=4, sticky="w")
folder_button.grid(row=0, column=1, padx=4, pady=4, sticky="w")
download_button.grid(row=0, column=2, padx=4, pady=4, sticky="w")
upload_button.grid(row=0, column=3, padx=4, pady=4, sticky="w")
upload_folder_button.grid(row=0, column=4, padx=4, pady=4, sticky="w")
search_icon.grid(row=0, column=5, padx=4, pady=4, sticky="e")
search_entry.grid(row=0, column=6, padx=(0, 50), pady=4, sticky="e")
""" TREE STYLE CONFIG """
style = ttk.Style()
style.configure("Treeview", font=("", 12), rowheight=29)
style.configure("Treeview.Heading", font=customtkinter.CTkFont(weight="bold", size=11))
style.map(
    "Treeview",
    background=[("selected", "#99FFFF")],
    foreground=[("selected", "black")],
)


# Create a new style for the Treeview
style = ttk.Style()

treeview = ttk.Treeview(dir_frame, style="Treeview", height=21)
treeview["columns"] = ("mtime", "size")
treeview.column("#0", width=400, anchor="w")
treeview.column("mtime", width=300, anchor="w")
treeview.column("size", width=100, anchor="w")
treeview.heading("#0", text="Name", anchor="w")
treeview.heading("mtime", text="Date modified", anchor="w")
treeview.heading("size", text="Size", anchor="w")
treeview.bind("<Motion>", highlight_row)
treeview.bind("<Button-3>", popup_menu)
vsb = ttk.Scrollbar(dir_frame, orient="vertical", command=treeview.yview)
treeview.configure(yscrollcommand=vsb.set)
treeview.tag_configure("highlight", background="#CCFFFF")


treeview.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, padx=(0, 57), sticky="ns")

explorer_frame.grid_columnconfigure(0, weight=1)
explorer_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
tool_frame.grid_columnconfigure(5, weight=1)
dir_frame.grid_rowconfigure(0, weight=1)
dir_frame.grid_columnconfigure(0, weight=1)


# region Setting
IP_server_default = customtkinter.StringVar(value="127.0.0.1")
port_default = customtkinter.StringVar(value="8888")
number_thread_default = customtkinter.StringVar(value="8")
segment_size_default = customtkinter.StringVar(value="65536")


# -------------------------------------// Function \\ -------------------------------------
def change_port_sever(event=None):
    port_label.configure(text=f"Port: {set_port_entry.get()}")


def change_ip_sever(event=None):
    ip_server.configure(text=f"IP: {set_ip_server_entry.get()}")


# -------------------------------------// Frame \\ -------------------------------------
setting_frame.columnconfigure(0, weight=1)
setting_frame.rowconfigure(0, weight=1)
setting_frame.rowconfigure(1, weight=1)

server_information_frame = customtkinter.CTkFrame(setting_frame, fg_color="#DAE8FC")
server_information_frame.grid(row=0, column=0, padx=(6, 52), pady=(6, 3), sticky="swne")

client_information_frame = customtkinter.CTkFrame(setting_frame, fg_color="#D5E8D4")
client_information_frame.grid(row=1, column=0, padx=(6, 52), pady=(3, 6), sticky="swne")

# -------------------------------------// Image \\ -------------------------------------
server_image = customtkinter.CTkImage(
    dark_image=Image.open("Image/sever.png"),
    light_image=Image.open("Image/sever.png"),
    size=(175, 150),
)
client_Image = customtkinter.CTkImage(
    dark_image=Image.open("Image/computer.png"),
    light_image=Image.open("Image/computer.png"),
    size=(175, 150),
)
# -------------------------------------// Object \\ -------------------------------------
""" ENTRY PORT, IP OF SERVER """

"===========================================================<SERVER FRAME>==========================================================="
text_server_info = customtkinter.CTkLabel(
    server_information_frame, text="Server Info", font=("Bold", 25)
)

server_ip_frame = customtkinter.CTkFrame(
    server_information_frame, fg_color="transparent"
)

server_port_frame = customtkinter.CTkFrame(
    server_information_frame, fg_color="transparent"
)

set_port_entry = customtkinter.CTkEntry(
    server_port_frame,
    width=250,
    font=("Helvetica", 18),
    textvariable=port_default,
)
set_port_entry.bind("<Return>", change_port_sever)

port_server = customtkinter.CTkLabel(
    server_information_frame,
    text=f"Port: {set_port_entry.get()}",
    font=("Helvetica", 15),
)

set_ip_server_entry = customtkinter.CTkEntry(
    server_ip_frame, width=250, font=("Helvetica", 18), textvariable=IP_server_default
)
set_ip_server_entry.bind("<Return>", change_ip_sever)

ip_server = customtkinter.CTkLabel(
    server_information_frame,
    text=f"IP: {set_ip_server_entry.get()}",
    font=("Helvetica", 15),
)
port_label = customtkinter.CTkLabel(
    server_port_frame,
    text="Set Port",
    font=customtkinter.CTkFont(weight="bold", size=18),
)

ip_label = customtkinter.CTkLabel(
    server_ip_frame,
    text="Set IP Server",
    font=customtkinter.CTkFont(weight="bold", size=18),
)

server_information_frame.rowconfigure(0, weight=1)
server_information_frame.rowconfigure(1, weight=2)
server_information_frame.rowconfigure(2, weight=2)
server_information_frame.columnconfigure(3, weight=1)
server_ip_frame.grid(row=1, column=2, pady=3, stick="swne")
server_port_frame.grid(row=2, column=2, pady=3, stick="swne")

text_server_info.grid(row=0, column=0, padx=(80, 50), pady=0, sticky="s")
customtkinter.CTkLabel(server_information_frame, image=server_image, text="").grid(
    row=1, column=0, rowspan=2, padx=(80, 50)
)
# ip_server.grid(row=1,column=1, padx = 10, )
# port_server.grid(row=2, column = 1, padx = 10)


server_port_frame.rowconfigure(0, weight=0)
server_port_frame.rowconfigure(1, weight=1)
server_ip_frame.rowconfigure(1, weight=0)
server_ip_frame.rowconfigure(0, weight=1)


ip_label.grid(row=0, column=0, padx=6, pady=3, sticky="ws")
set_ip_server_entry.grid(row=1, column=0, padx=6, pady=(9, 9), sticky="s")
port_label.grid(row=0, column=1, padx=6, pady=3, sticky="ws")
set_port_entry.grid(row=1, column=1, padx=6, pady=(3, 15), sticky="n")


"===========================================================<CLIENT FRAME>==========================================================="
text_client_info = customtkinter.CTkLabel(
    client_information_frame, text="App Setting", font=("Bold", 25)
)

segment_frame = customtkinter.CTkFrame(client_information_frame, fg_color="transparent")

thread_frame = customtkinter.CTkFrame(client_information_frame, fg_color="transparent")
number_thread_entry = customtkinter.CTkEntry(
    thread_frame,
    width=250,
    font=("Helvetica", 18),
    textvariable=number_thread_default,
)

segment_size_entry = customtkinter.CTkEntry(
    segment_frame,
    width=250,
    font=("Helvetica", 18),
    textvariable=segment_size_default,
)

segment_label = customtkinter.CTkLabel(
    segment_frame,
    text="Segment Size (Bytes)",
    font=customtkinter.CTkFont(weight="bold", size=18),
)

thread_label = customtkinter.CTkLabel(
    thread_frame,
    text="Number of Connections",
    font=customtkinter.CTkFont(weight="bold", size=18),
)

hostname_label = customtkinter.CTkLabel(
    client_information_frame, text=f"Host name: {hostname}", font=("Helvetica", 15)
)

hostip = customtkinter.CTkLabel(
    client_information_frame, text=f"Host IP: {hostip}", font=("Helvetica", 15)
)


client_information_frame.rowconfigure(0, weight=1)
client_information_frame.rowconfigure(1, weight=2)
client_information_frame.rowconfigure(2, weight=2)
client_information_frame.columnconfigure(3, weight=1)


segment_frame.grid(row=1, column=2, pady=3, stick="swne")
thread_frame.grid(row=2, column=2, pady=3, stick="swne")

text_client_info.grid(row=0, column=0, padx=(80, 50), pady=0, sticky="s")
customtkinter.CTkLabel(client_information_frame, image=client_Image, text="").grid(
    row=1, column=0, rowspan=2, padx=(80, 50)
)
# hostname_label.grid(row=1,column=1, padx = 10, )
# hostip.grid(row=2, column = 1, padx = 10)


segment_frame.rowconfigure(0, weight=1)
segment_frame.rowconfigure(1, weight=0)
thread_frame.rowconfigure(0, weight=0)
thread_frame.rowconfigure(1, weight=1)


segment_label.grid(row=0, column=0, padx=6, pady=3, sticky="ws")
segment_size_entry.grid(row=1, column=0, padx=6, pady=(9, 9), sticky="s")
thread_label.grid(row=0, column=1, padx=6, pady=3, sticky="ws")
number_thread_entry.grid(row=1, column=1, padx=6, pady=(3, 15), sticky="n")

"=========================================================== BUTTON ==========================================================="

connect_button = customtkinter.CTkButton(
    server_information_frame,
    text="Connect",
    width=130,
    font=customtkinter.CTkFont(weight="bold", size=18),
    command=connect,
)
connect_button.grid(row=1, column=3, padx=(100, 10), pady=10, sticky="sw")

disconnect_button = customtkinter.CTkButton(
    server_information_frame,
    text="Disconnect",
    width=130,
    font=customtkinter.CTkFont(weight="bold", size=18),
    command=disconnect,
)
disconnect_button.grid(row=2, column=3, padx=(100, 10), pady=10, sticky="nw")

apply_button = customtkinter.CTkButton(
    client_information_frame,
    text="Apply settings",
    width=130,
    font=customtkinter.CTkFont(weight="bold", size=18),
    command=apply_setting,
)
apply_button.grid(row=1, rowspan=2, column=3, padx=(100, 10), pady=10, sticky="w")


window.mainloop()
# endregion
