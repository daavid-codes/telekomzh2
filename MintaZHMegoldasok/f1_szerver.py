import socket, struct, sys

HOST, PORT = 'localhost', 10000
FMT = '20s i'

def feldolgoz(data):
    szoveg, n = struct.unpack(FMT, data)
    szoveg = szoveg.decode().strip('\x00')
    valasz = szoveg[:n][::-1]
    return struct.pack(f'{n}s', valasz.encode())

mod = sys.argv[1] if len(sys.argv) > 1 else 'tcp'

if mod == 'tcp':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(5)
        while True:
            conn, addr = srv.accept()
            with conn:
                data = conn.recv(struct.calcsize(FMT))
                if data:
                    conn.sendall(feldolgoz(data))
else:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as srv:
        srv.bind((HOST, PORT))
        while True:
            data, addr = srv.recvfrom(1024)
            srv.sendto(feldolgoz(data), addr)
