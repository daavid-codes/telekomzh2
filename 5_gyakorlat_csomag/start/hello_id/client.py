import socket
import struct
import sys

packer = struct.Struct("12s i")

if len(sys.argv) != 4:
    sys.exit("Használat: python client.py <host> <port> <azonosító 1-10>")
server_addr = (sys.argv[1], int(sys.argv[2]))
user_id = int(sys.argv[3])
if not 1 <= user_id <= 10:
    sys.exit("Az azonosító 1 és 10 közötti egész szám legyen")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(server_addr)
    client.sendall(packer.pack("Hello server".encode(), user_id))
    data = client.recv(64)
    print("Received:", data.decode())
