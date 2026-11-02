import socket, struct

TCP_CIM = ('localhost', 10001)
UDP_CIM = ('localhost', 10002)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as t:
    t.connect(TCP_CIM)
    t.sendall(struct.pack('4s i', b'INCR', 0))
    tcp_ertek = int(t.recv(1024).decode())

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:
    u.settimeout(2)
    u.sendto(struct.pack('5s i', b'PLUS', 0), UDP_CIM)
    data, _ = u.recvfrom(1024)
    udp_ertek = struct.unpack('i', data)[0]

print('TCP:', tcp_ertek, '| UDP:', udp_ertek)
print('Az UDP szerver HIBÁZOTT' if tcp_ertek != udp_ertek else 'Egyeznek, nincs hiba')
