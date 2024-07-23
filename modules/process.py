import os
from modules.shared import *
from modules.message import *
import shutil
from math import ceil
import threading

#yet to be done class
class uploadProcess:
    def __init__(self, server_address, client_path, server_path):
        self.server_address = server_address
        self.client_path = client_path
        self.server_path = server_path
        self.file_size = os.stat(client_path).st_size

    def start(self):
        pass

class downloadProcess:
    def __init__(self, server_address, server_path, client_path):
        self.server_address = server_address
        self.server_path = server_path
        self.client_path = client_path
        self.file_size = send_RRQ(server_address, server_path)

#yet to be use global queue, they not even queue :v
uploadQueue = []
downloadQueue = []

simpleThreadNumber = 8

def uploadFile(server_address, client_path, server_path):
    """upload file to server
    client path should be a file (because we don't have upload folder yet :v)
    server path should be a folder"""
    #server_path should already be valid since we get it from the directory request
    if not os.path.exists(client_path):
        raise FileNotFoundError('cant find file to upload')
    
    if os.path.isdir(client_path):
        raise NotImplementedError('chua cai :v')
    
    file_size = os.stat(client_path).st_size
    file_name = os.path.basename(os.path.normpath(client_path))
    destinate_path = os.path.join(server_path, file_name)

    send_WRQ(server_address, destinate_path, file_size)    #might raise file already exist or out of disk
    segment_length = file_size // simpleThreadNumber
    threadWait = []
    for i in range(simpleThreadNumber):
        upload = threading.Thread(target = send_DWRQ, args=(
            server_address, 
            destinate_path, 
            i * segment_length, 
            segment_length,
            client_path
        ))
        threadWait.append(upload)
        upload.start()

    if simpleThreadNumber * segment_length < file_size:
        upload = threading.Thread(target = send_DWRQ, args=(
            server_address, 
            destinate_path, 
            simpleThreadNumber * segment_length, 
            file_size - simpleThreadNumber * segment_length,
            client_path
        ))
        threadWait.append(upload)
        upload.start()

    for i in range(simpleThreadNumber):
        threadWait[i].join()
    
    send_FWRQ(server_address, destinate_path)

def downloadHelper(server_address, server_path, file_path, offset, length):
    data = send_DRRQ(server_address, server_path, offset, length)
    with open(file_path, "r+b") as f:
        f.seek(offset, 0)
        f.write(data)

def downloadFile(server_address, server_path, client_path):
    """download file from server
    server path should be a file (can't download folder for now...)
    client path should be a folder
    """
    if(not os.path.exists(client_path)):    #path not found, dev error
        raise FileNotFoundError('path not found')
    if not os.path.isdir(client_path):
        raise OSError('not folder path')
    
    #this might not work on Linux
    file_name = os.path.basename(os.path.normpath(server_path))
    file_path = os.path.join(client_path, file_name)
    if os.path.exists(file_path):   #file already exist on client, user decide
        raise FileExistsError('file already exist')

    file_size = send_RRQ(server_address, server_path)   #might raise file not exist
    if shutil.disk_usage(client_path)[2] < file_size:
        raise OSError('client diskspace full')

    with open(file_path, "wb") as f:
        f.seek(file_size - 1)
        f.write(b"\0")
    segment_length = file_size // simpleThreadNumber
    threadWait = []
    for i in range(simpleThreadNumber):
        download = threading.Thread(target = downloadHelper, args = (
            server_address, 
            server_path, 
            file_path,
            i * segment_length, 
            segment_length
        ))
        threadWait.append(download)
        download.start()
    if simpleThreadNumber * segment_length < file_size:
        download = threading.Thread(target = downloadHelper, args = (
            server_address, 
            server_path, 
            file_path,
            simpleThreadNumber * segment_length, 
            file_size - simpleThreadNumber * segment_length
        ))
        threadWait.append(download)
        download.start()

    for thread in threadWait:
        thread.join()
    
    send_FWRQ(server_address, server_path)
