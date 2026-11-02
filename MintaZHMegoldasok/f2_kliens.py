import socket, struct, sys

HOST = 'localhost'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    for parancs, x in [('IN', 20), ('INCR', 4), ('DECR', 5)]:
        s.sendall(struct.pack('4s i', parancs.encode(), x))
        print(parancs, x, '->', s.recv(1024).decode())
