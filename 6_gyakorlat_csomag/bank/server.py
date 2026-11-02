import select
import socket
import struct
import sys

request_packer = struct.Struct("2s i i")
reply_packer = struct.Struct("i")

egyenlegek = {}

pufferek = {}


def feldolgoz(parancs, azonosito, osszeg):
    egyenleg = egyenlegek.get(azonosito, 0)
    if parancs == b"BE":
        egyenleg += osszeg
    elif parancs == b"KI":
        egyenleg -= osszeg
    else:
        return None
    egyenlegek[azonosito] = egyenleg
    return egyenleg


def bont(sock, inputs):
    inputs.remove(sock)
    pufferek.pop(sock, None)
    sock.close()


def main():
    if len(sys.argv) != 2:
        print("Használat: python server.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("", port))
    srv.listen(10)
    inputs = [srv]
    print(f"Bankszerver fut a {port}-es porton")

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

            parancs, azonosito, osszeg = request_packer.unpack(pufferek[s])
            pufferek[s] = b""
            egyenleg = feldolgoz(parancs, azonosito, osszeg)
            if egyenleg is None:
                print(f"Ismeretlen parancs: {parancs!r}, bontás")
                bont(s, inputs)
                continue
            print(f"{parancs.decode(errors='replace')} {azonosito} {osszeg} -> {egyenleg}")
            try:
                s.sendall(reply_packer.pack(egyenleg))
            except ConnectionError:
                bont(s, inputs)


if __name__ == "__main__":
    main()
