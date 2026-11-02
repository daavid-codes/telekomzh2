import select
import socket
import struct
import sys
import time
from collections import deque

request = struct.Struct("3s")
reply = struct.Struct("i")

port, server_port = int(sys.argv[1]), int(sys.argv[2])
proxy_addr = ("localhost", port)
server_addr = ("localhost", server_port)

cache = {}
waiting = {}
asked = deque()
buffers = {}
backend_buf = b""


def connect_server():
    for _ in range(50):
        try:
            return socket.create_connection(server_addr)
        except ConnectionRefusedError:
            time.sleep(0.1)
    sys.exit(f"Nem érem el az árfolyam-szervert: {server_addr}")


def send_to(client, data):
    try:
        client.sendall(data)
    except OSError:
        pass


def close_client(sock, inputs):
    inputs.remove(sock)
    del buffers[sock]
    sock.close()


def handle_request(client, code):
    if code in cache:
        print(f"{code.decode()}: gyorsítótárból")
        send_to(client, cache[code])
    elif code in waiting:
        print(f"{code.decode()}: már úton van a szervertől, várakozik")
        waiting[code].append(client)
    else:
        print(f"{code.decode()}: új, megkérdezzük a szervert")
        waiting[code] = [client]
        asked.append(code)
        backend.sendall(request.pack(code))


def handle_backend():
    global backend_buf
    data = backend.recv(4096)
    if not data:
        sys.exit("Az árfolyam-szerver bontotta a kapcsolatot")
    backend_buf += data
    while len(backend_buf) >= reply.size:
        answer, backend_buf = backend_buf[:reply.size], backend_buf[reply.size:]
        code = asked.popleft()
        cache[code] = answer
        print(f"{code.decode()} = {reply.unpack(answer)[0]} (megjegyezve)")
        for client in waiting.pop(code):
            send_to(client, answer)


backend = connect_server()

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(proxy_addr)
        server.listen(5)
        print("Gyorsítótáras proxy fut:", proxy_addr, "->", server_addr)
        inputs = [server, backend]
        while True:
            readables, _, _ = select.select(inputs, [], [], 1.0)
            for s in readables:
                if s is server:
                    client, addr = server.accept()
                    inputs.append(client)
                    buffers[client] = b""
                    continue
                if s is backend:
                    handle_backend()
                    continue
                try:
                    chunk = s.recv(request.size - len(buffers[s]))
                except ConnectionError:
                    chunk = b""
                if not chunk:
                    close_client(s, inputs)
                    continue
                buffers[s] += chunk
                if len(buffers[s]) < request.size:
                    continue
                (code,) = request.unpack(buffers[s])
                buffers[s] = b""
                handle_request(s, code)
except KeyboardInterrupt:
    print("Proxy stopped")
finally:
    backend.close()
