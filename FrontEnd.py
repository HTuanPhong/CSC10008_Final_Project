import customtkinter
import socket
import time
from PIL import Image
from tkinter import filedialog, Menu
import os
from tkinter import messagebox

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
WIDTH_COLUMN_FILE_NAME = 180
WIDTH_COLUMN_FILE_SIZE = 75
WIDTH_COLUMN_DATE = 110
WIDTH_COLUMN_FILE_PATH = 420
WIDTH_COLUMN_STATUS = 100

upload_file_icon = customtkinter.CTkImage(
     dark_image=Image.open("Image/upload_file.png"), 
     light_image=Image.open("Image/upload_file.png"), 
     size=(17, 17)
)

add_icon = customtkinter.CTkImage(
     dark_image=Image.open("Image/plus.png"), 
     light_image=Image.open("Image/plus.png"), 
     size=(12, 12)
)

clear_icon_upload_list = customtkinter.CTkImage(
     dark_image=Image.open("Image/recycle-bin.png"), 
     light_image=Image.open("Image/recycle-bin.png"), 
     size=(15, 15)
)


file_dict = {}
title_frame = customtkinter.CTkFrame(upload_frame, corner_radius=0, width=920, fg_color="#EEEEEE")
title_frame.place(x=10, y=65)


customtkinter.CTkLabel(
     title_frame, 
     text="File Name", 
     width=WIDTH_COLUMN_FILE_NAME,
     font=bold_font,
     anchor="w"
).grid(row=0, column=0, padx=5)

customtkinter.CTkLabel(
     title_frame, 
     text="Size", 
     font=bold_font,
     width=WIDTH_COLUMN_FILE_SIZE, 
     anchor="w"
).grid(row=0, column=1, padx=5)

customtkinter.CTkLabel(
     title_frame, 
     text="Last Update", 
     width=WIDTH_COLUMN_DATE, 
     font=bold_font,
     anchor="center"
).grid(row=0, column=2, padx=5)

customtkinter.CTkLabel(
     title_frame, 
     text="Path", 
     width=WIDTH_COLUMN_FILE_PATH, 
     font=bold_font,
     anchor="center",
     fg_color="#EEEEEE"
).grid(row=0, column=3, padx=7)

customtkinter.CTkLabel(
     title_frame, 
     text="Action", 
     width=WIDTH_COLUMN_STATUS, 
     font=bold_font,
     anchor="center",
     fg_color="#EEEEEE"
).grid(row=0, column=4, padx=5)

file_upload_scroll_frame = customtkinter.CTkScrollableFrame(upload_frame, width=920, height=280, corner_radius=0, fg_color="#EEEEEE")
file_upload_scroll_frame.place(x=10, y=90)

def truncate_text(text, max_width):
    ellipsis = "..."
    max_length = max_width // 8

    if len(text) > max_length:
        return text[:max_length - len(ellipsis)] + ellipsis
    return text

def remove_file_upload(filename):
     if filename in file_dict:
          del file_dict[filename]
          refresh_file_list()

def clear_list_upload():
     file_dict.clear()
     refresh_file_list()

def uploadFile(server_address, client_path, server_path):
     pass

