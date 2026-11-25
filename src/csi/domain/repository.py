from typing import Protocol

from csi.domain.node import Node
from csi.domain.node_id import NodeId


# Port: depozitul de noduri
class NodeRepository(Protocol):
    # Nodul dupa ID
    def get(self, node_id: NodeId) -> Node | None: ...

    # Salveaza starea nodului
    def save(self, node: Node) -> None: ...

    # Toate nodurile, in ordine
    def all(self) -> tuple[Node, ...]: ...
