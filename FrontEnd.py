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

import warnings
warnings.filterwarnings("ignore", message=".*Given image is not CTkImage.*")

HOST = None
PORT = None
disconnect_event = threading.Event()
directory_lock = threading.Lock()
server_directory = {}
flatten_server_directory = {}
management_msgr = None
hostname = socket.gethostname()
hostip = socket.gethostbyname(hostname)

#============================================================={{ configure WINDOW }}===========================================================
# Set mode and default theme
customtkinter.set_appearance_mode("System")
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
window.resizable(False, False)
bold_font = customtkinter.CTkFont(weight="bold", size=14)

#============================================================={{ MENU }}===========================================================
#region Expand/Collapse Function
# --------------------------------------------------// Image - Icon \\ --------------------------------------------------
toggle_icon = customtkinter.CTkImage(dark_image=Image.open("Image/menu.png"), light_image=Image.open("Image/menu.png"), size=(20, 20))
close_icon = customtkinter.CTkImage(dark_image=Image.open("Image/close.png"), light_image=Image.open("Image/close.png"), size=(18, 18))

# --------------------------------------------------// Function \\ --------------------------------------------------
ANIMATION_DELAY = 8 #ms
def update_content_frame(menu_width):
     content_width = WINDOW_WIDTH - menu_width
     content_frame.configure(width=content_width)
     content_frame.place(relwidth=1.0, relheight=1.0, x=menu_width, y=0)

def update_menu_frame(width: int):
     menu_frame.configure(width = width)
     explorer_icon_button.configure(width = width - 2)
     setting_icon_button.configure(width = width - 2)
    #  progress_icon_button.configure(width = width - 2)

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
               window.after(
                    ms = max(8 - currentTime, 0),
                    func=extending_amination
               )

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
               window.after(
                    ms = max(8 - currentTime, 0), 
                    func=folding_amination
               )

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
    #  progress_indicate.configure(fg_color="lightblue")

     explorer_icon_button.configure(fg_color="lightblue")
     setting_icon_button.configure(fg_color="lightblue")
    #  progress_icon_button.configure(fg_color="lightblue")

def raise_frame(frame):
    frame.tkraise()

# --------------------------------------------------// Frame \\ --------------------------------------------------
menu_frame = customtkinter.CTkFrame(
     window,
     height=WINDOW_HEIGHT,
     width=MENU_COLLAPSED_WIDTH,
     fg_color="lightblue"
)
menu_frame.place(relheight = 1.0, x=0, y=0)

content_frame = customtkinter.CTkFrame(
     window,
     fg_color="white",
     height=WINDOW_HEIGHT,
     width=WINDOW_WIDTH-MENU_COLLAPSED_WIDTH
)
content_frame.place(relwidth=1.0, relheight=1.0, x=MENU_COLLAPSED_WIDTH, y=0)

explorer_frame = customtkinter.CTkFrame(content_frame, fg_color="white")
explorer_frame.place(relwidth=1.0, relheight=1.0)

setting_frame = customtkinter.CTkFrame(content_frame, fg_color="white")
setting_frame.place(relwidth=1.0, relheight=1.0)

# progress_frame = customtkinter.CTkFrame(content_frame, fg_color="white")
# progress_frame.place(relwidth=1.0, relheight=1.0)

# --------------------------------------------------// Object \\ --------------------------------------------------
is_folding = False
toggle_button = customtkinter.CTkButton(
     menu_frame,
     image=toggle_icon,
     width=10,
     fg_color="lightblue",
     hover_color="#CCFFFF",
     text="",
     command=extending_menu
)
toggle_button.place(x=5, y=10)

#endregion


#region Pape
# --------------------------------------------------// Image - Icon \\ --------------------------------------------------
explorer_icon = customtkinter.CTkImage(dark_image=Image.open("Image/explorer.png"), light_image=Image.open("Image/explorer.png"), size=(25, 25))
setting_icon = customtkinter.CTkImage(dark_image=Image.open("Image/setting-lines.png"), light_image=Image.open("Image/setting-lines.png"), size=(25, 25))
# progress_icon = customtkinter.CTkImage(dark_image= Image.open("Image/loading-bar.png"), light_image=Image.open("Image/loading-bar.png"), size=(27, 27))

