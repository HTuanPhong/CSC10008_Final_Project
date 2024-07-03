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

import struct  # for packing bytes
import os  # for directory operation
import shutil  # for disk size
import json  # to send directory
from server import SERVER_DATA_PATH

RRQ, WRQ, DRRQ, DWRQ, FWRQ, DRQ, DTRQ, FRQ = range(8)
ERROR, SUCC = range(2)
MAX_BUF = 65536


def recv_data(sock, file_path, offset, count):
    """receive data and write to file"""
    total_written = 0
    buffer = bytearray(MAX_BUF)
    view = memoryview(buffer)
    with open(file_path, "r+b") as f:
        f.seek(offset)
        while total_written < count:
            read_size = min(count - total_written, MAX_BUF)
            received = sock.recv_into(view[:read_size])
            if not received:
                raise OSError("Other side abruptly disconnected.")
            total_written += received
            f.write(view[:received])


def recv_all(sock, n):
    """recv n bytes or return except if EOF is hit."""
    data = bytearray(n)
    view = memoryview(data)
    total_received = 0
    while total_received < n:
        received = sock.recv_into(view[total_received:], n - total_received)
        if not received:
            raise OSError("Other side abruptly disconnected.")
        total_received += received
    return data


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


def send_error(sock, msg):
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


def process_RRQ(sock):
    """process read request.
    Receive structure:
       1 bytes      1 byte       n bytes
     ----------------------------------------
    |   Opcode   |   Length   |   Filepath   |
     ----------------------------------------
    Success reply structure:
       1 bytes      8 bytes
     ---------------------------
    |   Opcode   |   FileSize   |
     ---------------------------
    """
    file_path = get_path(sock)
    if not file_path:
        send_error(sock, "invalid file path.")
        return
    try:
        size = os.stat(file_path).st_size
    except OSError as e:
        send_error(sock, str(e))
        return
    sock.sendall(struct.pack(">BQ", SUCC, size))


def process_WRQ(sock):
    """process write request.
    Receive structure:
       1 bytes      1 byte       n bytes        8 bytes
     ---------------------------------------------------
    |   Opcode   |   Length   |   Filepath   |   Size   |
     ---------------------------------------------------
    Success reply structure:
       1 bytes
     ------------
    |   Opcode   |
     ------------
    """
    file_path = get_path(sock)
    file_size = struct.unpack(">Q", recv_all(sock, 8))[0]
    if not file_path:
        send_error(sock, "invalid file path.")
        return
    if os.path.isfile(file_path):
        send_error(sock, "file already exist.")
        return
    if shutil.disk_usage(SERVER_DATA_PATH)[2] < file_size:
        send_error(sock, "server diskspace full.")
        return
    file_upload_path = file_path + ".uploading"
    if os.path.isfile(file_upload_path):
        send_error(sock, "file already uploading.")
        return
    with open(file_upload_path, "wb") as f:
        f.seek(file_size - 1)
        f.write(b"\0")
    sock.sendall(struct.pack(">B", SUCC))


def process_DRRQ(sock):
    """process data read request.
    Receive structure:
       1 bytes      1 byte       n bytes        8 bytes      8 bytes
     -----------------------------------------------------------------
    |   Opcode   |   Length   |   Filepath   |   Offset   |   Length   |
     -----------------------------------------------------------------
    Success reply structure:
       1 bytes      end-start bytes
     -------------------------------
    |   Opcode   |       Data       |
     -------------------------------
    """
    file_path = get_path(sock)
    offset, length = struct.unpack(">QQ", recv_all(sock, 16))
    if not file_path:
        send_error(sock, "invalid file path.")
        return
    try:
        file_size = os.stat(file_path).st_size
    except OSError as e:
        send_error(sock, str(e))
        return
    if offset > file_size - 1:
        send_error(sock, "offset too large.")
        return
    if offset + length > file_size:
        send_error(sock, "out of range.")
        return
    with open(file_path, "rb") as f:
        sock.sendall(struct.pack(">B", SUCC))
        sock.sendfile(f, offset, length)


def process_DWRQ(sock):
    """process data write request
       1 bytes      1 byte       n bytes        8 bytes      8 bytes      n bytes
     -----------------------------------------------------------------------------
    |   Opcode   |   Length   |   Filepath   |   Offset   |   Length   |   Data   |
     -----------------------------------------------------------------------------
    Success reply structure:
       1 bytes
     ------------
    |   Opcode   |
     ------------
    """
    file_path = get_path(sock)
    offset, data_length = struct.unpack(">QQ", recv_all(sock, 16))
    if not file_path:
        send_error(sock, "invalid file path.")
        return
    file_upload_path = file_path + ".uploading"
    try:
        file_upload_size = os.stat(file_upload_path).st_size
    except OSError as e:
        send_error(sock, str(e))
        return
    if offset > file_upload_size - 1:
        send_error(sock, "offset too large.")
        return
    if offset + data_length > file_upload_size:
        send_error(sock, "out of range.")
        return
    recv_data(sock, file_upload_path, offset, data_length)
    sock.sendall(struct.pack(">B", SUCC))


