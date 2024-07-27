import os
from modules.shared import *
from modules.message import *
# from shared import *
# from message import *
import shutil
from math import ceil
import threading
import queue

simpleThreadNumber = 8


#region Manager
#connections manager and process manager, properly need a thread to handle process
#use static amount of connections for now
class UploadQueue():
    "Class to manage the hold upload process, also handle connection"
    def __init__(self, host, port):
        self.connections = []
        self.queue = queue.Queue
        self.errorQueue = queue.Queue
        self.status = 'wait'
        for i in range(simpleThreadNumber):
            self.connections.append(messengers(host, port))
        
        self.manager = threading.Thread(target=self.manager())

    
    def processUpload(self, client_path, server_path):
        self.queue.put(UploadProcess(client_path, server_path))

    #for now, only support upload 1 file at a time,
    def manager(self):
        while(self.status != 'stop'):
            if(self.queue.not_empty):
                self.startUpload()
        
    def startUpload(self):
        process = self.queue.get()
        try:
            process.start(self.connections)
        except:
            self.errorQueue.put(process)

    def stop(self):
        self.status = 'stop'
#endregion


#yet to be done class
#region upload
class UploadProcess():
    """Class to handle download of a single file
    """
    def __init__(self, client_path, server_path):
        self.source_path = client_path
        self.destinate_path = server_path
        self.file_size = os.stat(client_path).st_size
        self.segments = []      #use to expose data segment that haven't upload
        self.connections = []
        self.progress = 0       #expose progress
        self.status = 'wait'
        self.error = 'null'

#region segment Class
    class Segment():
        "inner class to handle data transfer of 1 segment"  
        def __init__(self, offset, length, process):
            self.offset = offset
            self.length = length
            self.process = process
            self.thread = None
            self.mark_byte = 0
            self.progress = 0

        def __str__(self):
            return f"({self.offset}, {self.length})"

        def startProcess(self, mes):
            if self.length == 0:
                return

            try:
                while(self.mark_byte < self.length and self.process.status != 'pause'):
                    print('debug:', self.process.destinate_path)
                    mes.send_DWRQ(
                        self.process.destinate_path,
                        self.offset,
                        min(MAX_BUF, self.length - self.mark_byte),
                        self.process.source_path
                    )
                    self.mark_byte += MAX_BUF
                    self.progress = self.mark_byte / self.length
            except Exception as error:
                print("segment error:", error)
                pass
            finally:
                self.offset += self.mark_byte
                self.length -= self.mark_byte
                self.mark_byte = 0

        def start(self, connection: messenger):
            self.thread = threading.Thread(target= self.startProcess, args=(connection, ))
            self.thread.start()
#endregion segment class
        
    #simply divide data length into segments
    def start(self, connections: list):
        """upload file to server
        client path should be a file (because we don't have upload folder yet :v)
        server path should be a folder"""
        #server_path should already be valid since we get it from the directory request

#region path checking
        try:
            if not os.path.exists(self.source_path):
                raise FileNotFoundError('cant find file to upload')
            
            if os.path.isdir(self.source_path):
                raise NotImplementedError('chua cai :v')
            
            file_name = os.path.basename(os.path.normpath(self.source_path))
            self.destinate_path = os.path.join(self.destinate_path, file_name)
            print('client path:', self.source_path)
            print('server path:', self.destinate_path)

#region fragment data into segment
            self.status = 'start'
            self.connections = connections

            connections[0].send_WRQ(self.destinate_path, self.file_size)    #might raise file already exist or out of disk
            connection_ = len(connections)
            segment_length = self.file_size // connection_

            for i in range(connection_):
                offset = i * segment_length
                length = min(segment_length, self.file_size - offset)
                self.segments.append(UploadProcess.Segment(offset, length, self))
    
            # If the last segment is smaller than segment_length
            if self.segments:
                self.segments[-1].length = self.self.file_size - self.segments[-1].offset

#region start process
            self.startProcess()
#region error
        except Exception as error:
            print('start error:', error)
            self.status = 'wait'
            self.error = error
#endregion
    def pauseProcess(self):
        self.status = 'pause'

    #need to handle differently went update to dynamic connection
    def startProcess(self):
        try:
            if self.status != 'uploading...':
                self.status = 'uploading...'
                for segment, connection in zip(self.segments, self.connections):
                    segment.start(connection)

                for segment in self.segments:
                    segment.thread.join()

                if(self.status != 'pause' or self.status != 'error'):
                    self.connections[0].send_FWRQ(self.destinate_path)
                    self.status = 'finish'
            else:
                raise Exception('already uploading')
                #for handling with client pressing button multiple time
        except Exception as error:
            print('Process error:', error)




#region download
class DownloadProcess():
#copy straight from upload, yet to be fix
    """Class to handle download of a single file
    """
    def __init__(self, server_path, client_path):
        self.source_path = server_path
        self.folder_path = client_path
        self.destinate_path = None
        self.file_size = None
        self.segments = []      #use to expose data segment that haven't upload
        self.connections = []
        self.progress = 0       #expose progress
        self.status = 'wait'
        self.error = 'null'

