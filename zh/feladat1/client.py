import socket
import struct
import sys

def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        more = sock.recv(size - len(data))
        if not more:
            raise EOFError("Socket closed before receiving all data")
        data += more
    return data

host, port = sys.argv[1], int(sys.argv[2])
neptun, jarat = b"EZQDD1", b"RZ65"

p = struct.Struct("6s 8s 7s")
valasz = struct.Struct("i 10s")
vegso = struct.Struct("12s")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    s.sendall(p.pack(neptun, jarat, b"request"))

    szam, osztaly = valasz.unpack(recv_exact(s, valasz.size))
    osztaly = osztaly.rstrip(b"\x00")
    print(f"Szabad helyek: {szam}, osztaly: {osztaly.decode()}")

    tipus = b"reserve" if szam >= 4 and osztaly == b"economy" else b"reject"
    s.sendall(p.pack(neptun, jarat, tipus))

    (azon,) = vegso.unpack(recv_exact(s, vegso.size))
    print("Foglalasi azonosito:", azon.rstrip(b"\x00").decode())
