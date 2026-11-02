import socket
import struct
import sys

packer = struct.Struct("i i c")
ops = {
    b"+": lambda a, b: a + b,
    b"-": lambda a, b: a - b,
    b"*": lambda a, b: a * b,
    b"/": lambda a, b: a // b,
}


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


def main():
    if len(sys.argv) != 2:
        sys.exit("Használat: python server.py <port>")
    server_addr = ("", int(sys.argv[1]))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_addr)
        sock.listen(5)
        sock.settimeout(1.0)
        print("Számológép szerver fut:", server_addr)

        try:
            while True:
                try:
                    client, client_addr = sock.accept()
                except TimeoutError:
                    continue
                with client:
                    try:
                        data = recv_exact(client, packer.size)
                    except ConnectionError:
                        continue
                    if not data:
                        continue
                    a, b, op = packer.unpack(data)
                    if op not in ops or (op == b"/" and b == 0):
                        print(f"{client_addr}: érvénytelen művelet: {a} {op!r} {b}")
                        continue
                    result = ops[op](a, b)
                    print(f"{client_addr}: {a} {op.decode()} {b} = {result}")
                    client.sendall(packer.pack(result, 0, b"R"))
        except KeyboardInterrupt:
            print("Server stopped")


if __name__ == "__main__":
    main()
