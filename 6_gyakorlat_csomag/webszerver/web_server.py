import mimetypes
import os
import select
import socket
import sys
from urllib.parse import unquote

VEGE = b"\r\n\r\n"
MAX_KERES = 64 * 1024

def valasz(status, body=b"", content_type="text/plain; charset=utf-8"):
    fejlec = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    return fejlec.encode() + body


def hiba_oldal(status):
    body = f"<html><body><h1>{status}</h1></body></html>".encode()
    return valasz(status, body, "text/html; charset=utf-8")


def kiszolgal(keres, gyoker):
    try:
        elso_sor = keres.split(b"\r\n", 1)[0].decode("ascii")
        metodus, utvonal, _verzio = elso_sor.split(" ")
    except ValueError:
        return hiba_oldal("400 Bad Request")

    print(elso_sor)
    if metodus != "GET":
        return hiba_oldal("405 Method Not Allowed")

    utvonal = unquote(utvonal.split("?", 1)[0])
    if utvonal.endswith("/"):
        utvonal += "index.html"

    fajl = os.path.realpath(os.path.join(gyoker, utvonal.lstrip("/")))
    if not fajl.startswith(gyoker + os.sep) or not os.path.isfile(fajl):
        return hiba_oldal("404 Not Found")

    with open(fajl, "rb") as f:
        tartalom = f.read()
    tipus = mimetypes.guess_type(fajl)[0] or "application/octet-stream"
    if tipus.startswith("text/"):
        tipus += "; charset=utf-8"
    return valasz("200 OK", tartalom, tipus)


def bont(sock, inputs, pufferek):
    inputs.remove(sock)
    pufferek.pop(sock, None)
    sock.close()


def main():
    if len(sys.argv) != 4:
        print("Használat: python web_server.py <host> <port> <mappa>")
        sys.exit(1)
    host, port = sys.argv[1], int(sys.argv[2])
    gyoker = os.path.realpath(sys.argv[3])

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(10)
    inputs = [srv]
    pufferek = {}
    print(f"Webszerver: http://{host}:{port}/index.html  (mappa: {gyoker})")

    while True:
        olvashato, _, _ = select.select(inputs, [], [], 1)
        for s in olvashato:
            if s is srv:
                conn, _ = srv.accept()
                inputs.append(conn)
                pufferek[conn] = b""
                continue

            try:
                data = s.recv(4096)
            except ConnectionError:
                data = b""
            if not data:
                bont(s, inputs, pufferek)
                continue

            pufferek[s] += data
            if VEGE not in pufferek[s]:
                if len(pufferek[s]) > MAX_KERES:
                    s.sendall(hiba_oldal("400 Bad Request"))
                    bont(s, inputs, pufferek)
                continue

            keres = pufferek[s].split(VEGE, 1)[0]
            try:
                s.sendall(kiszolgal(keres, gyoker))
            except ConnectionError:
                pass
            bont(s, inputs, pufferek)


if __name__ == "__main__":
    main()
