from dataclasses import dataclass

from csi.domain.node_id import NodeId


# Eveniment: nod nou vazut
@dataclass(frozen=True)
class NodeDiscovered:
    node_id: NodeId


# Eveniment: nodul a repornit
@dataclass(frozen=True)
class NodeRestarted:
    node_id: NodeId


# Toate evenimentele de domeniu
DomainEvent = NodeDiscovered | NodeRestarted
