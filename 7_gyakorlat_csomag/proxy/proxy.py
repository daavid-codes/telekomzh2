import select
import socket
import struct
import sys
import time

request = struct.Struct("i i c")
backend_req = struct.Struct("i i")
reply = struct.Struct("i")

port, add_port, mul_port = (int(x) for x in sys.argv[1:4])
proxy_addr = ("localhost", port)
adder_addr = ("localhost", add_port)
mul_addr = ("localhost", mul_port)


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


def connect_mul():
    for _ in range(50):
        try:
            return socket.create_connection(mul_addr)
        except ConnectionRefusedError:
            time.sleep(0.1)
    sys.exit(f"Nem érem el a szorzó szervert: {mul_addr}")


def add_udp(msg):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp:
        udp.settimeout(1.0)
        while True:
            udp.sendto(msg, adder_addr)
            try:
                answer, _ = udp.recvfrom(1024)
                if len(answer) == reply.size:
                    return answer
            except TimeoutError:
                print("Nincs válasz, újraküldés")


def mul_tcp(msg):
    global mul_sock
    mul_sock.sendall(msg)
    answer = recv_exact(mul_sock, reply.size)
    if not answer:
        mul_sock.close()
        mul_sock = connect_mul()
        mul_sock.sendall(msg)
        answer = recv_exact(mul_sock, reply.size)
    return answer


mul_sock = connect_mul()

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(proxy_addr)
        server.listen(5)
        print(f"Proxy fut: {proxy_addr}  + -> UDP {adder_addr}  * -> TCP {mul_addr}")
        inputs = [server]
        buffers = {}
        while True:
            readables, _, _ = select.select(inputs, [], [], 1.0)
            for s in readables:
                if s is server:
                    client, addr = server.accept()
                    print(f"New client: {addr[0]}:{addr[1]}")
                    inputs.append(client)
                    buffers[client] = b""
                    continue
                try:
                    chunk = s.recv(request.size - len(buffers[s]))
                except ConnectionError:
                    chunk = b""
                if not chunk:
                    inputs.remove(s)
                    del buffers[s]
                    s.close()
                    continue
                buffers[s] += chunk
                if len(buffers[s]) < request.size:
                    continue
                a, b, op = request.unpack(buffers[s])
                buffers[s] = b""
                msg = backend_req.pack(a, b)
                if op == b"+":
                    answer = add_udp(msg)
                elif op == b"*":
                    answer = mul_tcp(msg)
                else:
                    print(f"Ismeretlen művelet: {op!r}, bontás")
                    inputs.remove(s)
                    del buffers[s]
                    s.close()
                    continue
                (result,) = reply.unpack(answer)
                print(f"{a} {op.decode()} {b} = {result}")
                s.sendall(answer)
except KeyboardInterrupt:
    print("Proxy stopped")
finally:
    mul_sock.close()
