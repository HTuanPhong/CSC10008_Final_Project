import customtkinter
import tkinter
import socket
import time
from PIL import Image, ImageTk
from tkinter import filedialog, Menu
import os
from tkinter import messagebox, ttk
import threading
from threading import Thread
from modules.shared import *
from modules.message import messenger, messengerError
import modules.message as msg


# ==== Function in client.py ============================================================================================
def connect():
     pass

def disconnect():
     pass

def delete():
     pass

def folder():
     pass

def download():
     pass

def upload():
     pass
#========================================================================================================================
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
#-------------------------------------- {{ MENU AREA }} --------------------------------------
#region Expand/Collapse Function
ANIMATION_DELAY = 8 #ms
def update_content_frame(menu_width):
     content_width = WINDOW_WIDTH - menu_width
     content_frame.configure(width=content_width)
     content_frame.place(relwidth=1.0, relheight=1.0, x=menu_width, y=0)

def update_menu_frame(width: int):
     menu_frame.configure(width = width)
     download_icon_button.configure(width = width - 2)
     upload_icon_button.configure(width = width - 2)
     setting_icon_button.configure(width = width - 2)

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
     download_indicate.configure(fg_color="lightblue")
     upload_indicate.configure(fg_color="lightblue")
     setting_indicate.configure(fg_color="lightblue")

     download_icon_button.configure(fg_color="lightblue")
     upload_icon_button.configure(fg_color="lightblue")
     setting_icon_button.configure(fg_color="lightblue")

def raise_frame(frame):
    frame.tkraise()


menu_frame = customtkinter.CTkFrame(
     window,
     height=WINDOW_HEIGHT,
     width=MENU_COLLAPSED_WIDTH,
     fg_color="lightblue"
)
menu_frame.place(relheight = 1.0, x=0, y=0)


toggle_icon = customtkinter.CTkImage(
     dark_image=Image.open("Image/menu.png"),
     light_image=Image.open("Image/menu.png"),
     size=(20, 20)
)

close_icon = customtkinter.CTkImage(
     dark_image=Image.open("Image/close.png"),
     light_image=Image.open("Image/close.png"),
     size=(18, 18)
)

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

#region Download Button
def indicate_download():
     deactivate()
     download_indicate.configure(fg_color = "#0033FF")
     download_icon_button.configure(fg_color="#CCFFFF")

     if menu_frame.cget("width") > 45:
          folding_menu()
     
     raise_frame(download_frame)

download_icon = customtkinter.CTkImage(
     dark_image=Image.open("Image/download.png"),
     light_image=Image.open("Image/download.png"),
     size=(25, 25)
)

download_icon_button = customtkinter.CTkButton(
     menu_frame,
     image=download_icon,
     width=165,
     height=32,
     fg_color="#CCFFFF",
     hover_color="#CCFFFF",
     text=" Download",
     font=("Helvetica", 18),
     text_color="black",
     anchor="w",
     command=indicate_download
)
download_icon_button.place(x=1, y=100)

download_indicate = customtkinter.CTkLabel(
     menu_frame,
     text=" ",
     fg_color="#0033FF",
     height=31,
     
)
download_indicate.place(x=0, y=100)
#endregion
#region Upload button
def indicate_upload():
     deactivate()
     upload_indicate.configure(fg_color="#0033FF")
     upload_icon_button.configure(fg_color="#CCFFFF")

     if menu_frame.cget("width") > 45:
          folding_menu()
     
     raise_frame(upload_frame)

upload_icon = customtkinter.CTkImage(
     dark_image=Image.open("Image/upload.png"),
     light_image=Image.open("Image/upload.png"),
     size=(25, 25)
)

upload_icon_button = customtkinter.CTkButton(
     menu_frame,
     image=upload_icon,
     width=165,
     height=32,
     fg_color="lightblue",
     hover_color="#CCFFFF",
     text=" Upload",
     font=("Helvetica", 18),
     text_color="black",
     anchor="w",
     command=indicate_upload
)
upload_icon_button.place(x=1, y=150)

