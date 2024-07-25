import customtkinter
import socket
import ipaddress
from PIL import Image

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 1000
MENU_COLLAPSED_WIDTH = 45
MENU_EXPANDED_WIDTH = 167
DELTA_WIDTH = 10


window = customtkinter.CTk()
window.title("File Transfer")
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
window.resizable(False, False)


def resize_content_frame():
     menu_width = menu_frame.cget("width")
     content_width = WINDOW_WIDTH - menu_width
     content_frame.configure(width=content_width)
     content_frame.place(relwidth=1.0, relheight=1.0, x=menu_width, y=0)

def extending_amination():
     current_width = menu_frame.cget("width")
     if current_width < MENU_EXPANDED_WIDTH:
          if current_width < (MENU_EXPANDED_WIDTH - DELTA_WIDTH):
               current_width += DELTA_WIDTH
          else:
               current_width = MENU_EXPANDED_WIDTH
          menu_frame.configure(width=current_width)
          resize_content_frame()
          window.after(ms=8, func=extending_amination)

def folding_amination():
     current_width = menu_frame.cget("width")
     if current_width > MENU_COLLAPSED_WIDTH:
          if current_width > (MENU_COLLAPSED_WIDTH + DELTA_WIDTH):
               current_width -= DELTA_WIDTH
          else:
               current_width = MENU_COLLAPSED_WIDTH
          menu_frame.configure(width=current_width)
          resize_content_frame()
          window.after(ms=8, func=folding_amination)

def extending_menu():
     extending_amination()
     toggle_button.configure(image=close_icon)
     toggle_button.configure(command=folding_menu)

def folding_menu():
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

#------------------------------ {{ MENU AREA }} ------------------------------
menu_frame = customtkinter.CTkFrame(
     window,
     height=WINDOW_HEIGHT,
     width=MENU_COLLAPSED_WIDTH,
     fg_color="lightblue"
)
menu_frame.place(relheight = 1.0, x=0, y=0)

#Tonggle Button
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


# Download Button
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

# Upload button
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

#Setting button
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


#------------------------------ {{ CONTENT AREA }} ------------------------------
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

# Download
logo_pdfFile = customtkinter.CTkImage(
     dark_image=Image.open("Image/pdfFile.png"),
     light_image=Image.open("Image/pdfFile.png"),
)

image = customtkinter.CTkLabel(
     download_frame,
     image=logo_pdfFile,
     text="aaaaaaaa",
     
)
image.place(x=10, y=10)



# Setting
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
"fuck u"
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

