""" Custom basic file management protocol.

    client -> server
    opcode  operation
      0     Read request (RRQ)
      1     Write request (WRQ)
      2     Data read request (DRRQ)
      3     Data write request (DWRQ)
      4     Finish write request (FWRQ)
      5     Delete request (DRQ)
      6     Directory request (DTRQ)
      7     Create folder request (FRQ)

    server -> client
    opcode  operation
      0     Error (ERROR)
      1     Success (SUCCESS)

    request/reply structure:
       1 byte      n bytes
     -----------------------
    |   Opcode   |   Data   |
     -----------------------
    Length is big endian. (the internet standard)
    length is prefix for next segment. 

    max file path is 2^8 bytes = 255 characters.
    max file size is 2^(8*8) bytes ~ 18.3 exabytes.
"""

import struct  # for packing bytes
import os  # for directory operation
import shutil  # for disk size
import json  # to send directory
import time  # for directory monitor
from modules.shared import *

SERVER_DATA_PATH = ""
log = print


def set_log_method(func):
    global log
    log = func


def set_server_data_path(path):
    global SERVER_DATA_PATH
    SERVER_DATA_PATH = path


def get_path(sock):
    """Get path from socket.
    stop path with uplink.
    stop path with no dir exist.
    """
    path_length = struct.unpack(">B", recv_all(sock, 1))[0]
    file_path = os.path.normpath(recv_all(sock, path_length).decode(DEFAULT_FORMAT))
    if file_path.startswith(".." + os.sep):
        return ""
    local_file_path = os.path.join(SERVER_DATA_PATH, file_path)
    if not os.path.exists(os.path.dirname(local_file_path)):
        return ""
    return local_file_path


def send_error(sock, ip, msg):
    """send ERROR message reply.
    message length limit: 255 letters.

    Reply structure:
       1 byte       1 bytes      n bytes
     ---------------------------------------
    |   Opcode   |   Length   |   Message   |
     ---------------------------------------
    """
    data = msg.encode(DEFAULT_FORMAT)
    sock.sendall(struct.pack(">BB", ERROR, len(data)) + data)
    log(f"[INFO]: {ip} got an error: {msg}")


def process_RRQ(sock, ip):
    """process read request.
    Receive structure:
       1 byte       n bytes
     ---------------------------
    |   Length   |   Filepath   |
     ---------------------------
    Success reply structure:
       1 bytes      8 bytes
     ---------------------------
    |   Opcode   |   FileSize   |
     ---------------------------
    """
    log(f"[INFO]: {ip} sent a {OP_STR[RRQ]}.")
    file_path = get_path(sock)
    if not file_path:
        send_error(sock, ip, ERR_STR[PATH_ERR])
        return False
    size = os.stat(file_path).st_size
    sock.sendall(struct.pack(">BQ", SUCCESS, size))
    log(f"[INFO]: {ip} got a success on {OP_STR[RRQ]}")
    return True


def process_WRQ(sock, ip):
    """process write request.
    Receive structure:
       1 byte       n bytes        8 bytes
     --------------------------------------
    |   Length   |   Filepath   |   Size   |
     --------------------------------------
    Success reply structure:
       1 bytes
     ------------
    |   Opcode   |
     ------------
    """
    log(f"[INFO]: {ip} sent a {OP_STR[WRQ]}.")
    file_path = get_path(sock)
    file_size = struct.unpack(">Q", recv_all(sock, 8))[0]
    if not file_path:
        send_error(sock, ip, ERR_STR[PATH_ERR])
        return False
    if shutil.disk_usage(SERVER_DATA_PATH)[2] < file_size:
        send_error(sock, ip, ERR_STR[DISKSPACE_ERR])
        return False
    file_upload_path = file_path + ".uploading"
    if os.path.isfile(file_upload_path):
        send_error(sock, ip, ERR_STR[FILE_UPLOADING_ERR])
        return False
    with open(file_upload_path, "wb") as f:
        f.seek(file_size - 1)
        f.write(b"\0")
    sock.sendall(struct.pack(">B", SUCCESS))
    log(f"[INFO]: {ip} got a success on {OP_STR[WRQ]}")
    return True


def process_DRRQ(sock, ip):
    """process data read request.
    Receive structure:
       1 byte       n bytes        8 bytes      8 bytes
     ----------------------------------------------------
    |   Length   |   Filepath   |   Offset   |   Length   |
     ----------------------------------------------------
    Success reply structure:
       1 bytes      Length bytes
     -------------------------------
    |   Opcode   |       Data       |
     -------------------------------
    """
    log(f"[INFO]: {ip} sent a {OP_STR[DRRQ]}.")
    file_path = get_path(sock)
    offset, length = struct.unpack(">QQ", recv_all(sock, 16))
    if not file_path:
        send_error(sock, ip, ERR_STR[PATH_ERR])
        return False
    file_size = os.stat(file_path).st_size
    if offset > file_size - 1:
        send_error(sock, ip, ERR_STR[OFFSET_ERR])
        return False
    if offset + length > file_size:
        send_error(sock, ip, ERR_STR[RANGE_ERR])
        return False
    with open(file_path, "rb") as f:
        sock.sendall(struct.pack(">B", SUCCESS))
        sock.sendfile(f, offset, length)
    log(f"[INFO]: {ip} got a success on {OP_STR[DRRQ]}")
    return True