upload_indicate = customtkinter.CTkLabel(
     menu_frame,
     text=" ",
     fg_color="lightblue",
     height=31,
     bg_color="lightblue"
)
upload_indicate.place(x=0, y=150)
#endregion
#region Setting button
def indicate_setting():
     deactivate()
     setting_indicate.configure(fg_color="#0033FF")
     setting_icon_button.configure(fg_color="#CCFFFF")

     if menu_frame.cget("width") > 45:
          folding_menu()
     
     raise_frame(setting_frame)

setting_icon = customtkinter.CTkImage(
     dark_image=Image.open("Image/setting-lines.png"),
     light_image=Image.open("Image/setting-lines.png"),
     size=(25, 25)
)

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
setting_icon_button.place(x=1, y=200)

setting_indicate = customtkinter.CTkLabel(
     menu_frame,
     text=" ",
     fg_color="lightblue",
     height=31,
     bg_color="lightblue"
)
setting_indicate.place(x=0, y=200)
#endregion

#------------------------------------------ {{ CONTENT AREA }} ------------------------------------------
#region content
content_frame = customtkinter.CTkFrame(
     window,
     fg_color="white",
     height=WINDOW_HEIGHT,
     width=WINDOW_WIDTH-MENU_COLLAPSED_WIDTH
)
content_frame.place(relwidth=1.0, relheight=1.0, x=MENU_COLLAPSED_WIDTH, y=0)

download_frame = customtkinter.CTkFrame(content_frame, fg_color="white")
download_frame.place(relwidth=1.0, relheight=1.0)

upload_frame = customtkinter.CTkFrame(content_frame, fg_color="white")
upload_frame.place(relwidth=1.0, relheight=1.0)

setting_frame = customtkinter.CTkFrame(content_frame, fg_color="white")
setting_frame.place(relwidth=1.0, relheight=1.0)

raise_frame(download_frame)

# // Download Page \\
all_data = ["file1.txt", "file2.pdf", "file3.jpg", "file4.txt", "file5.txt", "file6.pdf", "file7.jpg", "file8.txt", 
            "file9.txt", "file10.pdf", "file13.jpg", "file14.txt", "file15.txt", "file16.pdf", "file17.jpg", "file18.txt", "file1.txt", "file2.pdf", "file3.jpg", "file4.txt", "file5.txt", "file6.pdf", "file7.jpg", "file8.txt", 
            "file9.txt", "file10.pdf", "file13.jpg", "file34.txt", "file15.txt", "file16.pdf", "file17.jpg", "file18.txt", "file1.txt", "file2.pdf", "file3.jpg", "file4.txt", "file5.txt", "file6.pdf", "file7.jpg", "file8.txt", 
            "file9.txt", "file10.pdf", "file13.jpg", "file24.txt", "file15.txt", "file16.pdf", "file17.jpg", "file18.txt", "file1.txt", "file2.pdf", "file3.jpg", "file4.txt", "file5.txt", "file6.pdf", "file7.jpg", "file8.txt", 
            "file9.txt", "file10.pdf", "file13.jpg", "file74.txt", "file15.txt", "file16.pdf", "file17.jpg", "file18.txt", "file1.txt", "file2.pdf", "file3.jpg", "file4.txt", "file5.txt", "file6.pdf", "file7.jpg", "file8.txt", 
            "file9.txt", "file10.pdf", "file13.jpg", "file14.txt", "file15.txt", "file16.pdf", "file17.jpg", "file18.txt", "file1.txt", "file2.pdf", "file3.jpg", "file4.txt", "file5.txt", "file6.pdf", "file7.jpg", "file8.txt", 
            "file9.txt", "file30.pdf", "file13.jpg", "file14.txt", "file15.txt", "file16.pdf", "file17.jpg", "file18.txt", "file1.txt", "file2.pdf", "file3.jpg", "file4.txt", "file5.txt", "file6.pdf", "file7.jpg", "file8.txt", 
            "file9.txt", "file50.pdf", "file13.jpg", "file14.txt", "file15.txt", "file16.pdf", "file17.jpg", "file18.txt", "file1.txt", "file2.pdf", "file3.jpg", "file4.txt", "file5.txt", "file6.pdf", "file7.jpg", "file8.txt", 
            "file9.txt", "file10.pdf", "file13.jpg", "file14.txt", "file15.txt", "file16.pdf", "file17.jpg", "file18.txt"]
