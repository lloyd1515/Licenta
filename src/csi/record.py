import argparse
import socket
import time

from csi.packets import DATA_DIR, UDP_PORT, UDP_RECEIVE_BYTES, open_udp_socket, parse_datagram, save_recording

READ_TIMEOUT_S = 0.1


def receive(sock, duration_s):
    packets_by_node = {}
    end_s = time.monotonic() + duration_s
    try:
        while time.monotonic() < end_s:
            try:
                data = sock.recv(UDP_RECEIVE_BYTES)
            except socket.timeout:
                continue
            for packet in parse_datagram(data):
                packets_by_node.setdefault(packet.node_id, []).append(packet)
    except KeyboardInterrupt:
        print("\n[!] Oprire forțată de utilizator.")
    return [packets_by_node[node_id] for node_id in sorted(packets_by_node)]


def main():
    parser = argparse.ArgumentParser(description="Captură date CSI reale de pe 3 noduri ESP32 (UDP)")
    parser.add_argument("--port", type=int, default=UDP_PORT, help="Port UDP de ascultare")
    parser.add_argument("--duration", type=float, default=20.0, help="Durata capturii în secunde")
    parser.add_argument("--out", default=DATA_DIR / "capture_real.npz", help="Fișier salvare .npz")
    args = parser.parse_args()

    try:
        sock = open_udp_socket(args.port, READ_TIMEOUT_S)
    except OSError as error:
        print(f"[!] Eroare deschidere port UDP {args.port}: {error}")
        return
    print(f"[*] Ascultare UDP pe portul {args.port} timp de {args.duration} secunde...")
    try:
        packets_by_node = receive(sock, args.duration)
    finally:
        sock.close()

    print(f"[+] Captură finalizată! Total pachete recepționate: {sum(len(p) for p in packets_by_node)}")
    save_recording(args.out, packets_by_node)
    print(f"[+] Date salvate în: {args.out}")


if __name__ == "__main__":
    main()
