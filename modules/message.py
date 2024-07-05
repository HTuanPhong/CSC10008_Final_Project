"""Useful funtion for client to interact with server protocol

file_path is file path relative to server's root not path on our machine.
"""

import struct
import json
from socket import AF_INET, socket, SOCK_STREAM
from modules.shared import *


def send_RRQ(address, file_path):
    """send Read request"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)
    sock.sendall(struct.pack(">BB", RRQ, len(file_path)) + file_path.encode("utf-8"))
    result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]
    size = None
    if result_opcode:
        size = struct.unpack(">Q", recv_all(sock, 8))[0]
    sock.close()
    return result_opcode, size


def send_WRQ(address, file_path, size):
    """send Write request"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)
    sock.sendall(
        struct.pack(">BB", WRQ, len(file_path))
        + file_path.encode("utf-8")
        + struct.pack(">Q", size)
    )
    result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]
    sock.close()
    return result_opcode


def send_DRRQ(address, file_path, offset, count):
    """send Data read request"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)
    sock.sendall(
        struct.pack(">BB", DRRQ, len(file_path))
        + file_path.encode("utf-8")
        + struct.pack(">QQ", offset, count)
    )
    result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]
    data = None
    if result_opcode:
        data = recv_all(sock, count)
    sock.close()
    return result_opcode, data


def send_DWRQ(address, file_path, offset, length, local_file_path):
    """send Data write request"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)
    sock.sendall(
        struct.pack(">BB", DWRQ, len(file_path))
        + file_path.encode("utf-8")
        + struct.pack(">QQ", offset, length)
    )
    with open(local_file_path, "rb") as f:
        sock.sendfile(f, offset, length)
    result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]
    sock.close()
    return result_opcode


def send_FWRQ(address, file_path):
    """send Finish write request"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)
    sock.sendall(struct.pack(">BB", FWRQ, len(file_path)) + file_path.encode("utf-8"))
    result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]
    sock.close()
    return result_opcode


def send_DRQ(address, file_path):
    """send Delete request"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)
    sock.sendall(struct.pack(">BB", DRQ, len(file_path)) + file_path.encode("utf-8"))
    result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]
    sock.close()
    return result_opcode


def send_DTRQ(address):
    """send Directory request"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)
    sock.sendall(struct.pack(">B", DTRQ))
    result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]
    directory_dict = None
    if result_opcode:
        data_length = struct.unpack(">I", recv_all(sock, 4))[0]
        directory_dict = json.loads(recv_all(sock, data_length).decode("utf-8"))
    sock.close()
    return result_opcode, directory_dict


def send_FRQ(address, path):
    """send Create folder request"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)
    sock.sendall(struct.pack(">BB", FRQ, len(path)) + path.encode("utf-8"))
    result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]
    sock.close()
    return result_opcode