#region segment Class
    class Segment():
        "inner class to handle data transfer of 1 segment"  
        def __init__(self, offset, length, process):
            self.offset = offset
            self.length = length
            self.process = process
            self.progress = process
            self.thread = None
            self.mark_byte = 0
            self.progress = 0

        def __str__(self):
            return f"({self.offset}, {self.length})"

        def startProcess(self, mes):
            if self.length == 0:
                return

            try:
                while(self.mark_byte < self.length and self.process.status != 'pause'):
                    print('debug:', self.process.destinate_path)
                    mes.send_DRRQ(
                        self.process.source_path,
                        self.offset,
                        min(MAX_BUF, self.length - self.mark_byte),
                        self.process.destinate_path
                    )
                    self.mark_byte += MAX_BUF
                    self.progress = self.mark_byte / self.length
            except Exception as error:
                print("segment error:", error)
                pass
            finally:
                self.offset += self.mark_byte
                self.length -= self.mark_byte
                self.mark_byte = 0

        def start(self, connection: messenger):
            self.thread = threading.Thread(target= self.startProcess, args=(connection, ))
            self.thread.start()
#endregion segment class
        
    #simply divide data length into segments
    def start(self, connections: list):
        """download file from server
        server path should be a file (can't download folder for now...)
        client path should be a folder
        """

#region path checking
        try:
            if(not os.path.exists(self.folder_path)):    #path not found, dev error
                raise FileNotFoundError('path not found')
            if not os.path.isdir(self.folder_path):
                raise OSError('not folder path')
            
            #this might not work on Linux
            file_name = os.path.basename(os.path.normpath(self.source_path))
            self.destinate_path = os.path.join(self.folder_path, file_name)
            if os.path.exists(self.destinate_path):   #file already exist on client, user decide
                raise FileExistsError('file already exist')

            self.file_size = connections[0].send_RRQ(self.source_path)   #might raise file not exist
            if shutil.disk_usage(self.folder_path)[2] < self.file_size:
                raise OSError('client diskspace full')

            self.destinate_path = self.destinate_path + '.downloading'

#region fragment data into segment
            self.status = 'start'
            self.connections = connections

            connection_ = len(connections)
            segment_length = self.file_size // connection_

            for i in range(connection_):
                offset = i * segment_length
                length = min(segment_length, self.file_size - offset)
                self.segments.append(DownloadProcess.Segment(offset, length, self))
    
            # If the last segment is smaller than segment_length
            if self.segments:
                self.segments[-1].length = self.file_size - self.segments[-1].offset

#region start process
            self.startProcess()
#region error
        # except:
        #     pass
        except Exception as error:
            print('start error:', error)
            self.status = 'wait'
            self.error = error
#endregion
    def pauseProcess(self):
        self.status = 'pause'

    #need to handle differently went update to dynamic connection
    def startProcess(self):
        try:
            if self.status == 'start':
                with open(self.destinate_path, "wb") as f:
                    f.seek(self.file_size - 1)
                    f.write(b"\0")

            if self.status != 'downloading...':
                self.status = 'downloading...'
                for segment, connection in zip(self.segments, self.connections):
                    segment.start(connection)

                for segment in self.segments:
                    segment.thread.join()

                if(self.status != 'pause' or self.status != 'error'):
                    new_file_path = os.path.splitext(self.destinate_path)[0]
                    os.rename(self.destinate_path, get_unique_filename(new_file_path, self.folder_path))
                    self.status = 'finish'
            else:
                raise Exception('already downloading...')
                #for handling with client pressing button multiple time
        except Exception as error:
            print('Process error:', error)
#endregion download

#region old code
# controller = None
# def connect(host, port, threadNum: int):
#     for i in range(threadNum + 1):
#         messenger(host, port)
#     global controller
#     controller = messenger(host, port)

# def downloadFile(server_path, client_path):
#     """download file from server
#     server path should be a file (can't download folder for now...)
#     client path should be a folder
#     """
#     if(not os.path.exists(client_path)):    #path not found, dev error
#         raise FileNotFoundError('path not found')
#     if not os.path.isdir(client_path):
#         raise OSError('not folder path')
    
#     #this might not work on Linux
#     file_name = os.path.basename(os.path.normpath(server_path))
#     file_path = os.path.join(client_path, file_name)
#     if os.path.exists(file_path):   #file already exist on client, user decide
#         raise FileExistsError('file already exist')

#     file_size = controller.send_RRQ(server_path)   #might raise file not exist
#     if shutil.disk_usage(client_path)[2] < file_size:
#         raise OSError('client diskspace full')

#     with open(file_path, "wb") as f:
#         f.seek(file_size - 1)
#         f.write(b"\0")
#     segment_length = file_size // simpleThreadNumber
#     threadWait = []
#     for i in range(simpleThreadNumber):
#         download = threading.Thread(target = messengers[i].send_DRRQ, args = (
#             server_path,
#             i * segment_length, 
#             segment_length,
#             file_path
#         ))
#         threadWait.append(download)
#         download.start()
#     if simpleThreadNumber * segment_length < file_size:
#         download = threading.Thread(target = messengers[simpleThreadNumber].send_DRRQ, args = (
#             server_path, 
#             simpleThreadNumber * segment_length, 
#             file_size - simpleThreadNumber * segment_length,
#             file_path
#         ))
#         threadWait.append(download)
#         download.start()

#     for thread in threadWait:
#         thread.join()
    
#     controller.send_FWRQ(server_path)
#endregion old code