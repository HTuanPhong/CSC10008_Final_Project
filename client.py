"""Client demo"""

from socket import AF_INET, socket, SOCK_STREAM  # Stream mean TCP
import modules.message as msg

HOST = "172.0.0.1"  # IP adress server
PORT = 1234  # Port is used by the server
ADDR = (HOST, PORT)
FORMAT = "utf-8"

file_path = "random_server.txt"  # the file is in same dir as server chosen root
local_file_path = "random.txt"  # the file is in same dir as client.py
# remember these path are not the same
# first is a request to upload to server
# single thread example but the two send_DWRQ below can run on 2 thread.
# should error check with if and redo it but i want example to be simple.
msg.send_WRQ(ADDR, file_path, 25)  # calculate file size with os module instead.
msg.send_DWRQ(ADDR, file_path, 12, 13, local_file_path)  # write at index 12 to end
#### you can stop here and check the server's .uploading file on hex editor to confirm.
msg.send_DWRQ(ADDR, file_path, 0, 12, local_file_path)  # write at index 0 to 11
msg.send_FWRQ(ADDR, file_path)  # we done.

# get server's directory layout
result, dir_dict = msg.send_DTRQ(ADDR)
print(dir_dict)

# now we download a file
file_path = dir_dict["."]["files"][0]
# get first file in directory (should be random.txt if the dir is empty before this script run.)
res, size = msg.send_RRQ(ADDR, file_path)  # remember to handle the result.
res, data = msg.send_DRRQ(ADDR, file_path, 0, size)
# we just order entire file data here but you can order in chunks and multi thread this.
with open("random_from_server.txt", "wb") as f:
    f.write(data)


"""
at the end of this run you should see a random_server.txt in server directory.
assuming the server dir is empty before we run this code:
a random_from_server.txt in same directory as client.py 
with same data as random.txt
The second time you run this send_WRQ will error because file already exist on server.
"""