# --------------------------------------------------// Function \\ --------------------------------------------------
# Explorer
def indicate_explorer():
     deactivate()
     explorer_indicate.configure(fg_color="#0033FF")
     explorer_icon_button.configure(fg_color="#CCFFFF")

     if menu_frame.cget("width") > 45:
          folding_menu()
     
     raise_frame(explorer_frame)

# Setting
def indicate_setting():
     deactivate()
     setting_indicate.configure(fg_color="#0033FF")
     setting_icon_button.configure(fg_color="#CCFFFF")

     if menu_frame.cget("width") > 45:
          folding_menu()
     
     raise_frame(setting_frame)


# Progress
# def indicate_progress():
#      deactivate()
#      progress_indicate.configure(fg_color="#0033FF")
#      progress_icon_button.configure(fg_color="#CCFFFF")

#      if menu_frame.cget("width") > 45:
#           folding_menu()
     
#      raise_frame(progress_frame)

# --------------------------------------------------// Object \\ --------------------------------------------------
# Explorer
explorer_icon_button = customtkinter.CTkButton(
     menu_frame,
     image=explorer_icon,
     width=165,
     height=32,
     fg_color="lightblue",
     hover_color="#CCFFFF",
     text=" Upload",
     font=("Helvetica", 18),
     text_color="black",
     anchor="w",
     command=indicate_explorer
)
explorer_icon_button.place(x=1, y=100)

explorer_indicate = customtkinter.CTkLabel(
     menu_frame,
     text=" ",
     fg_color="#0033FF",
     height=31,
     bg_color="lightblue"
)
explorer_indicate.place(x=0, y=100)

# Setting 
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
     command=indicate_setting
)
setting_icon_button.place(x=1, y=150)

setting_indicate = customtkinter.CTkLabel(
     menu_frame,
     text=" ",
     fg_color="lightblue",
     height=31,
     bg_color="lightblue"
)
setting_indicate.place(x=0, y=150)

# Progress
# progress_icon_button = customtkinter.CTkButton(
#      menu_frame,
#      image=progress_icon,
#      width=165,
#      height=32,
#      fg_color="lightblue",
#      hover_color="#CCFFFF",
#      text=" Progress",
#      font=("Helvetica", 18),
#      text_color="black",
#      anchor="w",
#      command=indicate_progress
# )
# progress_icon_button.place(x=1, y=200)

# progress_indicate = customtkinter.CTkLabel(
#      menu_frame,
#      text=" ",
#      fg_color="lightblue",
#      height=31,
#      bg_color="lightblue"
# )
# progress_indicate.place(x=0, y=200)

#endregion

raise_frame(explorer_frame)

