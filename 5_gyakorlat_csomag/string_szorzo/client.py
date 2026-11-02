import socket
import struct
import sys

request_packer = struct.Struct("20s i")

if len(sys.argv) != 5:
    sys.exit("Használat: python client.py <host> <port> <szöveg> <szorzó>")
server_addr = (sys.argv[1], int(sys.argv[2]))
text, count = sys.argv[3], int(sys.argv[4])

encoded = text.encode()
if len(encoded) > 20:
    sys.exit(f"A szöveg legfeljebb 20 byte lehet, ez {len(encoded)} byte")
if not 1 <= count <= 10:
    sys.exit("A szorzó 1 és 10 közötti egész szám legyen")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(server_addr)
    client.sendall(request_packer.pack(encoded, count))
    data = b""
    while chunk := client.recv(256):
        data += chunk
    print(data.decode())
