import os
from modules.shared import *
from modules.message import *
import shutil
from math import ceil
import threading
import time

simpleThreadNumber = 8
MAX_CONNECTIONS = 8
DEF_BUF = 2 ** 13 #8kB
directory_path = None
# HOST = None
# PORT = None
HOST = "localhost"  # IP adress server
PORT = 8888  # Port is used by the server

def set_address(host, port):
    global HOST, PORT
    HOST = host
    PORT = port

#region Manager
#connections manager and process manager
#use static amount of connections for now

connections = []
queue = []
error_queue = []
manager_error = 'null'
manager_status = 'wait'
# for i in range(MAX_CONNECTIONS):
#     connections.append(messenger(HOST, PORT))
    
def upload(client_paths, sizes, server_folder, callback = print):
    for client_path, size in zip(client_paths, sizes):
        process = Upload(client_path, server_folder, size, callback)
        queue.append(process)

def download(server_paths, sizes, client_folder, callback = print):
    for server_path, size in zip(server_paths, sizes): 
        process = Download(client_folder, server_path, size, callback)
        queue.append(process)

def manager(error_callback = print):
    while manager_status != 'stop':
        time.sleep(0.25)
        if len(queue) > 0:
            try:
                connection_cnt = ceil(queue[-1].file_size / DEF_BUF)
                
                while (len(connections) < MAX_CONNECTIONS) and (len(connections) < connection_cnt):
                    connections.append(messenger(HOST, PORT))
                    
                print('connection cnt:', connection_cnt, queue[-1].file_size, DEF_BUF)
                queue[-1].startProcess(connections)
                if(queue[-1].status == 'finish'):
                    queue.pop(-1)

            except Exception as error:
                error_callback(error)
                error_queue.append(queue[-1])
                queue.pop()
        else:
            for i in range(len(connections)-1, -1, -1):
                connections[i].close()
                connections.pop(i)
    
    print('error queue', error_queue)
    for i in range(len(connections)-1, -1, -1):
                connections[i].close()
                connections.pop(i)

Manager = None

def managerStart(error_callback):
    global manager, manager_status
    manager_status = 'working'
    Manager = threading.Thread(target=manager, args=(error_callback,))
    Manager.start()

def managerStop():
    global manager_status
    manager_status = 'stop'

def managerPause(num: int):
    "pause process num th in queue"
    queue[num].pauseProcess()

#endregion

#yet to be done class
#region Segment
class Segment():
    def __init__(self, offset, length, process):
        self.offset = offset
        self.length = length
        self.process = process
        self.thread = None
        self.mark_byte = 0
        self.progress = 0
        self.cnt = 0

    def __str__(self):
        return f"({self.offset}, {self.length})"

    def startProcess(self, messenger):
        if self.length == 0:
            return

        try:
            while(self.mark_byte < self.length and self.process.status != 'pause'):
                # self.cnt += 1
                # if self.cnt == 100:
                #     print('progress', self.offset, self.progress)
                #     self.cnt = 0
                
                if isinstance(self.process, Upload):
                    messenger.send_DWRQ(
                        self.process.destinate_path,
                        self.offset + self.mark_byte,
                        min(DEF_BUF, self.length - self.mark_byte),
                        self.process.client_path
                    )
                    self.mark_byte += min(MAX_BUF, self.length - self.mark_byte)
                    self.progress = self.mark_byte / self.length
                    self.process.callback(self.process.client_path, self.process.server_path, self.mark_byte)

                else:
                    messenger.send_DRRQ(
                        self.process.server_path,
                        self.offset + self.mark_byte,
                        min(DEF_BUF, self.length - self.mark_byte),
                        self.process.destinate_path
                    )
                    self.mark_byte += min(MAX_BUF, self.length - self.mark_byte)
                    self.progress = self.mark_byte / self.length
                    self.process.callback(self.process.server_path, self.process.client_path, self.mark_byte)
        except Exception as error:
            #dev error here
            print("segment error:", error)
            pass
        finally:
            self.offset += self.mark_byte
            self.length -= self.mark_byte
            self.mark_byte = 0

    def _start(self, connection: messenger):
        self.thread = threading.Thread(target= self.startProcess, args=(connection, ))
        self.thread.start()
#endregion

