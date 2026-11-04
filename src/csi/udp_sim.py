import argparse
import socket
import time

import numpy as np

from csi.packets import Packet, UDP_PORT, encode_packet
from csi.room import LINKS, link_name
from csi.simulator import make_trajectory, simulate_csi

INT8_PEAK = 40
SIMULATED_RSSI_DBM = -45
MICROSECONDS_PER_SECOND = 1_000_000
SEQ_MODULO = 1 << 16
TIMESTAMP_MODULO = 1 << 32


def simulated_packets(seed=0):
    simulated = simulate_csi(make_trajectory(), seed=seed)
    peak = max(
        max(np.abs(csi.real).max(), np.abs(csi.imag).max()) for csi in simulated.csi_by_link.values()
    )
    scale = INT8_PEAK / peak
    rows = []
    for index, time_s in enumerate(simulated.trajectory.times_s):
        timestamp_us = int(time_s * MICROSECONDS_PER_SECOND) % TIMESTAMP_MODULO
        for link in LINKS:
            csi = simulated.csi_by_link[link_name(link)][index] * scale
            receiver = link[1]
            rows.append((time_s, Packet(receiver, SIMULATED_RSSI_DBM, timestamp_us, index % SEQ_MODULO, csi)))
    return rows


def send(host, port, speed=1.0, seed=0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    start_s = time.monotonic()
    sent = 0
    try:
        for time_s, packet in simulated_packets(seed):
            delay_s = start_s + time_s / speed - time.monotonic()
            if delay_s > 0:
                time.sleep(delay_s)
            sock.sendto(encode_packet(packet), (host, port))
            sent += 1
    finally:
        sock.close()
    return sent


def main():
    parser = argparse.ArgumentParser(description="Simulare 3 noduri ESP32 care trimit pachete CSI prin UDP")
    parser.add_argument("--host", default="127.0.0.1", help="Adresa receptorului")
    parser.add_argument("--port", type=int, default=UDP_PORT, help="Port UDP destinație")
    parser.add_argument("--speed", type=float, default=1.0, help="Factor de accelerare a timpului simulat")
    parser.add_argument("--seed", type=int, default=0, help="Seed pentru zgomotul simulat")
    args = parser.parse_args()

    print(f"[*] Trimitere scenariu simulat (stat, mers, cădere) către {args.host}:{args.port}...")
    try:
        sent = send(args.host, args.port, args.speed, args.seed)
    except KeyboardInterrupt:
        print("\n[!] Oprire forțată de utilizator.")
        return
    print(f"[+] Pachete trimise: {sent}")


if __name__ == "__main__":
    main()
