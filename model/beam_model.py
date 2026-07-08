class BeamModel:
    def __init__(self):
        self.nodes: dict[int, tuple[float, float]] = {}
        self.beams: set[tuple[int, int]] = set()
        self._next_id = 1

    def add_node(self, x: float, y: float) -> int:
        node_id = self._next_id
        self.nodes[node_id] = (x, y)
        self._next_id += 1
        return node_id

    def add_beam(self, node_id1: int, node_id2: int):
        beam = tuple(sorted((node_id1, node_id2)))
        self.beams.add(beam)
        return beam

    def clear(self):
        self.nodes.clear()
        self.beams.clear()
        self._next_id = 1
