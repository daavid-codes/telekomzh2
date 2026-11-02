import socket, select, struct

HOST, PORT = 'localhost', 10001
FMT = '4s i'
MERET = struct.calcsize(FMT)

ertek = 0

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((HOST, PORT))
srv.listen(5)
inputs = [srv]

while True:
    olvashato, _, _ = select.select(inputs, [], [], 1)
    for s in olvashato:
        if s is srv:
            conn, addr = srv.accept()
            inputs.append(conn)
            print('Csatlakozott:', addr)
            continue
        try:
            data = s.recv(MERET)
        except ConnectionResetError:
            data = b''
        if not data:
            inputs.remove(s)
            s.close()
            continue
        parancs, x = struct.unpack(FMT, data)
        parancs = parancs.decode().strip('\x00')
        if parancs == 'IN':
            ertek = x
        elif parancs == 'INCR':
            ertek += x
        elif parancs == 'DECR':
            ertek -= x
        print(parancs, x, '->', ertek)
        s.sendall(str(ertek).encode())
