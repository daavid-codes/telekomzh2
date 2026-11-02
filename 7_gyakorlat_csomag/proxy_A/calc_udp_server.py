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
server_addr = ("localhost", int(sys.argv[1]))

try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(server_addr)
        sock.settimeout(1.0)
        print("UDP számológép fut:", server_addr)
        while True:
            try:
                data, client = sock.recvfrom(1024)
            except TimeoutError:
                continue
            if len(data) != packer.size:
                print(f"{client}: {len(data)} byte jött, {packer.size} kellene")
                continue
            a, b, op = packer.unpack(data)
            if op not in ops or (op == b"/" and b == 0):
                print(f"{client}: érvénytelen művelet: {a} {op!r} {b}")
                continue
            result = ops[op](a, b)
            print(f"{client}: {a} {op.decode()} {b} = {result}")
            sock.sendto(packer.pack(result, 0, b"R"), client)
except KeyboardInterrupt:
    print("Server stopped")