selected_files = []

tool_frame = customtkinter.CTkFrame(download_frame, fg_color="white", height=60)
tool_frame.place(relwidth=1.0, x=0, y=0)

def create_file_item(filename, logofile, page_frame):
     file_button = customtkinter.CTkButton(
          page_frame, 
          height=FILE_ITEM_HEIGHT, 
          width=FILE_ITEM_WIDTH, 
          image=logofile,
          text=filename,
          compound="top",
          fg_color="white",
          text_color="black",
          hover_color="silver",
          command=lambda:add_download_list(filename)
     )
     return file_button

def filter_extension(extension, data):
     if extension == "all":
          return data
     res_fillter = []
     for item in data:
          if item.endswith(f".{extension}"):
               res_fillter.append(item)
     return res_fillter

def deactivate_extension():
     all_extension.configure(fg_color="lightblue")
     pdf_extension.configure(fg_color="lightblue")
     text_extension.configure(fg_color="lightblue")
     picture_extension.configure(fg_color="lightblue")

def indicate_page_extension(but, page_frame, scroll_frame, extension):
     deactivate_extension()
     if menu_frame.cget("width") > MENU_COLLAPSED_WIDTH:
          folding_menu()
     but.configure(fg_color="#6699FF", text_color="black")
     data = filter_extension(extension, all_data)

     displayFile(scroll_frame, data)
     raise_frame(page_frame)

def add_download_list(filename):
     if filename not in selected_files:
          selected_files.append(filename)
          display_download_list()

def display_download_list():
     for widget in list_file_selected_scroll_frame.winfo_children():
          widget.destroy()

     for file in selected_files:
          checkVar = customtkinter.StringVar(value="on")
          checbox_selected = customtkinter.CTkCheckBox(
               list_file_selected_scroll_frame,
               text=file,
               variable=checkVar,
               font=("", 18),
               checkbox_height=18,
               checkbox_width=18,
               corner_radius=50,
               onvalue="on",
               offvalue="off",
               hover=True,
               hover_color="red",
               fg_color="green",
               command=lambda f=file, v=checkVar: delete_from_download_list(f, v)
          )
          checbox_selected.pack(anchor='w', padx=10, pady=5)

def delete_from_download_list(filename, checkVar):
     if checkVar.get() == "off":
          selected_files.remove(filename)
          display_download_list()

def displayFile(page_frame, data):
     for widget in page_frame.winfo_children():
          widget.destroy()
    
     current_row = customtkinter.CTkFrame(page_frame, fg_color="white")
     current_row.pack(fill="x", padx=20, pady=10)
    
     row_width = 0
     for item in data:
          file_ext = item[-3:]
          if file_ext == 'txt':
               logofile = logo_textFile
          elif file_ext == 'pdf':
               logofile = logo_pdfFile
          elif file_ext == 'jpg':
               logofile = logo_imageFile
          else:
               continue
        
          newItem = create_file_item(item, logofile, current_row)
          newItem.pack(side="left", padx=(0, SPACE_X))
        
          row_width += (FILE_ITEM_WIDTH + SPACE_X)
          if row_width > SCROLL_FRAME_WIDTH - 90:
               current_row = customtkinter.CTkFrame(page_frame, fg_color="white")
               current_row.pack(fill="x", padx=20, pady=10)
               row_width = 0

