""" Custom basic stateless file management protocol.
    by H.T.Phong

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
      1     Success (SUCC)

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
#TODO: change utf-8 to some constant in shared file
#change send error message to opcode

import struct  # for packing bytes
import os  # for directory operation
import shutil  # for disk size
import json  # to send directory
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
    file_path = os.path.normpath(recv_all(sock, path_length).decode("utf-8"))
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
    data = msg.encode("utf-8")
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
        send_error(sock, ip, "invalid file path.")
        return
    try:
        size = os.stat(file_path).st_size
    except OSError as e:
        send_error(sock, ip, str(e))
        return
    sock.sendall(struct.pack(">BQ", SUCC, size))
    log(f"[INFO]: {ip} got a success on {OP_STR[RRQ]}")


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
        send_error(sock, ip, "invalid file path.")
        return
    if os.path.isfile(file_path):
        send_error(sock, ip, "file already exist.")
        return
    if shutil.disk_usage(SERVER_DATA_PATH)[2] < file_size:
        send_error(sock, ip, "server diskspace full.")
        return
    file_upload_path = file_path + ".uploading"
    if os.path.isfile(file_upload_path):
        send_error(sock, ip, "file already uploading.")
        return
    with open(file_upload_path, "wb") as f:
        f.seek(file_size - 1)
        f.write(b"\0")
    sock.sendall(struct.pack(">B", SUCC))
    log(f"[INFO]: {ip} got a success on {OP_STR[WRQ]}")


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
        send_error(sock, ip, "invalid file path.")
        return
    try:
        file_size = os.stat(file_path).st_size
    except OSError as e:
        send_error(sock, ip, str(e))
        return
    if offset > file_size - 1:
        send_error(sock, ip, "offset too large.")
        return
    if offset + length > file_size:
        send_error(sock, ip, "out of range.")
        return
    with open(file_path, "rb") as f:
        sock.sendall(struct.pack(">B", SUCC))
        sock.sendfile(f, offset, length)
    log(f"[INFO]: {ip} got a success on {OP_STR[DRRQ]}")


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
        send_error(sock, ip, "invalid file path.")
        return
    file_upload_path = file_path + ".uploading"
    try:
        file_upload_size = os.stat(file_upload_path).st_size
    except OSError as e:
        send_error(sock, ip, str(e))
        return
    if offset > file_upload_size - 1:
        send_error(sock, ip, "offset too large.")
        return
    if offset + data_length > file_upload_size:
        send_error(sock, ip, "out of range.")
        return
    recv_data(sock, file_upload_path, offset, data_length)
    sock.sendall(struct.pack(">B", SUCC))
    log(f"[INFO]: {ip} got a success on {OP_STR[DWRQ]}")


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
        send_error(sock, ip, "invalid file path.")
        return
    file_upload_path = file_path + ".uploading"
    new_file_path = os.path.splitext(file_upload_path)[0]
    try:
        os.rename(file_upload_path, new_file_path)
    except OSError as e:
        send_error(sock, ip, str(e))
        return
    sock.sendall(struct.pack(">B", SUCC))
    log(f"[INFO]: {ip} got a success on {OP_STR[FWRQ]}")


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
        send_error(sock, ip, "invalid file path.")
        return
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            os.rmdir(path)
    except OSError as e:
        send_error(sock, ip, str(e))
        return
    sock.sendall(struct.pack(">B", SUCC))
    log(f"[INFO]: {ip} got a success on {OP_STR[DRQ]}")


def process_DTRQ(sock, ip):
    """process directory request
    Success reply structure:
       1 bytes      4 bytes      n bytes
     -----------------------------------------
    |   Opcode   |   Length   |   Json data   |
     -----------------------------------------
    """
    log(f"[INFO]: {ip} sent a {OP_STR[DTRQ]}.")
    directory_structure = {}
    for root, dirs, files in os.walk(SERVER_DATA_PATH):
        relative_path = os.path.relpath(root, SERVER_DATA_PATH)
        directory_structure[relative_path] = {"dirs": dirs, "files": files}
    data = json.dumps(directory_structure).encode("utf-8")
    sock.sendall(struct.pack(">BI", SUCC, len(data)))
    sock.sendall(data)
    log(f"[INFO]: {ip} got a success on {OP_STR[DTRQ]}")


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
        send_error(sock, ip, "invalid file path.")
        return
    try:
        os.mkdir(path)
    except OSError as e:
        send_error(sock, ip, str(e))
        return
    sock.sendall(struct.pack(">B", SUCC))
    log(f"[INFO]: {ip} got a success on {OP_STR[FRQ]}")


def process_request(sock, ip):
    """
    Take a socket and read the first byte for request type (opcode).
    """
    req = struct.unpack(">B", recv_all(sock, 1))[0]
    if req == RRQ:
        process_RRQ(sock, ip)
    elif req == WRQ:
        process_WRQ(sock, ip)
    elif req == DRRQ:
        process_DRRQ(sock, ip)
    elif req == DWRQ:
        process_DWRQ(sock, ip)
    elif req == FWRQ:
        process_FWRQ(sock, ip)
    elif req == DRQ:
        process_DRQ(sock, ip)
    elif req == DTRQ:
        process_DTRQ(sock, ip)
    elif req == FRQ:
        process_FRQ(sock, ip)
    else:
        log(f"[INFO]: {ip} sent an unknown.")
        send_error(sock, ip, "unknown request.")
