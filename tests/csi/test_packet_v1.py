import numpy as np
import pytest

from csi.contract import packet_v1
from csi.domain.node_id import NodeId
from tests.csi.factories import wire_packet


# Pachet: 138 octeti ca firmware
def test_packet_is_138_bytes_like_the_firmware_struct():
    assert packet_v1.PACKET_BYTES == 138
    assert packet_v1.HEADER.size == 10


# Pachet: octeti cunoscuti, antet corect
def test_golden_bytes_decode_to_known_header():
    data = bytes.fromhex("5aa5" "03" "d8" "e8030000" "0700") + bytes(128)
    frame = packet_v1.decode(data)
    assert (frame.node_id, frame.rssi_dbm, frame.timestamp_us, frame.seq) == (NodeId(3), -40, 1000, 7)


# Pachet: perechea este (Q, I)
def test_each_pair_is_imaginary_then_real():
    pairs = [(3, 4)] + [(0, 0)] * 63
    frame = packet_v1.decode(wire_packet(pairs=pairs))
    assert frame.iq[0] == pytest.approx(4 + 3j)
    assert frame.amplitude[0] == pytest.approx(5.0)
    assert frame.phase[0] == pytest.approx(np.arctan2(3, 4))


# Pachet: int8 negativ pastreaza semnul
def test_negative_int8_values_keep_their_sign():
    pairs = [(-128, -1)] + [(0, 0)] * 63
    frame = packet_v1.decode(wire_packet(pairs=pairs))
    assert frame.iq[0] == pytest.approx(-1 - 128j)


# Pachet: lungime gresita respinsa
@pytest.mark.parametrize("data", [b"", bytes(137), bytes(139), wire_packet()[:-1]])
def test_wrong_length_is_rejected(data):
    assert packet_v1.decode(data) is None


# Pachet: magic gresit respins
def test_wrong_magic_is_rejected():
    assert packet_v1.decode(wire_packet(magic=0x5AA5)) is None
