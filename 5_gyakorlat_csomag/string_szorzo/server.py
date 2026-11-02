import socket
import struct
import sys

request_packer = struct.Struct("20s i")
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
    sock.listen(5)
    sock.settimeout(1.0)
    print("String szorzó szerver fut:", server_addr)

    try:
        while True:
            try:
                client, client_addr = sock.accept()
            except TimeoutError:
                continue
            with client:
                data = recv_exact(client, request_packer.size)
                if not data:
                    continue
                raw_text, count = request_packer.unpack(data)
                text = raw_text.rstrip(b"\x00").decode(errors="replace")
                if not 1 <= count <= 10:
                    print(f"{client_addr}: érvénytelen szorzó: {count}")
                    continue
                result = text * count
                print(f"{client_addr}: {text!r} x {count} -> {result!r}")
                client.sendall(result.encode())
    except KeyboardInterrupt:
        print("Server stopped")
