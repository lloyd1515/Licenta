import struct

import numpy as np

from csi.domain.csi_frame import CsiFrame
from csi.domain.node_id import NodeId


# Pachet v1 fara cod productie
def wire_packet(node_id=3, rssi=-40, timestamp_us=1000, seq=7, pairs=None, magic=0xA55A):
    pairs = [(0, 0)] * 64 if pairs is None else pairs
    body = bytes(b & 0xFF for q, i in pairs for b in (q, i))
    return struct.pack("<HBbIH", magic, node_id, rssi, timestamp_us, seq) + body


# CsiFrame de test rapid
def frame(node=3, seq=0, timestamp_us=0, rssi=-40, iq=None):
    return CsiFrame(NodeId(node), rssi, seq, timestamp_us, np.zeros(64) if iq is None else iq)
