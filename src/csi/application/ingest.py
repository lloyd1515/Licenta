from dataclasses import dataclass

from csi.contract import packet_v1
from csi.domain.csi_frame import CsiFrame
from csi.domain.events import DomainEvent
from csi.domain.node import Node
from csi.domain.node_id import NodeId
from csi.domain.repository import NodeRepository


# Rezultatul unui lot primit
@dataclass(frozen=True)
class IngestResult:
    frames: tuple[CsiFrame, ...] = ()
    nodes: tuple[Node, ...] = ()
    events: tuple[DomainEvent, ...] = ()


# Caz utilizare: datagrame in cadre
class IngestFrames:
    # Depozit noduri si filtru optional
    def __init__(self, repository: NodeRepository, only_node: NodeId | None = None):
        self._repository = repository
        self._only_node = only_node

    # Decodeaza, actualizeaza noduri, aduna evenimente
    def __call__(self, datagrams):
        frames, events, touched = [], [], {}
        for data in datagrams:
            frame = packet_v1.decode(data)
            if frame is None or (self._only_node is not None and frame.node_id != self._only_node):
                continue
            node = self._repository.get(frame.node_id) or Node(frame.node_id)
            node, new_events = node.record(frame)
            self._repository.save(node)
            frames.append(frame)
            events.extend(new_events)
            touched[node.node_id] = node
        return IngestResult(tuple(frames), tuple(touched.values()), tuple(events))
