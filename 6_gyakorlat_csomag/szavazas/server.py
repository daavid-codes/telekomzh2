import select
import socket
import struct
import sys

request_packer = struct.Struct("4s i")
reply_packer = struct.Struct("i")

IDOPONTOK = range(1, 6)

szavazatok = {n: 0 for n in IDOPONTOK}
ki_mire = {}
pufferek = {}


def feldolgoz(sock, parancs, n):
    if parancs == "VOTE":
        if n not in IDOPONTOK:
            return -2
        if sock in ki_mire:
            return -1
        ki_mire[sock] = n
        szavazatok[n] += 1
        return szavazatok[n]

    if parancs == "UNDO":
        if n != 0:
            return -2
        if sock not in ki_mire:
            return -1
        regi = ki_mire.pop(sock)
        szavazatok[regi] -= 1
        return szavazatok[regi]

    if parancs == "STAT":
        if n == 0:
            return sum(szavazatok.values())
        if n in IDOPONTOK:
            return szavazatok[n]
        return -2

    return -2


def bont(sock, inputs):
    inputs.remove(sock)
    ki_mire.pop(sock, None)
    pufferek.pop(sock, None)
    sock.close()


def main():
    if len(sys.argv) != 2:
        print("Használat: python3 server.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("", port))
    srv.listen(10)
    inputs = [srv]
    print(f"Szavazószerver fut a {port}-es porton")

    while True:
        olvashato, _, _ = select.select(inputs, [], [], 1)
        for s in olvashato:
            if s is srv:
                conn, _ = srv.accept()
                inputs.append(conn)
                pufferek[conn] = b""
                continue

            try:
                data = s.recv(request_packer.size - len(pufferek[s]))
            except ConnectionError:
                data = b""
            if not data:
                bont(s, inputs)
                continue

            pufferek[s] += data
            if len(pufferek[s]) < request_packer.size:
                continue

            nyers_parancs, n = request_packer.unpack(pufferek[s])
            pufferek[s] = b""
            parancs = nyers_parancs.decode(errors="replace").strip("\x00")
            valasz = feldolgoz(s, parancs, n)
            print(f"{parancs} {n} -> {valasz}   {szavazatok}")
            try:
                s.sendall(reply_packer.pack(valasz))
            except ConnectionError:
                bont(s, inputs)


if __name__ == "__main__":
    main()
