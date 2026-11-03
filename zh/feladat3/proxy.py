import select
import socket
import struct
import sys

port, szerver_port = int(sys.argv[1]), int(sys.argv[2])
szerver = ("localhost", szerver_port)

kliens_uzenet = struct.Struct("i 20s")
szerver_uzenet = struct.Struct("5s 20s")
TIPUSOK = {0: b"LOGIN", 1: b"GUEST"}

proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy.bind(("", port))
proxy.listen()

# minden TCP kliensnek saját UDP socketje van, így a válaszok nem keverednek
pufferek = {}  # tcp kliens -> beérkezett bájtok
udp_kliens = {}  # udp socket -> tcp kliens
kliens_udp = {}  # tcp kliens -> udp socket


def lezar(kliens):
    u = kliens_udp.pop(kliens)
    del udp_kliens[u], pufferek[kliens]
    u.close()
    kliens.close()


while True:
    olvashato, _, _ = select.select([proxy, *pufferek, *udp_kliens], [], [])
    for s in olvashato:
        if s is proxy:
            kliens, _ = proxy.accept()
            u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            pufferek[kliens] = b""
            udp_kliens[u], kliens_udp[kliens] = kliens, u

        elif s in udp_kliens:
            data, _ = s.recvfrom(4096)
            udp_kliens[s].sendall(data)

        elif s in pufferek:
            data = s.recv(1024)
            if not data:
                lezar(s)
                continue
            pufferek[s] += data
            while len(pufferek[s]) >= kliens_uzenet.size:
                uzenet, pufferek[s] = pufferek[s][:kliens_uzenet.size], pufferek[s][kliens_uzenet.size:]
                tipus, nev = kliens_uzenet.unpack(uzenet)
                print(tipus, nev.rstrip(b"\x00").decode())
                kliens_udp[s].sendto(szerver_uzenet.pack(TIPUSOK[tipus], nev), szerver)
