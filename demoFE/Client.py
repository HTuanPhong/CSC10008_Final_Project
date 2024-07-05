import socket
import os
from tkinter import *
from tkinter import filedialog


IP = socket.gethostbyname(socket.gethostname())
PORT = 2024
ADDR = (IP, PORT)
BUFF_SIZE = 1024


def selectfile():
     global filename
     filename = filedialog.askopenfilename(
     initialdir=os.getcwd(),
     title="Select file",
     filetypes=(('file_type', '*.txt'),('all file', '*.*'))
     )

def upload():
    selectfile()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    file = open(filename, 'rb')
    data = file.read(BUFF_SIZE)
    client.send(data)
    file.close()
    client.close()


#======================================= FRONT END ==============================================
# Client functions should be written as separate functions to easily activate the button, especially the upload, list file, and download functions.
# The list file function should be designed to return a list of file names and file extensions
optWindow = Tk()
optWindow.title("USTF")
optWindow.geometry("750x460+500+200")
optWindow.configure(bg = "#ffffff")
optWindow.resizable(False, False)


def display_DownloadWindow():
     downloadWindown = Toplevel(optWindow)
     downloadWindown.title("USTF")
     downloadWindown.geometry("750x460+500+200")
     downloadWindown.configure(bg = "#ffffff")
     downloadWindown.resizable(False, False)

     image_AppIcon = PhotoImage(file = "./Image/appIcon.png")
     downloadWindown.iconphoto(False, image_AppIcon)

     left_bg = PhotoImage(file = "./Image/download.png")
     Label(downloadWindown, image = left_bg, borderwidth = 0, highlightthickness = 0).place(x = 0, y = 0)
     downloadWindown.mainloop()


def display_UploadWindow():
     uploadWindown = Toplevel(optWindow)
     uploadWindown.title("USTF")
     uploadWindown.geometry("750x460+500+200")
     uploadWindown.configure(bg = "#ffffff")
     uploadWindown.resizable(False, False)

     image_AppIcon = PhotoImage(file = "./Image/appIcon.png")
     uploadWindown.iconphoto(False, image_AppIcon)

     left_bg = PhotoImage(file = "./Image/upload.png")
     Label(uploadWindown, image = left_bg, borderwidth = 0, highlightthickness = 0).place(x = 0, y = 0)

     main_bg = PhotoImage(file = "./Image/main_bgu.png")
     Label(uploadWindown, image = main_bg, borderwidth = 0, highlightthickness=0).place(x = 320, y = 50)

     image_SelectButton = PhotoImage(file="./Image/select.png")
     Label(uploadWindown, image=image_SelectButton, borderwidth=0, highlightthickness=0)
     select_Buttion = Button(uploadWindown, image=image_SelectButton, borderwidth=0, highlightthickness=0, command=upload)
     select_Buttion.place(x = 390, y = 280)
     uploadWindown.mainloop()


# App Icon
image_AppIcon = PhotoImage(file = "./Image/appIcon.png")
optWindow.iconphoto(False, image_AppIcon)

# Title of home page
title_optWindow = PhotoImage(file = "./Image/title_home.png")
Label(optWindow, image = title_optWindow, borderwidth = 0, highlightthickness = 0).place(x = 0, y = 20)

# Button download
image_Button_Download = PhotoImage(file = "./Image/but_download.png")
Label(optWindow, image = image_Button_Download, borderwidth = 0, highlightthickness = 0)
download_Button = Button(optWindow, image = image_Button_Download, borderwidth = 0, highlightthickness = 0, command = display_DownloadWindow)
download_Button.place(x = 75, y = 150)

# Button upload
image_Button_Upload = PhotoImage(file = "./Image/but_upload.png")
Label(optWindow, image = image_Button_Upload, borderwidth = 0, highlightthickness = 0)
upload_Button = Button(optWindow, image = image_Button_Upload, borderwidth = 0, highlightthickness = 0, command = display_UploadWindow)
upload_Button.place(x = 410, y = 150)

optWindow.mainloop()

