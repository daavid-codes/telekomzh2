import select
import socket
import struct
import sys

packer = struct.Struct("i i c")

proxy_addr = ("localhost", int(sys.argv[1]))
server_addr = ("localhost", int(sys.argv[2]))


def ask_udp(msg):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp:
        udp.settimeout(1.0)
        while True:
            udp.sendto(msg, server_addr)
            try:
                answer, _ = udp.recvfrom(1024)
                return answer
            except TimeoutError:
                print("Nincs válasz, újraküldés")


try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(proxy_addr)
        server.listen(5)
        print("Proxy fut:", proxy_addr, "-> UDP", server_addr)
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
                    chunk = s.recv(packer.size - len(buffers[s]))
                except ConnectionError:
                    chunk = b""
                if not chunk:
                    inputs.remove(s)
                    del buffers[s]
                    s.close()
                    continue
                buffers[s] += chunk
                if len(buffers[s]) < packer.size:
                    continue
                msg, buffers[s] = buffers[s], b""
                answer = ask_udp(msg)
                print(f"{packer.unpack(msg)} -> {packer.unpack(answer)}")
                s.sendall(answer)
except KeyboardInterrupt:
    print("Proxy stopped")