#region Process
class Process():
    """
    Class to handle download of a single file
    """
    def __init__(self, client_path, server_path, size, callback = print):
        self.client_path = client_path
        self.server_path = server_path
        self.file_size = size
        self.callback = callback

        self.segments = []
        self.connections = []
        self.status = 'wait'
        self.error = 'null'
        
    def __str__(self):
        return f"({self.getProgress()})"
    def __repr__(self):
        return f"({self.client_path}, {self.server_path}, {self.getProgress()})"
    def _start():
        pass
    def _finish():
        pass
    def _checkPath(self):
        pass

    def _fragment(self):
        connection_ = len(self.connections)
        print('segment', connection_)
        segment_length = self.file_size // connection_
        
        for i in range(connection_):
            offset = i * segment_length
            length = min(segment_length, self.file_size - offset)
            self.segments.append(Segment(offset, length, self))

        # If the last segment is smaller than segment_length
        if self.segments:
            self.segments[-1].length = self.file_size - self.segments[-1].offset

    #need to handle differently went update to dynamic connection
    def startProcess(self, connections):
        try:
            if self.status == 'wait':
                self._start(connections)
                self._fragment()

                self.continueProcess()

            else:
                raise Exception('already uploading')
                #for handling with client pressing button multiple time 
        except Exception as error:
            self.callback('start error:', error)
            self.status = 'wait'
            self.error = error
            raise error

    def continueProcess(self):
        self.status = 'processing...'
        for segment, connection in zip(self.segments, self.connections):
            segment._start(connection)

        for segment in self.segments:
                    segment.thread.join()

        if(self.status != 'pause' or self.status != 'error'):
            self._finish(self.connections[0])
            self.status = 'finish'
        
    def pauseProcess(self):
        self.status = 'pause'

    def getProgress(self):
        processed_byte = self.file_size
        for segment in self.segments:
            processed_byte -= segment.length
        
        return processed_byte / self.file_size

    def getSegmentProgress(self):
        segmentsProgress = []
        for segment in self.segments:
            segmentsProgress.append((segment.offset, segment.progress))

        return segmentsProgress

#endregion

#region Upload
class Upload(Process):
    def __init__(self, client_path, server_path, file_size, callback = print):
        super().__init__(client_path, server_path, file_size, callback)
        self.destinate_path = None

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return f"({self.client_path_path}, {self.destinate_path}, {self.getProgress()})"

    def _start(self, connections):
        try:
            if not os.path.exists(self.client_path):
                raise FileNotFoundError('cant find file to upload')
            
            if os.path.isdir(self.client_path):
                raise NotImplementedError('chua cai :v')
            
            file_name = os.path.basename(os.path.normpath(self.client_path))
            self.destinate_path = os.path.join(self.server_path, file_name)

            self.status = 'start'
            self.connections = connections

            #might raise file already exist or out of disk
            connections[0].send_WRQ(self.destinate_path, self.file_size)
               
        except Exception as error:
            self.callback('Process error:', error)
            self.status = 'error'
            self.error = error
            raise error

    def _finish(self, connection):
        connection.send_FWRQ(self.destinate_path)
#endregion

#region Download
class Download(Process):
    def __init__(self, client_path, server_path, file_size, callback = print):
        super().__init__(client_path, server_path, file_size, callback)
        self.destinate_path = None

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return f"({self.server_path}, {self.destinate_path}, {self.getProgress()})"
    def check(self):
        pass
    def _start(self, connections):
        try:
            if(not os.path.exists(self.client_path)):    #path not found, dev error
                raise FileNotFoundError('path not found')
            if not os.path.isdir(self.client_path):
                raise OSError('not folder path')
            
            #this might not work on Linux
            file_name = os.path.basename(os.path.normpath(self.server_path))
            self.destinate_path = os.path.join(self.client_path, file_name)
            if os.path.exists(self.destinate_path):   #file already exist on client, user decide
                # print('file dest:', self.destinate_path)
                # self.destinate_path = get_unique_filename(self.destinate_path)
                raise FileExistsError('file already exist')

            self.file_size = connections[0].send_RRQ(self.server_path)   #might raise file not exist
            if shutil.disk_usage(self.client_path)[2] < self.file_size:
                raise OSError('client diskspace full')

            self.destinate_path = self.destinate_path + '.downloading'
            with open(self.destinate_path, "wb") as f:
                f.seek(self.file_size - 1)
                f.write(b"\0")

            self.status = 'start'
            self.connections = connections

        except Exception as error:
            self.callback('start error:', error)
            self.status = 'wait'
            self.error = error
            raise error

    def _finish(self, connection):
        new_file_path = os.path.splitext(self.destinate_path)[0]
        os.rename(self.destinate_path, new_file_path)