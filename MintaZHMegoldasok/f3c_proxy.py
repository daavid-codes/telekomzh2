import socket, select, struct

TCP_CIM = ('localhost', 10003)
UDP_CIM = ('localhost', 10002)
FORDITAS = {'IN': 'PUSH', 'INCR': 'PLUS', 'DECR': 'MINUS'}
MERET = struct.calcsize('4s i')

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(TCP_CIM)
srv.listen(5)

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.settimeout(2)

inputs = [srv]
while True:
    olvashato, _, _ = select.select(inputs, [], [], 1)
    for s in olvashato:
        if s is srv:
            conn, _ = srv.accept()
            inputs.append(conn)
            continue
        try:
            data = s.recv(MERET)
        except ConnectionResetError:
            data = b''
        if not data:
            inputs.remove(s)
            s.close()
            continue
        parancs, x = struct.unpack('4s i', data)
        parancs = parancs.decode().strip('\x00')
        udp.sendto(struct.pack('5s i', FORDITAS[parancs].encode(), x), UDP_CIM)
        valasz, _ = udp.recvfrom(1024)
        ertek = struct.unpack('i', valasz)[0]
        s.sendall(str(ertek).encode())
