import socket
import struct
import sys

tipp_packer = struct.Struct("6s i i")
valasz_packer = struct.Struct("c 10s")
azonosito_packer = struct.Struct("6s 10s i")
kod_packer = struct.Struct("12s")


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            sys.exit("A szerver bontotta a kapcsolatot")
        data += chunk
    return data


def main():
    if len(sys.argv) != 4:
        sys.exit("Használat: python client.py <host> <port> <NEPTUN>")
    host, port, neptun = sys.argv[1], int(sys.argv[2]), sys.argv[3].upper().encode()

    with socket.create_connection((host, port)) as sock:
        kuldesek = 0

        def tippel(szam):
            nonlocal kuldesek
            kuldesek += 1
            sock.sendall(tipp_packer.pack(neptun, szam, kuldesek))
            jel, azonosito = valasz_packer.unpack(recv_exact(sock, valasz_packer.size))
            print(f"{kuldesek}. tipp: {szam} -> {jel.decode()}")
            return jel, azonosito

        also, felso = 1, 100
        while also < felso:
            kozep = (also + felso) // 2
            jel, azonosito = tippel(kozep)
            if jel == b"<":
                felso = kozep - 1
            elif jel == b">":
                also = kozep + 1
            elif jel == b"=":
                break
            else:
                sys.exit(f"Váratlan válasz: {jel!r}")
        else:
            jel, azonosito = tippel(also)
            if jel != b"=":
                sys.exit(f"A szám {also} kellene legyen, de a válasz: {jel!r}")

        kuldesek += 1
        sock.sendall(azonosito_packer.pack(neptun, azonosito, kuldesek))
        (kod,) = kod_packer.unpack(recv_exact(sock, kod_packer.size))
        print(kod.rstrip(b"\x00").decode())


if __name__ == "__main__":
    main()
