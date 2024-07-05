import socket
import os


IP = socket.gethostbyname(socket.gethostname())
PORT = 2024
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
PATH = "Sever_Data"

def main():

     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     server.bind(ADDR)
     server.listen(1) 

     while True:
          conn, addr = server.accept()
          data = conn.recv(1024)

          with open(os.path.join(PATH, "file.txt"), 'wb') as file:
               file.write(data)

          conn.close()

if __name__ == "__main__":
    main()