def clear_download_list():
     selected_files.clear()
     display_download_list()

all_extension = customtkinter.CTkButton(
     tool_frame,
     text="All File",
     font=("Helvetica", 14),
     width=65,
     height=17,
     fg_color="#6699FF",
     text_color="black",
     hover_color="#6699FF",
     command=lambda: indicate_page_extension(all_extension, all_extension_frame, scroll_frame_all_extension, "all")
)
all_extension.place(x=50, y=30)


pdf_extension = customtkinter.CTkButton(
     tool_frame,
     text="PDF File",
     font=("Helvetica", 14),
     width=65,
     height=17,
     fg_color="lightblue",
     text_color="black",
     hover_color="#6699FF",
     command=lambda: indicate_page_extension(pdf_extension, pdf_extension_frame, scroll_frame_pdf_extension, "pdf")
)
pdf_extension.place(x=150, y=30)

text_extension = customtkinter.CTkButton(
     tool_frame,
     text="Text File",
     font=("Helvetica", 14),
     width=65,
     height=17,
     fg_color="lightblue",
     text_color="black",
     hover_color="#6699FF",
     command=lambda: indicate_page_extension(text_extension, text_extension_frame, scroll_frame_text_extension, "txt")
)
text_extension.place(x=250, y=30)

picture_extension = customtkinter.CTkButton(
     tool_frame,
     text="Picture",
     font=("Helvetica", 14),
     width=65,
     height=17,
     fg_color="lightblue",
     text_color="black",
     hover_color="#6699FF",
     command=lambda: indicate_page_extension(picture_extension, picture_extension_frame, scroll_frame_picture_extension, "jpg")
)
picture_extension.place(x=350, y=30)

search_box = customtkinter.CTkEntry(
     tool_frame,
     width=300,
     height=28,
     placeholder_text="Search file",
     font=("", 17)

)
search_box.place(x=450, y=30)


list_file_frame = customtkinter.CTkFrame(download_frame, fg_color="white")
list_file_frame.place(relwidth=1.0, relheight=1.0, x=0, y=60)

all_extension_frame = customtkinter.CTkFrame(
     list_file_frame, 
     fg_color="black", 
     width=SCROLL_FRAME_WIDTH + 24, 
     height=SCROLL_FRAME_HEIGHT + 15
)
all_extension_frame.place(x=0, y=0)

scroll_frame_all_extension = customtkinter.CTkScrollableFrame(
     all_extension_frame,
     height= SCROLL_FRAME_HEIGHT,
     width=SCROLL_FRAME_WIDTH,
     orientation="vertical",
     fg_color="white",
)
scroll_frame_all_extension.place(x=0, y=0)


pdf_extension_frame = customtkinter.CTkFrame(     
     list_file_frame, fg_color="black", 
     width=SCROLL_FRAME_WIDTH + 24, 
     height=SCROLL_FRAME_HEIGHT + 15
     )
pdf_extension_frame.place(x=0, y=0)

scroll_frame_pdf_extension = customtkinter.CTkScrollableFrame(
     pdf_extension_frame, 
     height= SCROLL_FRAME_HEIGHT, 
     width=SCROLL_FRAME_WIDTH,
     orientation="vertical",
     fg_color="white"
)
scroll_frame_pdf_extension.place(x=0, y=0)


text_extension_frame = customtkinter.CTkFrame(
     list_file_frame, fg_color="black", 
     width=SCROLL_FRAME_WIDTH + 24, 
     height=SCROLL_FRAME_HEIGHT + 15
)
text_extension_frame.place(x=0, y=0)

scroll_frame_text_extension = customtkinter.CTkScrollableFrame(
     text_extension_frame, 
     height= SCROLL_FRAME_HEIGHT, 
     width=SCROLL_FRAME_WIDTH,
     orientation="vertical",
     fg_color="white"
)
scroll_frame_text_extension.place(x=0, y=0)

