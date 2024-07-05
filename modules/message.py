"""Useful funtion for client to interact with server protocol"""

import struct
from modules.shared import *


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