def refresh_file_list():
     for widget in file_upload_scroll_frame.winfo_children():
          widget.destroy()
        
     for idx, (filename, info) in enumerate(file_dict.items()):
          file_name_truncated = truncate_text(filename, WIDTH_COLUMN_FILE_NAME)
          file_name_label = customtkinter.CTkLabel(
               file_upload_scroll_frame, 
               text=file_name_truncated, 
               width=WIDTH_COLUMN_FILE_NAME, 
               anchor="w", 
               font=("", 15),
               fg_color="#EEEEEE"
          )
          file_name_label.grid(row=idx, column=0, sticky="w", padx=5)


          size = round(float(info[0] / 1e6), 3)
          file_truncated = truncate_text(f"{size} MB", WIDTH_COLUMN_FILE_SIZE)
          size_label = customtkinter.CTkLabel(
               file_upload_scroll_frame, 
               text=file_truncated, 
               width=WIDTH_COLUMN_FILE_SIZE, 
               anchor="w", 
               font=("", 15),
               fg_color="#EEEEEE"
          )
          size_label.grid(row=idx, column=1, sticky="w", padx=5)
          

          date_truncated = truncate_text(info[1], WIDTH_COLUMN_DATE)
          date_label = customtkinter.CTkLabel(
               file_upload_scroll_frame, 
               text=date_truncated, 
               width=WIDTH_COLUMN_DATE, 
               anchor="center", 
               font=("", 15),
               fg_color="#EEEEEE"
          )
          date_label.grid(row=idx, column=2, sticky="w", padx=5)
          
          path_truncated = truncate_text(info[2], WIDTH_COLUMN_FILE_PATH)
          path_label = customtkinter.CTkLabel(
               file_upload_scroll_frame, 
               text=path_truncated, 
               width=WIDTH_COLUMN_FILE_PATH, 
               anchor="w", 
               font=("", 15),
               fg_color="#EEEEEE"
          )
          path_label.grid(row=idx, column=3, sticky="w", padx=7)
        
          remove_var = customtkinter.StringVar(value="on")
          remove_file_upload_ckeckbox = customtkinter.CTkCheckBox(
               file_upload_scroll_frame,
               text="",
               variable=remove_var,
               checkbox_height=17,
               checkbox_width=17,
               corner_radius=50,
               onvalue="on",
               offvalue="off",
               hover=True,
               hover_color="red",
               fg_color="green",
               command=lambda name = filename: remove_file_upload(name)
          )
          remove_file_upload_ckeckbox.grid(row=idx, column=4, padx=20)
          
          upload_current_file = customtkinter.CTkButton(
               file_upload_scroll_frame,
               text="",
               image=upload_file_icon,
               height=20, 
               width=20,
               fg_color="#EEEEEE",
               hover_color="lightblue",
               command=lambda path=info[2]: uploadFile("Default", path, "default")
          )
          upload_current_file.grid(row=idx, column=4, padx=5)
     
     info_upload.configure(text=f"Total: {len(file_dict)} files ({round(calculate_total_size(file_dict) / 1e6, 4)} MB)")

def select_files():
     file_paths = filedialog.askopenfilenames()
     # Create dictionary : {"filename": [file size, last update, path]}
     for file_path in file_paths:
          filename = os.path.basename(file_path)
          if filename in file_dict:
               messagebox.showerror("Error", "File already exists")
               continue
          
          file_size = os.path.getsize(file_path)
          last_modified_time = os.path.getmtime(file_path)
          last_modified_date = time.strftime('%Y-%m-%d', time.localtime(last_modified_time))
          file_dict[filename] = [file_size, last_modified_date, file_path]

     refresh_file_list()

def calculate_total_size(file_dict):
     total_size = 0
     for file_info in file_dict.values():
          size = file_info[0]  
          total_size += size
     return total_size

add_file_upload_button = customtkinter.CTkButton(
     upload_frame, image=add_icon, 
     text="Add file", 
     font=("", 14),
     width=22,
     fg_color="lightblue", 
     text_color="black",
     hover_color="#6699FF",
     command=select_files
)
add_file_upload_button.place(x=770, y = 35)

clear_file_upload_button = customtkinter.CTkButton(
     upload_frame, 
     text="Clear",
     image=clear_icon_upload_list, 
     font=("", 14),
     width=22,
     fg_color="lightblue", 
     text_color="black",
     hover_color="#6699FF",
     command=clear_list_upload
)
clear_file_upload_button.place(x=870, y = 35)

bold_font_lv1 = customtkinter.CTkFont(weight="bold", size=21)
customtkinter.CTkLabel(upload_frame, text="List upload file", font=bold_font_lv1).place(x= 10, y = 35)

upload_all = customtkinter.CTkButton(
     upload_frame,
     text="Upload all file",
     font= customtkinter.CTkFont(weight="bold", size=18)

)
upload_all.place(x=400, y = 460)


info_upload = customtkinter.CTkLabel(
     upload_frame,
     text=f"Total: {len(file_dict)} files ({round(calculate_total_size(file_dict) / 1e6, 4)} MB)",
     font=bold_font
)
info_upload.place(x=10, y=370)

#endregion


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

port_list = ["1234", "8888"]
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
set_port_combobox.place(x=50, y=350)

text_set_port = customtkinter.CTkLabel(setting_frame, text="Set Port", font=("Bold", 25))
text_set_port.place(x=50, y=300)

ip_sever_list = ["1.2.3.4", "5.4.3.2", "123.123.123.123"]
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

text_set_ip_sever = customtkinter.CTkLabel(setting_frame, text="Set IP Sever", font=("Bold", 25))
text_set_ip_sever.place(x=470, y=300)

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

window.mainloop()
#endregion
