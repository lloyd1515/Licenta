"""Asculta UDP 5005 si verifica pachetele nodurilor cu decode din src/csi/contract/packet_v1.py.
Utilizare (din radacina repository-ului): .venv/bin/python docs/StatusLicenta/9Nov2026/unelte/verifica_udp.py <secunde>
Afiseaza: pachete pe nod, seq lipsa, RSSI, indicii mereu 0 si amplitudinea medie pe indice."""
import collections, socket, sys, time
# sys.path[0] = acest director, care are dis.py (ar ascunde modulul standard dis); il inlocuim cu src/
sys.path[0] = str(__import__("pathlib").Path(__file__).resolve().parents[4] / "src")
import numpy as np
from csi.contract.packet_v1 import decode as parse_packet, PACKET_BYTES

secunde = float(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", 5005))
sock.settimeout(0.5)
brute, invalide = 0, 0
per_nod = collections.defaultdict(list)
surse = collections.Counter()
start = time.time()
while time.time() - start < secunde:
    try:
        data, adr = sock.recvfrom(2048)
    except socket.timeout:
        continue
    brute += 1
    p = parse_packet(data)
    if p is None:
        invalide += 1
        continue
    surse[(adr[0], p.node_id.value)] += 1
    per_nod[p.node_id.value].append((time.time(), p))
print(f"datagrame: {brute}, invalide: {invalide}, marime asteptata {PACKET_BYTES} B")
for (ip, nod), n in sorted(surse.items()):
    print(f"  {ip} -> node_id {nod}: {n} pachete")
for nod, lst in sorted(per_nod.items()):
    seq = np.array([p.seq for _, p in lst], dtype=np.int64)
    pasi = np.diff(seq) % 65536
    lipsa = int(np.sum(pasi - 1))
    amp = np.stack([p.amplitude for _, p in lst])
    rssi = np.array([p.rssi_dbm for _, p in lst])
    durata = lst[-1][0] - lst[0][0]
    zero01 = np.mean((amp[:, 0] == 0) & (amp[:, 1] == 0))
    nule = [i for i in range(64) if np.all(amp[:, i] == 0)]
    print(f"nod {nod}: {len(lst)} pachete in {durata:.1f} s = {len(lst)/max(durata,1e-9):.1f} pachete/s; "
          f"seq lipsa: {lipsa} ({100*lipsa/max(lipsa+len(lst),1):.1f}%)")
    print(f"  RSSI: medie {rssi.mean():.1f} dBm, min {rssi.min()}, max {rssi.max()}")
    print(f"  k=0 si k=1 zero in {100*zero01:.0f}% din pachete; indici mereu 0: {nule}")
    print(f"  amplitudine medie pe indice (0..63):", " ".join(f"{v:.0f}" for v in amp.mean(axis=0)))