#region Explorer
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
    download_popup.title("Download process")

    btn_frame = ttk.Labelframe(download_popup, text="Button for all files:", style="White.TLabelframe")
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

    def update_progress(index, bytes):
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
                pause_button.configure(text="Resume")
            else:
                manager.resume_file(index)
                pause_button.configure(text="Pause")

    def toggle_pause_all():
        with ui_lock:
            if pause_all_button["text"] == "Pause":
                for index, ui in ui_list.items():
                    if ui["pause"]["text"] == "Pause":
                        manager.pause_file(index)
                        ui["pause"].configure(text="Resume")
                pause_all_button.configure(text="Resume")
            else:
                for index, ui in ui_list.items():
                    if ui["pause"]["text"] == "Resume":
                        manager.resume_file(index)
                        ui["pause"].configure(text="Pause")
                pause_all_button.configure(text="Pause")
    def cancel_all_thread():
        manager.stop()
        canvas.unbind_all("<MouseWheel>")
        download_popup.destroy()

    def cancel_all():
        t = threading.Thread(target=cancel_all_thread, daemon=True)
        t.start()

    ui_list = {}
    for i, file in enumerate(file_list):
        progress_frame = ttk.Labelframe(scrollable_frame, text="From: " + file[0], style="White.TLabelframe")
        progress_frame.grid(row=i, column=0, pady=5, padx=10, sticky="ew")
        des_label = ttk.Label(progress_frame, text="To: " + file[2], style="White.TLabel")
        des_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        progress_bar = ttk.Progressbar(
            progress_frame, maximum=file[1] + 1, mode="determinate"
        )
        progress_bar.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        total_label = ttk.Label(progress_frame, text="Total: " + format_bytes(file[1]), style="White.TLabel")
        total_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        pause_button = ttk.Button(progress_frame, text="Pause", style="White.TButton")
        pause_button.configure(command=lambda index=i: toggle_pause(index))
        cancel_button = ttk.Button(
            progress_frame,
            text="Cancel",
            style="White.TButton",
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

    pause_all_button = ttk.Button(btn_frame, text="Pause", style="White.TButton", command=toggle_pause_all)
    pause_all_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    cancel_all_button = ttk.Button(btn_frame, text="Cancel", style="White.TButton", command=cancel_all)
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
    manager.add_files(file_list)
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

    # def download_siever(item, parent=download_dir):
    #     if item["path"] not in download_set:
    #         download_set.add(item["path"])
    #         local_path = os.path.normpath(os.path.join(parent, item["name"]))
    #         file_exist = os.path.exists(local_path)
    #         if not file_exist or tkinter.messagebox.askyesno(
    #             title=f'Replace or Skip {item["type"]}',
    #             message=f'The destination already has a {"folder" if os.path.isfile(local_path) else "file"} named "{item["name"]}".\nDo you wish to replace it? (no will skip it.)',
    #         ):  # short-circuit logic
    #             if item["type"] == "file":
    #                 if file_exist:
    #                     os.remove(local_path)
    #                 download_list.append((item["path"], item["size"], local_path))
    #             else:
    #                 if file_exist:
    #                     shutil.rmtree(local_path)
    #                 os.mkdir(local_path)
    #                 for child in item.get("children", []):
    #                     download_siever(child, local_path)

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


# def upload_files():
#     if not treeview.selection():
#         return
#     file_list = tkinter.filedialog.askopenfilenames()
#     if not file_list:
#         return
#     destination = treeview.selection()[0]
#     if flatten_server_directory[destination]["type"] == "file":
#         destination = os.path.dirname(destination)
#     upload_list = []
#     delete_list = []
#     for file in file_list:
#         file_name = os.path.basename(file)
#         server_path = os.path.normpath(os.path.join(destination, file_name))
#         file_exist = server_path in flatten_server_directory
#         if not file_exist or tkinter.messagebox.askyesno(
#             title=f"Replace or Skip file",
#             message=f'The destination already has a {flatten_server_directory[server_path]["type"]} named "{file_name}".\nDo you wish to replace it? (no will skip it.)',
#         ):
#             if file_exist:
#                 delete_list.append(server_path)
#             upload_list.append(
#                 (os.path.normpath(file), os.path.getsize(file), server_path)
#             )
#     try:
#         for path in delete_list:
#             management_msgr.send_DRQ(path)
#         for file in upload_list:
#             management_msgr.send_WRQ(file[2], file[1])
#     except (OSError, MessengerError) as e:
#         tkinter.messagebox.showerror("Error", str(e))
#         return
#     file_progress_ui(upload_list, pro.UploadManager)


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


# def upload_folder():
#     if not treeview.selection():
#         return
#     folder = tkinter.filedialog.askdirectory()
#     if not folder:
#         return
#     destination = treeview.selection()[0]
#     if flatten_server_directory[destination]["type"] == "file":
#         destination = os.path.dirname(destination)
#     upload_list = []
#     delete_list = []
#     make_list = []

#     def upload_siever(root_dir, current_path):
#         with os.scandir(root_dir) as it:
#             for entry in it:
#                 server_path = os.path.join(current_path, entry.name)
#                 if not entry.is_dir(follow_symlinks=False):
#                     upload_list.append(
#                         (
#                             # python module maker need to agree on the path like tkinter give / os.path give \\ scandir path give / MAKE UP UR MIND!
#                             os.path.normpath(entry.path),
#                             entry.stat().st_size,
#                             server_path,
#                         )
#                     )
#                 else:
#                     make_list.append(server_path)
#                     upload_siever(entry.path, server_path)

#     folder_name = os.path.basename(folder)
#     server_path = os.path.normpath(os.path.join(destination, folder_name))
#     entry_exist = server_path in flatten_server_directory
#     if not entry_exist or tkinter.messagebox.askyesno(
#         title=f"Replace or Skip folder",
#         message=f'The destination already has a {flatten_server_directory[server_path]["type"]} named "{folder_name}".\nDo you wish to replace it? (no will skip it.)',
#     ):
#         if entry_exist:
#             delete_list.append(server_path)
#         make_list.append(server_path)
#         upload_siever(folder, server_path)
#     try:
#         for path in delete_list:
#             management_msgr.send_DRQ(path)
#         for directory in make_list:
#             management_msgr.send_FRQ(directory)
#         for file in upload_list:
#             management_msgr.send_WRQ(file[2], file[1])
#     except (OSError, MessengerError) as e:
#         tkinter.messagebox.showerror("Error", str(e))
#         return

#     file_progress_ui(upload_list, pro.UploadManager)


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
                    if child not in flatten_server_directory or query not in child:
                        treeview.delete(child)
            for child in item.get("children", []):
                process_directory(child, query, item["path"])
        elif item["type"] == "file":
            icon_file = find_icon_file(item["name"]) 
            if query in item["name"] and not treeview.exists(item["path"]):
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
def find_icon_file(filename):
     dot_index = filename.rfind('.')
     
     if dot_index == -1:
          return indefinite_icon

     extension = filename[dot_index + 1:].lower()
     for key, extensions in file_extension.items():
          if extension in extensions:
               if key == "PDF":
                    return pdf_image
               elif key == "Text":
                    return txt_image
               elif key == "Picture":
                    return pictureFile_image
               elif key == "Code":
                    return coding_icon
     
     return indefinite_icon



explorer_objects = {}

# --------------------------------------------------- // Icon - Image \\ ----------------------------------------------------
folder_image = Image.open("Image/folder.png")  
folder_image = ImageTk.PhotoImage(folder_image.resize((22, 22), Image.LANCZOS))

pdf_image = Image.open("Image/pdfOnTree.png")  
pdf_image = ImageTk.PhotoImage(pdf_image.resize((20, 20), Image.LANCZOS))

txt_image = Image.open("Image/txtFile.png")  
txt_image = ImageTk.PhotoImage(txt_image.resize((16, 16), Image.LANCZOS))

pictureFile_image = Image.open("Image/picture.png")  
pictureFile_image = ImageTk.PhotoImage(pictureFile_image.resize((20, 20), Image.LANCZOS))

recycle_bin_icon = Image.open("Image/recycle-bin.png")  
recycle_bin_icon = ImageTk.PhotoImage(recycle_bin_icon.resize((22, 22), Image.LANCZOS))

new_folder_icon = Image.open("Image/new-folder.png")  
new_folder_icon = ImageTk.PhotoImage(new_folder_icon.resize((24, 24), Image.LANCZOS))

download_file_icon = Image.open("Image/download.png")  
download_file_icon = ImageTk.PhotoImage(download_file_icon.resize((24, 24), Image.LANCZOS))

upload_file_icon = Image.open("Image/upload_file.png")  
upload_file_icon = ImageTk.PhotoImage(upload_file_icon.resize((24, 24), Image.LANCZOS))

upload_folder_icon = Image.open("Image/upload_folder.png")  
upload_folder_icon = ImageTk.PhotoImage(upload_folder_icon.resize((24, 24), Image.LANCZOS))

coding_icon = Image.open("Image/coding.png")  
coding_icon = ImageTk.PhotoImage(coding_icon.resize((24, 24), Image.LANCZOS))

indefinite_icon = Image.open("Image/new-document.png")  
indefinite_icon = ImageTk.PhotoImage(indefinite_icon.resize((24, 24), Image.LANCZOS))

search_icon = Image.open("Image/search.png")  
search_icon = ImageTk.PhotoImage(search_icon.resize((24, 24), Image.LANCZOS))

# ---------------------------------------------- // Frame \\ -----------------------------------------------------
style = ttk.Style(explorer_frame)

main_frame = customtkinter.CTkFrame(explorer_frame, fg_color="white")
tool_frame = customtkinter.CTkFrame(main_frame, fg_color="white", height=75)
dir_frame = customtkinter.CTkFrame(main_frame, width=1000, height=600, fg_color="white")
dir_frame.place(x=1, y=75)
tool_frame.place(x=1, y=0)
main_frame.grid(row=0, column=0, sticky="nwes")
tool_frame.grid(row=0, column=0, stick="nwes")

# Popup
popup = Menu(explorer_frame, tearoff=0)
popup.add_command(label="Delete", command=delete)
popup.add_command(label="New folder", command=folder)
popup.add_command(label="Download", command=download)
popup.add_command(label="Upload file", command=upload_files)
popup.add_command(label="Upload folder", command=upload_folder)


# ---------------------------------------------- // Object \\ -----------------------------------------------------
customtkinter.CTkLabel(tool_frame, text="Server's Directory", font=customtkinter.CTkFont(weight="bold", size=18)).place(x=3, y=3)

""" FUNCTION BUTTONS """
delete_button = customtkinter.CTkButton(
    tool_frame, text="", 
    state="normal", 
    image=recycle_bin_icon,
    fg_color="white",
    font=("", 25),
    width=25,
    hover_color="#CCFFFF",
    command=delete
)
delete_button.place(x=280, y=42)


folder_button = customtkinter.CTkButton(
    tool_frame, 
    text="New folder", 
    image=new_folder_icon,
    fg_color="white",
    text_color="black",
    state="normal", 
    width=25,
    hover_color="#CCFFFF",
    command=folder
)
folder_button.place(x=20, y=42)

download_button = customtkinter.CTkButton(
    tool_frame, 
    text="", 
    width=25,
    state="normal", 
    fg_color="white",
    image=download_file_icon,
    hover_color="#CCFFFF",
    command=download
)
download_button.place(x=130, y=42)

upload_button = customtkinter.CTkButton(
    tool_frame, 
    text="", 
    fg_color="white",
    image=upload_file_icon,
    width=25,
    state="normal", 
    hover_color="#CCFFFF",
    command=upload_files
)
upload_button.place(x=180, y=42)

upload_folder_button = customtkinter.CTkButton(
    tool_frame, 
    text="", 
    fg_color="white",
    image=upload_folder_icon,
    width=25,
    state="normal", 
    hover_color="#CCFFFF",
    command=upload_folder
)
upload_folder_button.place(x=230, y=42)


""" SEARCH """
customtkinter.CTkLabel(tool_frame, image=search_icon, text="").place(x=610, y=42)
search_var = customtkinter.StringVar()
search_var.trace("w", search_dir)
search_entry = customtkinter.CTkEntry(
     tool_frame,
     placeholder_text="Search file",
     textvariable=search_var,
     width=300,
     height=25,
     corner_radius=9,
     font=("", 14)
)
search_entry.place(x=640, y=42)

""" TREE STYLE CONFIG """
style = ttk.Style()
style.configure("Treeview", font=("", 12), rowheight=29)
style.configure("Treeview.Heading", font=customtkinter.CTkFont(weight="bold", size=11))
style.map(
     "Treeview", 
          background=[('selected', '#99FFFF')],
          foreground=[('selected', 'black')],
     )



# Create a new style for the Treeview
style = ttk.Style()

treeview = ttk.Treeview(dir_frame, style="Treeview", height=21)
treeview["columns"] = ("mtime", "size")
treeview.column("#0", width=670, anchor="w")  
treeview.column("mtime", width=300, anchor="w")  
treeview.column("size", width=200, anchor="w")
treeview.heading("#0", text="Name", anchor="w")
treeview.heading("mtime", text="Date modified", anchor="w")
treeview.heading("size", text="Size", anchor="w")
treeview.bind("<Motion>", highlight_row)
treeview.bind("<Button-3>", popup_menu)
vsb = ttk.Scrollbar(dir_frame, orient="vertical", command=treeview.yview)
treeview.configure(yscrollcommand=vsb.set)
treeview.tag_configure("highlight", background="#CCFFFF")



treeview.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")

explorer_frame.grid_columnconfigure(0, weight=1)
explorer_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
# search_frame.grid_columnconfigure(1, weight=1)
tool_frame.grid_columnconfigure(1, weight=1)
dir_frame.grid_rowconfigure(0, weight=1)
dir_frame.grid_columnconfigure(0, weight=1)



#region Setting
IP_server_default = customtkinter.StringVar(value="127.0.0.1")
port_default = customtkinter.StringVar(value="8888")

# -------------------------------------// Function \\ -------------------------------------
def change_port_sever(event=None):
    port_label.configure(text=f"Port: {set_port_entry.get()}")

def change_ip_sever(event=None):
    ip_server.configure(text=f"IP: {set_ip_server_entry.get()}")


# -------------------------------------// Frame \\ -------------------------------------
client_information_frame = customtkinter.CTkFrame(
    setting_frame,
    fg_color="white",
    width=360,
    height=200
)
client_information_frame.place(x=50, y=60)

sever_information_frame = customtkinter.CTkFrame(
    setting_frame,
    fg_color="white",
    width=360,
    height=200
)
sever_information_frame.place(x=470, y=60)

# -------------------------------------// Image \\ -------------------------------------
server_image = customtkinter.CTkImage(dark_image=Image.open("Image/sever.png"), light_image=Image.open("Image/sever.png"), size=(145, 145))
client_Image = customtkinter.CTkImage(dark_image=Image.open("Image/computer.png"), light_image=Image.open("Image/computer.png"),size=(125, 125))


# -------------------------------------// Object \\ -------------------------------------
""" ENTRY PORT, IP OF SERVER """
set_port_entry = customtkinter.CTkEntry(
    setting_frame,
    width=200,
    font=("Helvetica", 18),
    textvariable=port_default,
)
set_port_entry.place(x=50, y=430)
set_port_entry.bind("<Return>", change_port_sever)

set_ip_server_entry = customtkinter.CTkEntry(
    setting_frame,
    width=200,
    font=("Helvetica", 18),
    textvariable=IP_server_default

)
set_ip_server_entry.place(x=50, y=350)
set_ip_server_entry.bind("<Return>", change_ip_sever)


""" DISPLAY INFOMATION OF CLIENT, SERVER """
text_client_info = customtkinter.CTkLabel(setting_frame, text="Client Info", font=("Bold", 25))
text_client_info.place(x=50, y=40)
text_server_info = customtkinter.CTkLabel(setting_frame, text="Server Info", font=("Bold", 25))
text_server_info.place(x=470, y=40)

port_info = customtkinter.CTkLabel(setting_frame, text="Set Port", font=customtkinter.CTkFont(weight="bold", size=18))
port_info.place(x=50, y=402)
IP_server_Info = customtkinter.CTkLabel(setting_frame, text="Set IP Server", font=customtkinter.CTkFont(weight="bold", size=18))
IP_server_Info.place(x=50, y=322)

customtkinter.CTkLabel(sever_information_frame, image=server_image, text="").place(x=0, y=30)
customtkinter.CTkLabel(client_information_frame, image=client_Image, text="").place(x=0, y=30)

hostname_label = customtkinter.CTkLabel(client_information_frame, text=f"Host name: {hostname}", font=("Helvetica", 15))
hostname_label.place(x=140, y=30)
hostip = customtkinter.CTkLabel(client_information_frame, text=f"Host IP: {hostip}", font=("Helvetica", 15))
hostip.place(x=140, y=60)

port_label = customtkinter.CTkLabel(sever_information_frame, text=f"Port: {set_port_entry.get()}", font=("Helvetica", 15))
port_label.place(x=145, y=30)
ip_server = customtkinter.CTkLabel(sever_information_frame, text=f"IP: {set_ip_server_entry.get()}", font=("Helvetica", 15))
ip_server.place(x=145, y=60)


""" CONNECT - DISCONNECT BUTTON """
connect_button = customtkinter.CTkButton(
    setting_frame,
    text="Connect",
    width=130,
    font=customtkinter.CTkFont(weight="bold", size=18),
    command=connect,
)
connect_button.place(x=470, y=350)

disconnect_button = customtkinter.CTkButton(
    setting_frame,
    text="Disconnect",
    width=130,
    font=customtkinter.CTkFont(weight="bold", size=18),
    command=disconnect,
)
disconnect_button.place(x=470, y=400)

connect()

window.mainloop()
#endregion
