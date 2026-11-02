import socket
import struct
import sys

packer = struct.Struct("i i c")


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


def main():
    if len(sys.argv) != 6:
        sys.exit("Használat: python client.py <host> <port> <a> <op> <b>   (szorzás: x vagy '*')")
    host, port = sys.argv[1], int(sys.argv[2])
    a, op, b = int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
    op = "*" if op == "x" else op
    if op not in ("+", "-", "*", "/"):
        sys.exit(f"Ismeretlen művelet: {op}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host, port))
        client.sendall(packer.pack(a, b, op.encode()))
        data = recv_exact(client, packer.size)

    if not data:
        sys.exit("A szerver nem válaszolt (érvénytelen művelet?)")
    result, _, mark = packer.unpack(data)
    print(f"{a} {op} {b} = {result}")


if __name__ == "__main__":
    main()
