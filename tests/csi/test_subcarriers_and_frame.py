import numpy as np
import pytest

from csi.domain import subcarriers
from csi.domain.csi_frame import CsiFrame
from csi.domain.node_id import NodeId
from tests.csi.factories import frame


# Ordinea k in buffer
def test_buffer_order_is_0_to_31_then_minus_32_to_minus_1():
    assert list(subcarriers.BUFFER_INDICES[:3]) == [0, 1, 2]
    assert subcarriers.BUFFER_INDICES[31] == 31
    assert subcarriers.BUFFER_INDICES[32] == -32
    assert subcarriers.BUFFER_INDICES[63] == -1


# Cele 52 subpurtatoare, ordine k
def test_data_subcarriers_are_the_52_lltf_tones_in_k_order():
    iq = subcarriers.BUFFER_INDICES.astype(float)
    data = frame(iq=iq).data_subcarriers()
    assert data.shape == (subcarriers.DATA_COUNT,)
    assert list(data.real[:2]) == [-26, -25]
    assert list(data.real[24:28]) == [-2, -1, 1, 2]
    assert data.real[-1] == 26
    assert 0 not in data.real


# Tabelele de asezare sunt read-only
def test_layout_arrays_are_read_only():
    with pytest.raises(ValueError):
        subcarriers.DATA_POSITIONS[0] = 0


# Cadru: iq copiat si blocat
def test_frame_iq_is_copied_and_read_only():
    source = np.zeros(64)
    f = frame(iq=source)
    source[0] = 9
    assert f.iq[0] == 0
    with pytest.raises(ValueError):
        f.iq[0] = 1


# Cadru: egalitate pe valori
def test_frames_with_same_values_are_equal():
    assert frame(seq=1) == frame(seq=1)
    assert frame(seq=1) != frame(seq=2)
    assert frame(iq=np.ones(64)) != frame()


# Cadru: campuri invalide respinse
@pytest.mark.parametrize("field, value, error", [
    ("seq", 65536, ValueError), ("seq", -1, ValueError), ("timestamp_us", 1 << 32, ValueError),
    ("rssi_dbm", 128, ValueError), ("seq", 1.5, TypeError), ("seq", True, TypeError), ("seq", None, TypeError),
])
def test_frame_rejects_invalid_fields(field, value, error):
    fields = dict(node_id=NodeId(1), rssi_dbm=-40, seq=0, timestamp_us=0, iq=np.zeros(64))
    with pytest.raises(error):
        CsiFrame(**{**fields, field: value})


# Cadru: forma iq gresita
@pytest.mark.parametrize("iq", [np.zeros(63), np.zeros((2, 64)), []])
def test_frame_rejects_wrong_iq_shape(iq):
    with pytest.raises(ValueError):
        frame(iq=iq)


# Cadru: node_id int simplu respins
def test_frame_rejects_plain_int_node_id():
    with pytest.raises(TypeError):
        CsiFrame(3, -40, 0, 0, np.zeros(64))


# NodeId: valori invalide respinse
@pytest.mark.parametrize("value, error", [
    (-1, ValueError), (256, ValueError), ("3", TypeError), (None, TypeError), (False, TypeError),
])
def test_node_id_rejects_invalid_values(value, error):
    with pytest.raises(error):
        NodeId(value)


# NodeId: limitele 0 si 255
def test_node_id_bounds_are_accepted():
    assert NodeId(0) < NodeId(255)
    assert str(NodeId(7)) == "7"