picture_extension_frame = customtkinter.CTkFrame(
     list_file_frame, fg_color="black", 
     width=SCROLL_FRAME_WIDTH + 24, 
     height=SCROLL_FRAME_HEIGHT + 15
)
picture_extension_frame.place(x=0, y=0)

scroll_frame_picture_extension = customtkinter.CTkScrollableFrame(
     picture_extension_frame, 
     height= SCROLL_FRAME_HEIGHT, 
     width=SCROLL_FRAME_WIDTH,
     orientation="vertical",
     fg_color="white"
)
scroll_frame_picture_extension.place(x=0, y=0)


logo_pdfFile = customtkinter.CTkImage(
     dark_image=Image.open("Image/pdfFile.png"),
     light_image=Image.open("Image/pdfFile.png"),
     size=(60, 60)
)

logo_textFile = customtkinter.CTkImage(
     dark_image=Image.open("Image/txtFile.png"),
     light_image=Image.open("Image/txtFile.png"),
     size=(60, 60)
)

logo_imageFile = customtkinter.CTkImage(
     dark_image=Image.open("Image/image.png"),
     light_image=Image.open("Image/image.png"),
     size=(60, 60)
)

indicate_page_extension(all_extension, all_extension_frame, scroll_frame_all_extension, "all")

list_file_download = customtkinter.CTkFrame(
     list_file_frame,
     width=225,
     fg_color="white"
)
list_file_download.place(x=730, y=0, relheight=1.0)

list_file_selected_title = customtkinter.CTkLabel(
     list_file_download,
     text="Selected",
     font=bold_font,
     text_color="black",
)
list_file_selected_title.place(x=0, y=0)

delete_icon = customtkinter.CTkImage(
     dark_image=Image.open("Image/delete.png"),
     light_image=Image.open("Image/delete.png"),
     size=(22, 22)
)
clear_download_list_button = customtkinter.CTkButton(
     list_file_download,
     text="",
     image=delete_icon,
     font=("", 15),
     width=20,
     fg_color="white",
     hover_color="lightblue",
     command=clear_download_list
)
clear_download_list_button.place(x=175, y=0)

list_file_selected_scroll_frame = customtkinter.CTkScrollableFrame(
     list_file_download,
     fg_color="#EEEEEE",
     height=150
)
list_file_selected_scroll_frame.place(relwidth=1.0, y=35)

download_button = customtkinter.CTkButton(
     list_file_download,
     text="Download",
     font=("Bold", 20)
)
download_button.place(x=40, y=260)
#endregion

#region Upload
HOST = None
PORT = None
disconnect_event = threading.Event()
directory_lock = threading.Lock()
server_directory = {}
flatten_server_directory = {}


def download():
     if not treeview.selection():
          return
     download_dir = customtkinter.filedialog.askdirectory()
     if not download_dir:
          return
     for path in treeview.selection():
          print(path)


def upload():
     if not treeview.selection():
          return
     file_list = customtkinter.filedialog.askopenfilenames()
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
               customtkinter.messagebox.showerror("Error", str(e))
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
          port = int(set_port_combobox.get())
     except ValueError:
          customtkinter.messagebox.showerror("Error", "Please enter port number")
          return False
     if port < 0 or port > 65535:
          customtkinter.messagebox.showerror("Error", "Port must be between 0 and 65535")
          return False
     return True


def connect():
     if not validate_input():
          return
     global HOST, PORT
     HOST = set_ip_sever_combobox.get()
     PORT = int(set_port_combobox.get())
     try:
          dir_msg = messenger(HOST, PORT)
     except (OSError, msg.messengerError) as e:
          customtkinter.messagebox.showerror("Error", str(e))
          return
     disconnect_event.clear()
     directory_thread = Thread(target=monitor_directory, args=(dir_msg,), daemon=True)
     directory_thread.start()

     connect_button.configure(state="disabled")
     upload_button.configure(state="normal")
     download_button.configure(state="normal")
     folder_button.configure(state="normal")
     delete_button.configure(state="normal")
     disconnect_button.configure(state="normal")



