import struct

import numpy as np

from csi.domain import subcarriers
from csi.domain.csi_frame import CsiFrame
from csi.domain.node_id import NodeId

# Formatul pachetului v1, 138 octeti
HEADER = struct.Struct("<HBbIH")
MAGIC = 0xA55A
IQ_BYTES = 2 * subcarriers.COUNT
PACKET_BYTES = HEADER.size + IQ_BYTES


# Octeti in CsiFrame sau None
def decode(data):
    if len(data) != PACKET_BYTES:
        return None
    magic, node_id, rssi_dbm, timestamp_us, seq = HEADER.unpack_from(data)
    if magic != MAGIC:
        return None
    pairs = np.frombuffer(data, dtype=np.int8, offset=HEADER.size).astype(np.float32)
    iq = pairs[1::2] + 1j * pairs[0::2]
    return CsiFrame(NodeId(node_id), rssi_dbm, seq, timestamp_us, iq)
