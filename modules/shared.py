"""shared constant and function for server and client"""

# request types:
RRQ, WRQ, DRRQ, DWRQ, FWRQ, DRQ, DTRQ, FRQ = range(8)
OP_STR = [
    "Read request",
    "Write request",
    "Data read request",
    "Data write request",
    "Finish write request",
    "Delete request",
    "Directory request",
    "Create folder request",
]
ERROR, SUCCESS = range(2)
# error types:
(
    PATH_ERR,
    FILE_UPLOADING_ERR,
    DISKSPACE_ERR,
    OFFSET_ERR,
    RANGE_ERR,
    DELETE_ERR,
    FOLDER_ERR,
) = range(7)

ERR_STR = [
    "path dont exist.",  # dev fault
    "file already uploading.",  # dev fault
    "server diskspace full.",  # user decide
    "offset too large.",  # dev fault
    "out of range.",  # dev fault
    "unable to delete.",  # user decide
    "unable to make folder.",  # user decide
]


MAX_BUF = 65536
DEFAULT_SERVER_PORT = 8888
DEFAULT_FORMAT = "utf-8"


def recv_data(sock, file_path, offset, length):
    """receive data and write to file"""
    total_written = 0
    buffer = bytearray(MAX_BUF)
    view = memoryview(buffer)
    with open(file_path, "r+b") as f:
        f.seek(offset)
        while total_written < length:
            read_size = min(length - total_written, MAX_BUF)
            received = sock.recv_into(view[:read_size])
            if not received:
                raise OSError("closed connection.")
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
            raise OSError("closed connection.")
        total_received += received
    return data


import os
def get_unique_filename(filename):
    """
    Generate a unique filename by appending a number if needed.
    """
    base, extension = os.path.splitext(filename)
    new_filename = filename
    counter = 1

    while os.path.exists(os.path.join(SERVER_DATA_PATH, new_filename)):
        new_filename = f"{base}({counter}){extension}"
        counter += 1

    return new_filename