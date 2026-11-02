import socket, struct, random, json, sys

HOST, PORT = 'localhost', 10000
FMT = '20s i'

def kuld_tcp(szoveg, n):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(struct.pack(FMT, szoveg.encode(), n))
        data = s.recv(1024)
    return struct.unpack(f'{n}s', data)[0].decode().strip('\x00')

def kuld_udp(szoveg, n):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2)
        s.sendto(struct.pack(FMT, szoveg.encode(), n), (HOST, PORT))
        data, _ = s.recvfrom(1024)
    return struct.unpack(f'{n}s', data)[0].decode().strip('\x00')

valtozat = sys.argv[1] if len(sys.argv) > 1 else 'a'

if valtozat in ('a', 'd'):
    szoveg = input('Szöveg: ')
    n = random.randint(1, len(szoveg))
elif valtozat == 'b':
    with open('input.txt') as f:
        sorok = f.read().splitlines()
    sor = sorok[random.randint(1, 3) - 1]
    szoveg, n = sor.split()
    n = int(n)
elif valtozat == 'c':
    with open('input.json') as f:
        adat = json.load(f)
    kulcs = str(random.randint(1, 3))
    szoveg, n = adat[kulcs]

kuld = kuld_udp if valtozat == 'd' else kuld_tcp
print(f'{szoveg},{n} -> {kuld(szoveg, n)}')
