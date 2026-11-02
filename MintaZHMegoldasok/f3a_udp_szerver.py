import socket, struct, random, sys

HOST, PORT = 'localhost', 10002
FMT = '5s i'
HIBAS = len(sys.argv) > 1 and sys.argv[1] == 'hibas'

ertek = 0
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as srv:
    srv.bind((HOST, PORT))
    while True:
        data, addr = srv.recvfrom(1024)
        parancs, x = struct.unpack(FMT, data)
        parancs = parancs.decode().strip('\x00')
        if HIBAS:
            x += random.choice([-1, 0, 1])
        if parancs == 'PUSH':
            ertek = x
        elif parancs == 'PLUS':
            ertek += x
        elif parancs == 'MINUS':
            ertek -= x
        print(parancs, x, '->', ertek)
        srv.sendto(struct.pack('i', ertek), addr)
