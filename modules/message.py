"""Useful funtion for client to interact with server protocol

file_path is file path relative to server's root not path on our machine.
"""

# change all send method to raise exception when there is error
import struct
import json
from socket import AF_INET, socket, SOCK_STREAM
from modules.shared import *

FORMAT = DEFAULT_FORMAT


def raise_err(sock):
    err_len = struct.unpack(">B", recv_all(sock, 1))[0]
    err_msg = recv_all(sock, err_len).decode(FORMAT)

    if err_msg in ERROR_CODES:
        raise ERROR_CODES[err_msg]

    else:
        raise OSError(err_msg)


def send_RRQ(address, file_path):
    """send Read request"""
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect(address)
        sock.sendall(struct.pack(">BB", RRQ, len(file_path)) + file_path.encode(FORMAT))
        result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]

        if result_opcode == SUCCESS:
            return struct.unpack(">Q", recv_all(sock, 8))[0]
        else:
            raise_err(sock)
    finally:
        sock.close()
    return None


def send_WRQ(address, file_path, size):
    """send Write request"""
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect(address)
        sock.sendall(
            struct.pack(">BB", WRQ, len(file_path))
            + file_path.encode(FORMAT)
            + struct.pack(">Q", size)
        )
        result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]

        if result_opcode == ERROR:
            raise_err(sock)
    finally:
        sock.close()


# file_path is from server, offset, count is byte
def send_DRRQ(address, file_path, offset, count):
    """send Data read request"""
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect(address)
        sock.sendall(
            struct.pack(">BB", DRRQ, len(file_path))
            + file_path.encode(FORMAT)
            + struct.pack(">QQ", offset, count)
        )
        result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]

        if result_opcode == SUCCESS:
            return recv_all(sock, count)
        else:
            raise_err(sock)
    finally:
        sock.close()
    return None


def send_DWRQ(address, file_path, offset, length, local_file_path):
    """send Data write request"""
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect(address)
        sock.sendall(
            struct.pack(">BB", DWRQ, len(file_path))
            + file_path.encode(FORMAT)
            + struct.pack(">QQ", offset, length)
        )
        with open(local_file_path, "rb") as f:
            sock.sendfile(f, offset, length)
        result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]

        if result_opcode == ERROR:
            raise_err(sock)
    finally:
        sock.close()


def send_FWRQ(address, file_path):
    """send Finish write request"""
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect(address)
        sock.sendall(
            struct.pack(">BB", FWRQ, len(file_path)) + file_path.encode(FORMAT)
        )
        result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]
        if result_opcode == ERROR:
            raise_err(sock)
    finally:
        sock.close()


def send_DRQ(address, file_path):
    """send Delete request"""
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect(address)
        sock.sendall(struct.pack(">BB", DRQ, len(file_path)) + file_path.encode(FORMAT))
        result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]
        error_msg = ""
        if result_opcode == ERROR:
            raise_err(sock)
    finally:
        sock.close()


def send_DTRQ(address):
    """send Directory request"""
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect(address)
        sock.sendall(struct.pack(">B", DTRQ))
        result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]

        if result_opcode:
            data_length = struct.unpack(">I", recv_all(sock, 4))[0]
            directory_dict = json.loads(recv_all(sock, data_length).decode(FORMAT))
            return directory_dict
        else:
            raise_err(sock)
    finally:
        sock.close()
    return None


def send_FRQ(address, path):
    """send Create folder request"""
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect(address)
        sock.sendall(struct.pack(">BB", FRQ, len(path)) + path.encode(FORMAT))
        result_opcode = struct.unpack(">B", recv_all(sock, 1))[0]
        if not result_opcode:
            raise_err(sock)
    finally:
        sock.close()
