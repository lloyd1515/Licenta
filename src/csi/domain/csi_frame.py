from dataclasses import dataclass

import numpy as np

from csi.domain import subcarriers
from csi.domain.node_id import NodeId

# Limitele campurilor din pachet
SEQ_MODULUS = 1 << 16
TIMESTAMP_MODULUS = 1 << 32
RSSI_RANGE_DBM = (-128, 127)


# Obiect-valoare: o masuratoare CSI
@dataclass(frozen=True, eq=False)
class CsiFrame:
    node_id: NodeId
    rssi_dbm: int
    seq: int
    timestamp_us: int
    iq: np.ndarray

    # Valideaza campurile, ingheata iq
    def __post_init__(self):
        if not isinstance(self.node_id, NodeId):
            raise TypeError("node_id trebuie sa fie NodeId")
        _check_range("rssi_dbm", self.rssi_dbm, *RSSI_RANGE_DBM)
        _check_range("seq", self.seq, 0, SEQ_MODULUS - 1)
        _check_range("timestamp_us", self.timestamp_us, 0, TIMESTAMP_MODULUS - 1)
        iq = np.array(self.iq, dtype=np.complex64)
        if iq.shape != (subcarriers.COUNT,):
            raise ValueError(f"iq trebuie sa aiba {subcarriers.COUNT} valori, nu forma {iq.shape}")
        iq.setflags(write=False)
        object.__setattr__(self, "iq", iq)

    # Amplitudinea pe subpurtatoare
    @property
    def amplitude(self):
        return np.abs(self.iq)

    # Faza pe subpurtatoare
    @property
    def phase(self):
        return np.angle(self.iq)

    # Cele 52 subpurtatoare LLTF
    def data_subcarriers(self):
        return self.iq[subcarriers.DATA_POSITIONS]

    # Egalitate pe valori
    def __eq__(self, other):
        if not isinstance(other, CsiFrame):
            return NotImplemented
        return (self.node_id, self.rssi_dbm, self.seq, self.timestamp_us) == (
            other.node_id, other.rssi_dbm, other.seq, other.timestamp_us
        ) and np.array_equal(self.iq, other.iq)

    __hash__ = None


# Verifica int intre limite
def _check_range(name, value, low, high):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} trebuie sa fie int, nu {type(value).__name__}")
    if not low <= value <= high:
        raise ValueError(f"{name} trebuie sa fie intre {low} si {high}, nu {value}")
