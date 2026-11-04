"""Primeste pachetele UDP de la placa si afiseaza campurile. Oprire: Ctrl+C.
Utilizare: python3 asculta.py [numar_pachete]"""
import socket
import struct
import sys

PORT = 5005
limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", PORT))
print("Ascult pe UDP %d ..." % PORT, flush=True)
count = 0
try:
    while limit is None or count < limit:
        data, addr = s.recvfrom(2048)
        if len(data) != 138:
            print("lungime neasteptata:", len(data))
            continue
        magic, node, rssi, ts, seq = struct.unpack("<HBbIH", data[:10])
        print("de la %s | magic=0x%04X nod=%d rssi=%d dBm ts=%d us seq=%d | csi[0:8]=%s"
              % (addr[0], magic, node, rssi, ts, seq, data[10:18].hex(" ")))
        count += 1
except KeyboardInterrupt:
    pass
