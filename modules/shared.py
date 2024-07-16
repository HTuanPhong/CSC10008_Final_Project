"""shared constant and function for server and client"""
#add some constant to use, like default format
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
#appearantly, file not exist is treat as invalid file path
ERR_STR = [
    "invalid file path.",        #don't have an exception, raise OSError
    "file already exist.",       #FileExistsError
    "server diskspace full.",    #OSError
    "file already uploading.",   #similar to file already exist, but for .uploading file
    "offset too large.",
    "out of range.", #IndexError exception
]
class FileTransferError(Exception):
    pass

class FileUploadingError(FileTransferError):
    pass  # Specific error for "file already uploading"
ERROR_CODES = {
    "invalid file path.": OSError('file already delete'),
    "file already exist.": FileExistsError,
    "server diskspace full.": OSError('server out of storage'),
    "file already uploading.": FileUploadingError,
    "offset too large.": IndexError('too large offset'),
    "out of range.": IndexError('out of range')
}

MAX_BUF = 65536
DEFAULT_SERVER_PORT = 8888
DEFAULT_FORMAT = 'utf-8'

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