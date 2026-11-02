import os
import socket
import struct
import sys

HEADER = struct.Struct("!HHI12s")
ATTR_HEADER = struct.Struct("!HH")
XOR_ADDR = struct.Struct("!BBHI")

BINDING_REQUEST = 0x0001
BINDING_RESPONSE = 0x0101
MAGIC_COOKIE = 0x2112A442
MAPPED_ADDRESS = 0x0001
XOR_MAPPED_ADDRESS = 0x0020
IPV4 = 1
MAX_TRIES = 8


def build_request():
    transaction_id = os.urandom(12)
    return HEADER.pack(BINDING_REQUEST, 0, MAGIC_COOKIE, transaction_id), transaction_id


def parse_response(data, transaction_id):
    if len(data) < HEADER.size:
        return None
    msg_type, length, cookie, tid = HEADER.unpack_from(data)
    if msg_type != BINDING_RESPONSE or cookie != MAGIC_COOKIE or tid != transaction_id:
        return None

    plain = None
    pos, end = HEADER.size, min(HEADER.size + length, len(data))
    while pos + ATTR_HEADER.size <= end:
        attr_type, attr_len = ATTR_HEADER.unpack_from(data, pos)
        value = data[pos + ATTR_HEADER.size: pos + ATTR_HEADER.size + attr_len]
        if attr_type in (XOR_MAPPED_ADDRESS, MAPPED_ADDRESS) and len(value) >= XOR_ADDR.size:
            _, family, port, ip = XOR_ADDR.unpack_from(value)
            if family == IPV4:
                if attr_type == XOR_MAPPED_ADDRESS:
                    port ^= MAGIC_COOKIE >> 16
                    ip ^= MAGIC_COOKIE
                    return socket.inet_ntoa(struct.pack("!I", ip)), port
                plain = socket.inet_ntoa(struct.pack("!I", ip)), port
        pos += ATTR_HEADER.size + (attr_len + 3) // 4 * 4
    return plain


def main():
    if len(sys.argv) != 3:
        sys.exit("Használat: python client.py <host> <port>")
    try:
        server = (socket.gethostbyname(sys.argv[1]), int(sys.argv[2]))
    except socket.gaierror:
        sys.exit(f"Nem található a szerver: {sys.argv[1]}")
    request, transaction_id = build_request()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(1.0)
        for _ in range(MAX_TRIES):
            sock.sendto(request, server)
            try:
                while True:
                    data, _ = sock.recvfrom(2048)
                    result = parse_response(data, transaction_id)
                    if result:
                        ip, port = result
                        print(f"{ip}:{port}")
                        return
            except TimeoutError:
                print("Nincs válasz, újraküldés", file=sys.stderr)
    sys.exit(f"Nem jött válasz {MAX_TRIES} próbálkozás után")


if __name__ == "__main__":
    main()
