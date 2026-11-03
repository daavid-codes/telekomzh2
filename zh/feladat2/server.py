import select
import socket
import struct
import sys
from collections import defaultdict

port = int(sys.argv[1])

keres = struct.Struct("3s 6s 8s i")
valasz = struct.Struct("i")

# raktar -> termek -> darabszam
keszlet = defaultdict(lambda: defaultdict(int))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", port))
server.listen()

pufferek = {}

while True:
    olvashato, _, _ = select.select([server, *pufferek], [], [])
    for s in olvashato:
        if s is server:
            kliens, _ = server.accept()
            pufferek[kliens] = b""
            continue

        data = s.recv(1024)
        if not data:
            del pufferek[s]
            s.close()
            continue

        pufferek[s] += data
        while len(pufferek[s]) >= keres.size:
            uzenet, pufferek[s] = pufferek[s][:keres.size], pufferek[s][keres.size:]
            cmd, w, p, q = keres.unpack(uzenet)
            cmd = cmd.rstrip(b"\x00")
            w, p = w.rstrip(b"\x00"), p.rstrip(b"\x00")

            if cmd == b"ADD":
                keszlet[w][p] += q
                eredmeny = keszlet[w][p]
            elif cmd == b"GET":
                eredmeny = keszlet[w][p]
            else:  # TOT
                eredmeny = sum(keszlet[w].values())

            print(cmd.decode(), w.decode(), p.decode(), q, "->", eredmeny)
            s.sendall(valasz.pack(eredmeny))
