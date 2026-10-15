import argparse
import threading
import time

import serial

from csi.packets import BAUD_RATE, DATA_DIR, PacketStream, save_recording

READ_BYTES = 256
READ_TIMEOUT_S = 0.1


def read_port(port, stop, packets):
    try:
        connection = serial.Serial(port, BAUD_RATE, timeout=READ_TIMEOUT_S)
        print(f"[+] Conectat la {port} @ {BAUD_RATE} baud")
    except Exception as error:
        print(f"[!] Eroare conectare la {port}: {error}")
        return
    stream = PacketStream()
    while not stop.is_set():
        raw = connection.read(READ_BYTES)
        if raw:
            packets.extend(stream.feed(raw))
    connection.close()


def main():
    parser = argparse.ArgumentParser(description="Captură date CSI reale de pe 3 noduri ESP32")
    parser.add_argument("--p1", default="/dev/ttyUSB0", help="Port nod 1")
    parser.add_argument("--p2", default="/dev/ttyUSB1", help="Port nod 2")
    parser.add_argument("--p3", default=None, help="Port nod 3 (optional, daca e in priza)")
    parser.add_argument("--duration", type=float, default=20.0, help="Durata capturii în secunde")
    parser.add_argument("--out", default=DATA_DIR / "capture_real.npz", help="Fișier salvare .npz")
    args = parser.parse_args()

    print(f"[*] Lansare captură serială pe {args.duration} secunde...")
    ports = [port for port in (args.p1, args.p2, args.p3) if port and port.lower() != "none"]
    stop = threading.Event()
    packets_by_port = [[] for _ in ports]
    threads = [
        threading.Thread(target=read_port, args=(port, stop, packets))
        for port, packets in zip(ports, packets_by_port)
    ]
    for thread in threads:
        thread.start()

    try:
        time.sleep(args.duration)
    except KeyboardInterrupt:
        print("\n[!] Oprire forțată de utilizator.")

    stop.set()
    for thread in threads:
        thread.join()

    print(f"[+] Captură finalizată! Total pachete recepționate: {sum(len(p) for p in packets_by_port)}")
    save_recording(args.out, packets_by_port)
    print(f"[+] Date salvate în: {args.out}")


if __name__ == "__main__":
    main()