def disconnect():
     if directory_lock.locked():
          return
     disconnect_event.set()
     msg.disconnect_all()
     treeview.delete(*treeview.get_children())
     connect_button.configure(state="normal")
     upload_button.configure(state="disabled")
     download_button.configure(state="disabled")
     folder_button.configure(state="disabled")
     delete_button.configure(state="disabled")
     disconnect_button.configure(state="disabled")



def delete():
     if not treeview.selection():
          return
     try:
          mes = messenger(HOST, PORT)
          for path in treeview.selection():
               mes.send_DRQ(path)
     except (OSError, msg.messengerError) as e:
          customtkinter.messagebox.showerror("Error", str(e))
     finally:
          mes.close()


def folder():
     if not treeview.selection():
          return
     try:
          mes = messenger(HOST, PORT)
          last_path = treeview.selection()[-1]
          name = tkinter.simpledialog.askstring("Input", "Please enter folder name:")
          if not name:
               return
          if flatten_server_directory[last_path]["type"] == "folder":
               mes.send_FRQ(os.path.join(last_path, name))
          else:
               mes.send_FRQ(os.path.join(os.path.dirname(last_path), name))
     except (OSError, msg.messengerError) as e:
          customtkinter.messagebox.showerror("Error", str(e))
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



picture_extension = ["jpg", "png", "svg", "gif", "raw"]
code_extension = ["cpp", "py", "css", "html", "js"]
file_extension = {
     "PDF": ["pdf"],
     "Text": ["txt"],
     "Picture": ["jpg", "png", "svg", "gif", "raw"],
     "Code": ["cpp", "py", "css", "html", "js", "cs", "c", "json"]
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

# Icon - Image
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

coding_icon = Image.open("Image/coding.png")  
coding_icon = ImageTk.PhotoImage(coding_icon.resize((24, 24), Image.LANCZOS))

indefinite_icon = Image.open("Image/new-document.png")  
indefinite_icon = ImageTk.PhotoImage(indefinite_icon.resize((24, 24), Image.LANCZOS))
# 
style = ttk.Style(upload_frame)

# Frame
main_frame = customtkinter.CTkFrame(upload_frame, fg_color="white")
tool_frame = customtkinter.CTkFrame(main_frame, fg_color="white", height=75)
# tool_frame.grid(row=0, column=0, padx=0, pady=0)
tool_frame.place(x=1, y=0)
dir_frame = customtkinter.CTkFrame(main_frame, width=1000, height=600, fg_color="white")
dir_frame.place(x=1, y=75)

# Popup
popup = Menu(upload_frame, tearoff=0)
popup.add_command(label="Delete", command=delete)
popup.add_command(label="Make folder", command=folder)
popup.add_command(label="Download", command=download)
popup.add_command(label="Upload", command=upload)



# host_label = ttk.Label(connection_frame, text="IPv4 host:")
# host_entry = ttk.Entry(connection_frame, width=26, state="normal")
# host_entry.insert(customtkinter.END, "127.0.0.1")
# port_label = ttk.Label(connection_frame, text="TCP port:")
# port_entry = ttk.Entry(connection_frame, width=13, state="normal")
# port_entry.insert(customtkinter.END, str(DEFAULT_SERVER_PORT))
# connect_button = ttk.Button(connection_frame, text="Connect", command=connect)
# disconnect_button = ttk.Button(
#     connection_frame, text="Disconnect", state="disabled", command=disconnect
# )
# operation_frame = ttk.Frame(tool_frame)

customtkinter.CTkLabel(tool_frame, text="Sever's Directory", font=customtkinter.CTkFont(weight="bold", size=18)).place(x=3, y=3)
delete_button = customtkinter.CTkButton(
    tool_frame, text="", 
    state="disabled", 
    image=recycle_bin_icon,
    fg_color="white",
    font=("", 25),
    width=25,
    command=delete
)
delete_button.place(x=230, y=42)

folder_button = customtkinter.CTkButton(
    tool_frame, 
    text="New folder", 
    image=new_folder_icon,
    fg_color="white",
    text_color="black",
    state="disabled", 
    width=25,
    command=folder
)
folder_button.place(x=20, y=42)

download_button = customtkinter.CTkButton(
    tool_frame, 
    text="", 
    width=25,
    state="disabled", 
    fg_color="white",
    image=download_file_icon,
    command=download
)
download_button.place(x=130, y=42)

upload_button = customtkinter.CTkButton(
    tool_frame, 
    text="", 
    fg_color="white",
    image=upload_file_icon,
    width=25,
    state="disabled", 
    command=upload
)
upload_button.place(x=180, y=42)
# search_frame = customtkinter.CTkFrame(tool_frame, fg_color="white")
search_var = customtkinter.StringVar()
search_var.trace("w", search_dir)
search_entry = customtkinter.CTkEntry(
     tool_frame,
     placeholder_text="Search file",
     textvariable=search_var,
     width=300,
     height=25,
     corner_radius=15,
     font=("", 14)
)
search_entry.place(x=640, y=42)


style = ttk.Style()
style.configure("Treeview", font=("", 12), rowheight=29)
style.configure("Treeview.Heading", font=customtkinter.CTkFont(weight="bold", size=11))
style.map(
     "Treeview", 
          background=[('selected', '#99FFFF')],
          foreground=[('selected', 'black')],
     )


treeview = ttk.Treeview(dir_frame, style="Treeview", height=21)
treeview["columns"] = ("mtime", "size")

treeview.column("#0", width=670, anchor="w")  
treeview.column("mtime", width=300, anchor="w")  
treeview.column("size", width=200, anchor="w")

treeview.heading("#0", text="Name", anchor="w")
treeview.heading("mtime", text="Date modified", anchor="w")
treeview.heading("size", text="Size", anchor="w")
treeview.bind("<Button-3>", popup_menu)
vsb = ttk.Scrollbar(dir_frame, orient="vertical", command=treeview.yview)
treeview.configure(yscrollcommand=vsb.set)


main_frame.grid(row=0, column=0, sticky="nwes")
tool_frame.grid(row=0, column=0, stick="nwes")

# search_frame.grid(row=1, column=1, sticky="w")

# search_entry.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
# host_label.grid(row=0, column=0, padx=4, pady=4, sticky="w")
# host_entry.grid(row=0, column=1, padx=4, pady=4, sticky="w")
# port_label.grid(row=0, column=2, padx=4, pady=4, sticky="w")
# port_entry.grid(row=0, column=3, padx=4, pady=4, sticky="w")
# connect_button.grid(row=0, column=4, padx=4, pady=4, sticky="w")
# disconnect_button.grid(row=0, column=5, padx=4, pady=4, sticky="w")
# operation_frame.grid(row=1, column=0, sticky="w")
# delete_button.grid(row=0, column=0, padx=4, pady=4, sticky="w")
# folder_button.grid(row=0, column=1, padx=4, pady=4, sticky="w")
# download_button.grid(row=0, column=2, padx=4, pady=4, sticky="w")
# upload_button.grid(row=0, column=3, padx=4, pady=4, sticky="w")
# dir_frame.grid(row=1, column=0, sticky="w")

treeview.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")

upload_frame.grid_columnconfigure(0, weight=1)
upload_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
# search_frame.grid_columnconfigure(1, weight=1)
tool_frame.grid_columnconfigure(1, weight=1)
dir_frame.grid_rowconfigure(0, weight=1)
dir_frame.grid_columnconfigure(0, weight=1)



#region Setting
def change_port_sever(chosent):
     port_label.configure(text=f"Port: {chosent}")

def change_ip_sever(chosent):
     ip_sever.configure(text=f"IP: {chosent}")

client_information_frame = customtkinter.CTkFrame(
     setting_frame,
     fg_color="white",
     width=360,
     height=200
)
client_information_frame.place(x=50, y=60)

text_client_info = customtkinter.CTkLabel(setting_frame, text="Client Info", font=("Bold", 25))
text_client_info.place(x=50, y=40)

sever_information_frame = customtkinter.CTkFrame(
     setting_frame,
     fg_color="white",
     width=360,
     height=200
)
sever_information_frame.place(x=470, y=60)

text_sever_info = customtkinter.CTkLabel(setting_frame, text="Sever Info", font=("Bold", 25))
text_sever_info.place(x=470, y=40)

port_list = ["8888"]
set_port_combobox = customtkinter.CTkComboBox(
     setting_frame,
     width=200,
     font=("Helvetica", 18),
     values=port_list, 
     button_color="#6699FF",
     button_hover_color="lightblue",
     dropdown_fg_color="white",
     dropdown_hover_color="#CCFFFF",
     command=change_port_sever
)
set_port_combobox.place(x=470, y=430)

text_set_port = customtkinter.CTkLabel(setting_frame, text="Set Port", font=customtkinter.CTkFont(weight="bold", size=18))
text_set_port.place(x=470, y=402)

ip_sever_list = ["127.0.0.1"]
set_ip_sever_combobox = customtkinter.CTkComboBox(
     setting_frame,
     width=200,
     font=("Helvetica", 18),
     values=ip_sever_list,
     button_color="#6699FF",
     button_hover_color="lightblue",
     dropdown_fg_color="white",
     dropdown_hover_color="#CCFFFF",
     command=change_ip_sever
)
set_ip_sever_combobox.place(x=470, y=350)

text_set_ip_sever = customtkinter.CTkLabel(setting_frame, text="Set IP Sever", font=customtkinter.CTkFont(weight="bold", size=18))
text_set_ip_sever.place(x=470, y=322)


connect_button = customtkinter.CTkButton(
     setting_frame,
     text="Connect",
     width=130,
     font=customtkinter.CTkFont(weight="bold", size=18),
     command=connect,
)
connect_button.place(x=50, y=350)
disconnect_button = customtkinter.CTkButton(
     setting_frame,
     text="Disconnect",
     width=130,
     font=customtkinter.CTkFont(weight="bold", size=18),
     command=disconnect,
)
disconnect_button.place(x=50, y=400)

client_icon = customtkinter.CTkImage(
     dark_image=Image.open("Image/computer.png"), 
     light_image=Image.open("Image/computer.png"),
     size=(125, 125)
)

client_icon_label = customtkinter.CTkLabel(client_information_frame, image=client_icon, text="")
client_icon_label.place(x=0, y=30)

hostname = socket.gethostname()
hostip = socket.gethostbyname(hostname)

hostname_label = customtkinter.CTkLabel(client_information_frame, text=f"Host name: {hostname}", font=("Helvetica", 15))
hostname_label.place(x=140, y=30)

hostip = customtkinter.CTkLabel(client_information_frame, text=f"Host IP: {hostip}", font=("Helvetica", 15))
hostip.place(x=140, y=60)

sever_icon = customtkinter.CTkImage(
     dark_image=Image.open("Image/sever.png"), 
     light_image=Image.open("Image/sever.png"),
     size=(145, 145)
)

sever_icon_label = customtkinter.CTkLabel(sever_information_frame, image=sever_icon, text="")
sever_icon_label.place(x=0, y=30)


port_label = customtkinter.CTkLabel(sever_information_frame, text=f"Port: {set_port_combobox.get()}", font=("Helvetica", 15))
port_label.place(x=145, y=30)

ip_sever = customtkinter.CTkLabel(sever_information_frame, text=f"IP: {set_ip_sever_combobox.get()}", font=("Helvetica", 15))
ip_sever.place(x=145, y=60)

# connect_button = customtkinter.CTkButton(

# )

window.mainloop()
#endregion
