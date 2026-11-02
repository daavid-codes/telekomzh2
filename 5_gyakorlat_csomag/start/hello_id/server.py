import json
import os
import socket
import struct
import sys

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
with open(USERS_FILE, encoding="utf-8") as f:
    USERS = json.load(f)

packer = struct.Struct("12s i")
server_addr = ("localhost", int(sys.argv[1]))


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_addr)
    sock.listen(1)
    sock.settimeout(1.0)

    try:
        while True:
            try:
                client, client_addr = sock.accept()
                print(f"Connected: {client_addr[0]}:{client_addr[1]}")
                with client:
                    data = recv_exact(client, packer.size)
                    if not data:
                        continue
                    greeting, user_id = packer.unpack(data)
                    print(f"Received: {greeting.decode()} from user {user_id}")
                    name = USERS.get(str(user_id), "ismeretlen")
                    client.sendall(f"Hello {name}".encode())
            except TimeoutError:
                pass
    except KeyboardInterrupt:
        print("Server stopped")
