from dataclasses import dataclass, replace

from csi.domain.csi_frame import SEQ_MODULUS, TIMESTAMP_MODULUS, CsiFrame
from csi.domain.events import NodeDiscovered, NodeRestarted
from csi.domain.node_id import NodeId

# Praguri repornire si intarziere
HALF_TIMESTAMP_CYCLE_US = TIMESTAMP_MODULUS // 2
LATE_FRAME_US = 1_000_000


# Agregat: fluxul unui nod
@dataclass(frozen=True)
class Node:
    node_id: NodeId
    frames_received: int = 0
    frames_lost: int = 0
    elapsed_us: int = 0
    last_frame: CsiFrame | None = None

    # Cadru nou, intoarce nod nou
    def record(self, frame):
        if frame.node_id != self.node_id:
            raise ValueError(f"cadrul este de la nodul {frame.node_id}, nu de la {self.node_id}")
        received = self.frames_received + 1
        if self.last_frame is None:
            return replace(self, frames_received=received, last_frame=frame), (NodeDiscovered(self.node_id),)
        step_us = (frame.timestamp_us - self.last_frame.timestamp_us) % TIMESTAMP_MODULUS
        if step_us <= HALF_TIMESTAMP_CYCLE_US:
            lost = (frame.seq - self.last_frame.seq - 1) % SEQ_MODULUS
            advanced = replace(self, frames_received=received, frames_lost=self.frames_lost + lost,
                               elapsed_us=self.elapsed_us + step_us, last_frame=frame)
            return advanced, ()
        if TIMESTAMP_MODULUS - step_us <= LATE_FRAME_US:
            return replace(self, frames_received=received), ()
        return replace(self, frames_received=received, elapsed_us=0, last_frame=frame), (NodeRestarted(self.node_id),)