def process_FWRQ(sock):
    """process finish write request
    Receive structure:
       1 bytes      1 byte       n bytes
     ----------------------------------------
    |   Opcode   |   Length   |   Filepath   |
     ----------------------------------------
    Success reply structure:
       1 bytes
     ------------
    |   Opcode   |
     ------------
    """
    file_path = get_path(sock)
    if not file_path:
        send_error(sock, "invalid file path.")
        return
    file_upload_path = file_path + ".uploading"
    new_file_path = os.path.splitext(file_upload_path)[0]
    try:
        os.rename(file_upload_path, new_file_path)
    except OSError as e:
        send_error(sock, str(e))
        return
    sock.sendall(struct.pack(">B", SUCC))


def process_DRQ(sock):
    """process delete request
    Receive structure:
       1 bytes      1 byte       n bytes
     ------------------------------------
    |   Opcode   |   Length   |   Path   |
     ------------------------------------
    Success reply structure:
       1 bytes
     ------------
    |   Opcode   |
     ------------
    """
    path = get_path(sock)
    if not path:
        send_error(sock, "invalid file path.")
        return
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            os.rmdir(path)
    except OSError as e:
        send_error(sock, str(e))
        return
    sock.sendall(struct.pack(">B", SUCC))


def process_DTRQ(sock):
    """process directory request
    Receive structure:
       1 bytes
     ------------
    |   Opcode   |
     ------------
    Success reply structure:
       1 bytes      4 bytes      n bytes
     -----------------------------------------
    |   Opcode   |   Length   |   Json data   |
     -----------------------------------------
    """
    directory_structure = {}
    for root, dirs, files in os.walk(SERVER_DATA_PATH):
        relative_path = os.path.relpath(root, SERVER_DATA_PATH)
        directory_structure[relative_path] = {"dirs": dirs, "files": files}
    data = json.dumps(directory_structure).encode("utf-8")
    sock.sendall(struct.pack(">BI", SUCC, len(data)))
    sock.sendall(data)


def process_FRQ(sock):
    """process folder request
    Receive structure:
       1 bytes      1 byte       n bytes
     ------------------------------------
    |   Opcode   |   Length   |   Path   |
     ------------------------------------
    Success reply structure:
       1 bytes
     ------------
    |   Opcode   |
     ------------
    """
    path = get_path(sock)
    if not path:
        send_error(sock, "invalid file path.")
        return
    try:
        os.mkdir(path)
    except OSError as e:
        send_error(sock, str(e))
        return
    sock.sendall(struct.pack(">B", SUCC))


def process_request(sock):
    """
    Take a socket and read the first byte for request type (opcode).
    """
    req = struct.unpack(">B", recv_all(sock, 1))[0]
    if req == RRQ:
        process_RRQ(sock)
    elif req == WRQ:
        process_WRQ(sock)
    elif req == DRRQ:
        process_DRRQ(sock)
    elif req == DWRQ:
        process_DWRQ(sock)
    elif req == FWRQ:
        process_FWRQ(sock)
    elif req == DRQ:
        process_DRQ(sock)
    elif req == DTRQ:
        process_DTRQ(sock)
    elif req == FRQ:
        process_FRQ(sock)
    else:
        send_error(sock, "unknown request.")


def send_RRQ(sock, file_path):
    """send Read request"""
    sock.sendall(struct.pack(">BB", RRQ, len(file_path)) + file_path.encode("utf-8"))


def send_WRQ(sock, file_path, size):
    """send Write request"""
    sock.sendall(
        struct.pack(">BB", WRQ, len(file_path))
        + file_path.encode("utf-8")
        + struct.pack(">Q", size)
    )


def send_DRRQ(sock, file_path, offset, count):
    """send Data read request"""
    sock.sendall(
        struct.pack(">BB", DRRQ, len(file_path))
        + file_path.encode("utf-8")
        + struct.pack(">QQ", offset, count)
    )


def send_DWRQ(sock, file_path, offset, length, local_file_path):
    """send Data write request"""
    sock.sendall(
        struct.pack(">BB", DWRQ, len(file_path))
        + file_path.encode("utf-8")
        + struct.pack(">QQ", offset, length)
    )
    with open(local_file_path, "rb") as f:
        sock.sendfile(f, offset, length)


def send_FWRQ(sock, file_path):
    """send Finish write request"""
    sock.sendall(struct.pack(">BB", FWRQ, len(file_path)) + file_path.encode("utf-8"))


def send_DRQ(sock, file_path):
    """send Delete request"""
    sock.sendall(struct.pack(">BB", DRQ, len(file_path)) + file_path.encode("utf-8"))


def send_DTRQ(sock):
    """send Directory request"""
    sock.sendall(struct.pack(">B", DTRQ))


def send_FRQ(sock, path):
    """send Create folder request"""
    sock.sendall(struct.pack(">BB", DRQ, len(path)) + path.encode("utf-8"))
