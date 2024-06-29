"""Code for sending and receiving messages over a socket"""

import struct
import os


# Because we have to send size first before data here is the max limits:
# message: 2^(4*8) bytes ~ 4.3 gigabytes
# file: 2^(8*8) bytes ~ 18.4 exabytes


MAX_BUF = 65536

### so i went wild and code the entire program in one weekend and
### forgot that each chunk need a thread so the code below is single thread ver.


def send_file(sock, file_path):
    """Send file size and data"""
    file_size = struct.pack(">Q", os.stat(file_path).st_size)
    sock.sendall(file_size)
    with open(file_path, "rb") as f:
        sock.sendfile(f)


def recv_file(sock, file_path):
    """Receive file size and write to path"""
    raw_file_size = recv_all(sock, 8)
    file_size = struct.unpack(">Q", raw_file_size)[0]
    total_written = 0
    buffer = bytearray(MAX_BUF)
    view = memoryview(buffer)
    with open(file_path, "wb") as f:
        while total_written < file_size:
            read_size = min(file_size - total_written, MAX_BUF)
            received = sock.recv_into(view[:read_size])
            if not received:
                raise OSError("Other side abruptly disconnected.")
            total_written += received
            f.write(view[:received])


def send_msg(sock, msg):
    """Prefix each message with a 4-byte length (network byte order)"""
    msg = struct.pack(">I", len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    """Unpack message length and read data"""
    raw_msg_len = recv_all(sock, 4)
    msg_len = struct.unpack(">I", raw_msg_len)[0]
    # Read the message data
    return recv_all(sock, msg_len)


def recv_all(sock, n):
    """Helper function to recv n bytes or return None if EOF is hit"""
    data = bytearray(n)
    view = memoryview(data)
    total_received = 0
    while total_received < n:
        received = sock.recv_into(
            view[total_received:], min(n - total_received, MAX_BUF)
        )
        if not received:
            raise OSError("Other side abruptly disconnected.")
        total_received += received
    return data
