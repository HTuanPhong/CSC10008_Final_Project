"""Code for sending and receiving messages over a socket"""

import struct
import os


# Because we have to send size first before data here is the max limits:
# message: 2^(4*8) bytes ~ 4.3 gigabytes
# file: 2^((2^(4*8))*8) bytes ~ (⊙_⊙;)?


MAX_BUF = 65536


def send_file(sock, file_path):
    """Send file size and data"""
    file_size = struct.pack(">I", os.stat(file_path).st_size)
    send_msg(sock, file_size)
    with open(file_path, "rb") as f:
        sock.sendfile(f)


def recv_file(sock, file_path):
    """Receive file size and write to path"""
    raw_file_size = recv_msg(sock)
    file_size = struct.unpack(">I", raw_file_size)[0]
    total_written = 0
    buffer = bytearray(MAX_BUF)
    view = memoryview(buffer)
    with open(file_path, "wb") as f:
        while total_written < file_size:
            read_size = min(file_size - total_written, MAX_BUF)
            received = sock.recv_into(view[:read_size])
            if not received:
                raise OSError("Client abruptly disconnected.")
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
            raise OSError("Client abruptly disconnected.")
        total_received += received
    return data
