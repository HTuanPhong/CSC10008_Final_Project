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
        self.source_path = client_path
        self.destinate_path = server_path
        self.file_size = os.stat(client_path).st_size
        self.progress = 0
        self.status = 'wait'

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

controller = None
def connect(host, port, threadNum: int):
    for i in range(threadNum + 1):
        messenger(host, port)
    global controller
    controller = messenger(host, port)


def uploadFile(client_path, server_path):
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

    controller.send_WRQ(destinate_path, file_size)    #might raise file already exist or out of disk
    segment_length = file_size // simpleThreadNumber
    threadWait = []
    for i in range(simpleThreadNumber):
        upload = threading.Thread(target = messengers[i].send_DWRQ, args=(
            destinate_path, 
            i * segment_length, 
            segment_length,
            client_path
        ))
        threadWait.append(upload)
        upload.start()

    if simpleThreadNumber * segment_length < file_size:
        upload = threading.Thread(target = messengers[simpleThreadNumber].send_DWRQ, args=(
            destinate_path, 
            simpleThreadNumber * segment_length, 
            file_size - simpleThreadNumber * segment_length,
            client_path
        ))
        threadWait.append(upload)
        upload.start()

    for i in range(simpleThreadNumber):
        threadWait[i].join()
    
    controller.send_FWRQ(destinate_path)

def downloadFile(server_path, client_path):
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

    file_size = controller.send_RRQ(server_path)   #might raise file not exist
    if shutil.disk_usage(client_path)[2] < file_size:
        raise OSError('client diskspace full')

    with open(file_path, "wb") as f:
        f.seek(file_size - 1)
        f.write(b"\0")
    segment_length = file_size // simpleThreadNumber
    threadWait = []
    for i in range(simpleThreadNumber):
        download = threading.Thread(target = messengers[i].send_DRRQ, args = (
            server_path,
            i * segment_length, 
            segment_length,
            file_path
        ))
        threadWait.append(download)
        download.start()
    if simpleThreadNumber * segment_length < file_size:
        download = threading.Thread(target = messengers[simpleThreadNumber].send_DRRQ, args = (
            server_path, 
            simpleThreadNumber * segment_length, 
            file_size - simpleThreadNumber * segment_length,
            file_path
        ))
        threadWait.append(download)
        download.start()

    for thread in threadWait:
        thread.join()
    
    controller.send_FWRQ(server_path)
