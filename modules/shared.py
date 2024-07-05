"""shared constant and function for server and client"""

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
