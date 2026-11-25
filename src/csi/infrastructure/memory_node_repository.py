from csi.domain.node import Node
from csi.domain.node_id import NodeId


# Depozit de noduri in memorie
class InMemoryNodeRepository:
    # Pornire cu depozit gol
    def __init__(self):
        self._nodes: dict[NodeId, Node] = {}

    # Nodul dupa ID
    def get(self, node_id):
        return self._nodes.get(node_id)

    # Inlocuieste nodul, dict nou
    def save(self, node):
        self._nodes = {**self._nodes, node.node_id: node}

    # Toate nodurile, ordinea descoperirii
    def all(self):
        return tuple(self._nodes.values())
