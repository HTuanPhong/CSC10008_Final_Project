"""Useful funtion for client to interact with server protocol

file_path is file path relative to server's root not path on our machine.
"""

import struct
import json
import threading
from socket import AF_INET, socket, SOCK_STREAM, SHUT_RDWR
from modules.shared import *
from queue import Queue

FORMAT = DEFAULT_FORMAT

lock = threading.Lock()
messengers = []


def disconnect_all():
    with lock:
        global messengers
        for msgr in messengers:
            msgr.shutdown()
        messengers = []


class messengerError(Exception):
    pass


class messenger:
    def __init__(self, host, port):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((host, port))
        with lock:
            messengers.append(self)

    def _raise_err(self):
        err_len = struct.unpack(">B", recv_all(self.sock, 1))[0]
        err_msg = recv_all(self.sock, err_len).decode(FORMAT)
        raise messengerError(err_msg)

    def send_RRQ(self, file_path):
        """send Read request"""
        self.sock.sendall(
            struct.pack(">BB", RRQ, len(file_path)) + file_path.encode(FORMAT)
        )
        result_opcode = struct.unpack(">B", recv_all(self.sock, 1))[0]

        if result_opcode == SUCCESS:
            return struct.unpack(">Q", recv_all(self.sock, 8))[0]
        else:
            self._raise_err()

    def send_WRQ(self, file_path, size):
        """send Write request"""
        self.sock.sendall(
            struct.pack(">BB", WRQ, len(file_path))
            + file_path.encode(FORMAT)
            + struct.pack(">Q", size)
        )
        result_opcode = struct.unpack(">B", recv_all(self.sock, 1))[0]

        if result_opcode == ERROR:
            self._raise_err()

    def send_DRRQ(self, file_path, offset, length, local_file_path):
        """send Data read request"""
        self.sock.sendall(
            struct.pack(">BB", DRRQ, len(file_path))
            + file_path.encode(FORMAT)
            + struct.pack(">QQ", offset, length)
        )
        result_opcode = struct.unpack(">B", recv_all(self.sock, 1))[0]

        if result_opcode == SUCCESS:
            return recv_data(self.sock, local_file_path, offset, length)
        else:
            self._raise_err()

    def send_DWRQ(self, file_path, offset, length, local_file_path):
        """send Data write request"""
        self.sock.sendall(
            struct.pack(">BB", DWRQ, len(file_path))
            + file_path.encode(FORMAT)
            + struct.pack(">QQ", offset, length)
        )
        with open(local_file_path, "rb") as f:
            self.sock.sendfile(f, offset, length)
        result_opcode = struct.unpack(">B", recv_all(self.sock, 1))[0]

        if result_opcode == ERROR:
            self._raise_err()

    def send_FWRQ(self, file_path):
        """send Finish write request"""
        self.sock.sendall(
            struct.pack(">BB", FWRQ, len(file_path)) + file_path.encode(FORMAT)
        )
        result_opcode = struct.unpack(">B", recv_all(self.sock, 1))[0]
        if result_opcode == ERROR:
            self._raise_err()

    def send_DRQ(self, file_path):
        """send Delete request"""
        self.sock.sendall(
            struct.pack(">BB", DRQ, len(file_path)) + file_path.encode(FORMAT)
        )
        result_opcode = struct.unpack(">B", recv_all(self.sock, 1))[0]
        if result_opcode == ERROR:
            self._raise_err()

    def sub_DTRQ(self):
        """send Directory subcribe"""
        self.sock.sendall(struct.pack(">B", DTRQ))

    def recv_DTRQ(self):
        """receive Directory"""
        result_opcode = struct.unpack(">B", recv_all(self.sock, 1))[0]
        if result_opcode == SUCCESS:
            data_length = struct.unpack(">I", recv_all(self.sock, 4))[0]
            directory_dict = json.loads(recv_all(self.sock, data_length).decode(FORMAT))
            return directory_dict
        else:
            self._raise_err()

    def send_FRQ(self, path):
        """send Create folder request"""
        self.sock.sendall(struct.pack(">BB", FRQ, len(path)) + path.encode(FORMAT))
        result_opcode = struct.unpack(">B", recv_all(self.sock, 1))[0]
        if result_opcode == ERROR:
            self._raise_err()

    def shutdown(self):
        if self.sock:
            self.sock.shutdown(SHUT_RDWR)

    def close(self):
        if self.sock:
            self.sock.close()
        with lock:
            if self in messengers:
                messengers.remove(self)
