import threading
from queue import Queue
from modules.message import *
import time
import os


def create_file(path, size):
    with open(path, "wb") as f:
        i = size - 1
        if i > -1:
            f.seek(i)
            f.write(b"\0")


MIN_SEGMENT_SIZE = 65536


class DownloadManager:
    def __init__(self, host, port, num_threads, min_seg, update=print):
        self.host = host
        self.port = port
        self.segment_queue = Queue()
        self.num_threads = num_threads
        self.min_seg = min_seg
        self.update = update
        self.files = {}
        self.threads = []
        self.lock = threading.Lock()

    def worker(self):
        try:
            with Messenger(self.host, self.port) as mes:
                while True:
                    segment = self.segment_queue.get()
                    if segment is None:
                        self.segment_queue.task_done()
                        break

                    file_id, start, length = segment
                    with self.lock:
                        file_data = self.files[file_id]
                        if file_data["removed"]:
                            self.segment_queue.task_done()
                            continue
                        if file_data["paused"]:
                            file_data["paused_segments"].append(segment)
                            self.segment_queue.task_done()
                            continue
                        server_path = file_data["server_path"]
                        client_path = file_data["client_path"]
                        temp_path = file_data["temp_path"]
                    if length > 0:
                        mes.send_DRRQ(server_path, start, length, temp_path)
                    with self.lock:
                        file_data = self.files[file_id]
                        file_data["bytes_done"] += length
                        self.update(file_id, file_data["bytes_done"])
                        if file_data["bytes_done"] == file_data["size"]:
                            os.rename(temp_path, client_path)
                    self.segment_queue.task_done()
        except (OSError, MessengerError) as e:
            print(e)

    def add_file(self, server_path, size, client_path):
        file_id = len(self.files)
        temp_path = client_path + ".downloading"
        self.files[file_id] = {
            "server_path": server_path,
            "size": size,
            "client_path": client_path,
            "temp_path": temp_path,
            "paused": False,
            "removed": False,
            "bytes_done": 0,
            "paused_segments": [],
        }

        create_file(temp_path, size)
        if size == 0:
            self.segment_queue.put((file_id, 0, 0))
        else:
            segment_size = max(size // (self.num_threads * 4), self.min_seg)
            for start in range(0, size, segment_size):
                length = min(segment_size, size - start)
                self.segment_queue.put((file_id, start, length))

    def add_files(self, file_list):
        for file in file_list:
            self.add_file(*file)

    def start(self):
        for _ in range(self.num_threads):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            self.threads.append(t)

    def pause_file(self, file_id):
        with self.lock:
            self.files[file_id]["paused"] = True

    def resume_file(self, file_id):
        with self.lock:
            self.files[file_id]["paused"] = False
            while self.files[file_id]["paused_segments"]:
                segment = self.files[file_id]["paused_segments"].pop(0)
                self.segment_queue.put(segment)

    def remove_file(self, file_id):
        with self.lock:
            self.files[file_id]["removed"] = True

    def wait_for_completion(self):
        self.segment_queue.join()
        for _ in range(self.num_threads):
            self.segment_queue.put(None)
        for t in self.threads:
            t.join()

    def stop(self):
        with self.lock:
            for file_id in self.files:
                self.files[file_id]["removed"] = True
        self.wait_for_completion()
        for file_id in self.files:
            if os.path.exists(self.files[file_id]["temp_path"]):
                os.remove(self.files[file_id]["temp_path"])


class UploadManager:
    def __init__(self, host, port, num_threads, min_seg, update=print):
        self.host = host
        self.port = port
        self.segment_queue = Queue()
        self.num_threads = num_threads
        self.min_seg = min_seg
        self.update = update
        self.files = {}
        self.threads = []
        self.lock = threading.Lock()

    def worker(self):
        try:
            with Messenger(self.host, self.port) as mes:
                while True:
                    segment = self.segment_queue.get()
                    if segment is None:
                        self.segment_queue.task_done()
                        break

                    file_id, start, length = segment
                    with self.lock:
                        file_data = self.files[file_id]
                        if file_data["removed"]:
                            self.segment_queue.task_done()
                            continue
                        if file_data["paused"]:
                            file_data["paused_segments"].append(segment)
                            self.segment_queue.task_done()
                            continue
                        server_path = file_data["server_path"]
                        client_path = file_data["client_path"]
                    if length > 0:
                        mes.send_DWRQ(server_path, start, length, client_path)
                    with self.lock:
                        file_data = self.files[file_id]
                        file_data["bytes_done"] += length
                        self.update(file_id, file_data["bytes_done"])
                        if file_data["bytes_done"] == file_data["size"]:
                            mes.send_FWRQ(server_path)
                    self.segment_queue.task_done()
        except (OSError, MessengerError) as e:
            print(e)

    def add_file(self, client_path, size, server_path):
        file_id = len(self.files)
        self.files[file_id] = {
            "server_path": server_path,
            "size": size,
            "client_path": client_path,
            "paused": False,
            "removed": False,
            "bytes_done": 0,
            "paused_segments": [],
        }
        if size == 0:
            self.segment_queue.put((file_id, 0, 0))
        else:
            segment_size = max(size // (self.num_threads * 4), self.min_seg)
            for start in range(0, size, segment_size):
                length = min(segment_size, size - start)
                self.segment_queue.put((file_id, start, length))

    def add_files(self, file_list):
        for file in file_list:
            self.add_file(*file)

    def start(self):
        for _ in range(self.num_threads):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            self.threads.append(t)

    def pause_file(self, file_id):
        with self.lock:
            self.files[file_id]["paused"] = True

    def resume_file(self, file_id):
        with self.lock:
            self.files[file_id]["paused"] = False
            while self.files[file_id]["paused_segments"]:
                segment = self.files[file_id]["paused_segments"].pop(0)
                self.segment_queue.put(segment)

    def remove_file(self, file_id):
        with self.lock:
            self.files[file_id]["removed"] = True

    def wait_for_completion(self):
        self.segment_queue.join()
        for _ in range(self.num_threads):
            self.segment_queue.put(None)
        for t in self.threads:
            t.join()

    def stop(self):
        with self.lock:
            for file_id in self.files:
                self.files[file_id]["removed"] = True
        self.wait_for_completion()