def process_DWRQ(sock, ip):
    """process data write request
    Receive structure:
       1 byte       n bytes        8 bytes      8 bytes      n bytes
     ----------------------------------------------------------------
    |   Length   |   Filepath   |   Offset   |   Length   |   Data   |
     ----------------------------------------------------------------
    Success reply structure:
       1 bytes
     ------------
    |   Opcode   |
     ------------
    """
    log(f"[INFO]: {ip} sent a {OP_STR[DWRQ]}.")
    file_path = get_path(sock)
    offset, data_length = struct.unpack(">QQ", recv_all(sock, 16))
    if not file_path:
        send_error(sock, ip, ERR_STR[PATH_ERR])
        return False
    file_upload_path = file_path + ".uploading"
    file_upload_size = os.stat(file_upload_path).st_size
    if offset > file_upload_size - 1:
        send_error(sock, ip, ERR_STR[OFFSET_ERR])
        return False
    if offset + data_length > file_upload_size:
        send_error(sock, ip, ERR_STR[RANGE_ERR])
        return False
    recv_data(sock, file_upload_path, offset, data_length)
    sock.sendall(struct.pack(">B", SUCCESS))
    log(f"[INFO]: {ip} got a success on {OP_STR[DWRQ]}")
    return True


def process_FWRQ(sock, ip):
    """process finish write request
    Receive structure:
       1 byte       n bytes
     ---------------------------
    |   Length   |   Filepath   |
     ---------------------------
    Success reply structure:
       1 bytes
     ------------
    |   Opcode   |
     ------------
    """
    log(f"[INFO]: {ip} sent a {OP_STR[FWRQ]}.")
    file_path = get_path(sock)
    if not file_path:
        send_error(sock, ip, ERR_STR[PATH_ERR])
        return False
    file_upload_path = file_path + ".uploading"
    new_file_path = os.path.splitext(file_upload_path)[0]
    os.rename(file_upload_path, get_unique_filename(new_file_path))
    sock.sendall(struct.pack(">B", SUCCESS))
    log(f"[INFO]: {ip} got a success on {OP_STR[FWRQ]}")
    return True


def process_DRQ(sock, ip):
    """process delete request
    Receive structure:
       1 byte       n bytes
     -----------------------
    |   Length   |   Path   |
     -----------------------
    Success reply structure:
       1 bytes
     ------------
    |   Opcode   |
     ------------
    """
    log(f"[INFO]: {ip} sent a {OP_STR[DRQ]}.")
    path = get_path(sock)
    if not path:
        send_error(sock, ip, ERR_STR[PATH_ERR])
        return False
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    except OSError as e:
        send_error(sock, ip, ERR_STR[PATH_ERR])
        return False
    sock.sendall(struct.pack(">B", SUCCESS))
    log(f"[INFO]: {ip} got a success on {OP_STR[DRQ]}")
    return True


def get_directory():
    directory = {"type": "folder", "name": "root", "path": "."}

    def build_json_structure(root_dir, current_path=""):
        structure = []

        with os.scandir(root_dir) as it:
            for entry in it:
                entry_path = os.path.join(current_path, entry.name)
                entry_info = {
                    "type": "folder" if entry.is_dir(follow_symlinks=False) else "file",
                    "name": entry.name,
                    "path": entry_path,
                }
                if entry.is_dir(follow_symlinks=False):
                    entry_info["children"] = build_json_structure(
                        os.path.join(root_dir, entry.name), entry_path
                    )
                else:
                    stat = entry.stat()
                    entry_info["size"] = stat.st_size
                    entry_info["mtime"] = stat.st_mtime

                structure.append(entry_info)

        return structure

    directory["children"] = build_json_structure(SERVER_DATA_PATH)
    return directory


def send_directory(sock, directory):
    """Send directory with length prefix"""
    data = json.dumps(directory).encode(DEFAULT_FORMAT)
    sock.sendall(struct.pack(">BI", SUCCESS, len(data)))
    sock.sendall(data)


directory_snapshot = None
directory_time = 0
directory_refresh_rate = 1
stop_event = None


def set_directory_refresh_rate(seconds):
    global directory_refresh_rate
    directory_refresh_rate = seconds


def set_stop_event(event):
    global stop_event
    stop_event = event


def monitor_directory():
    """Polling for a directory change"""
    while not stop_event.is_set():
        current_snapshot = get_directory()
        global directory_snapshot, directory_time
        if directory_snapshot != current_snapshot:
            directory_time = time.time()
            directory_snapshot = current_snapshot
        time.sleep(directory_refresh_rate)


def process_DTRQ(sock, ip):
    """process directory subscribe
    Success reply structure:
       1 bytes      4 bytes      n bytes
     -----------------------------------------
    |   Opcode   |   Length   |   Json data   |
     -----------------------------------------
    """
    log(f"[INFO]: {ip} sent a {OP_STR[DTRQ]}.")
    last_timeout = sock.gettimeout()
    last_time = 0
    sock.settimeout(directory_refresh_rate)
    while not stop_event.is_set():
        if last_time != directory_time:
            sock.settimeout(last_timeout)
            send_directory(sock, directory_snapshot)
            last_time = directory_time
            sock.settimeout(directory_refresh_rate)
        try:
            recv_all(sock, 1)
        except TimeoutError:
            continue


def process_FRQ(sock, ip):
    """process folder request
    Receive structure:
       1 byte       n bytes
     -----------------------
    |   Length   |   Path   |
     -----------------------
    Success reply structure:
       1 bytes
     ------------
    |   Opcode   |
     ------------
    """
    log(f"[INFO]: {ip} sent a {OP_STR[FRQ]}.")
    path = get_path(sock)
    if not path:
        send_error(sock, ip, ERR_STR[PATH_ERR])
        return False
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            send_error(sock, ip, ERR_STR[FOLDER_ERR])
            return False
    sock.sendall(struct.pack(">B", SUCCESS))
    log(f"[INFO]: {ip} got a success on {OP_STR[FRQ]}")
    return True
