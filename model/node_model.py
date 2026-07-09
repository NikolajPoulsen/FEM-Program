from dataclasses import dataclass


@dataclass
class NodeData:
    id: int
    x: float
    y: float

class NodeModel:
    def __init__(self):
        self.nodes: dict[int, NodeData] = {}
        self._next_id = 1

    def add_node(self, x: float, y: float) -> int:
        node_id = self._next_id
        self.nodes[node_id] = NodeData(id=node_id, x=x, y=y)
        self._next_id += 1
        return node_id

    def clear(self):
        self.nodes.clear()
        self._next_id = 1
