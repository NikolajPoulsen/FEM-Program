from dataclasses import dataclass


@dataclass
class BeamData:
    id: int
    node_id1: int
    node_id2: int

class BeamModel:
    def __init__(self):
        self.beams: dict[int, BeamData] = {}
        self._next_id = 1

    def add_beam(self, node_id1: int, node_id2: int) -> int:
        beam_id = self._next_id

        new_beam = BeamData(id=beam_id, node_id1=node_id1, node_id2=node_id2)
        self.beams[beam_id] = new_beam

        self._next_id += 1
        return beam_id

    def clear(self):
        self.beams.clear()
        self._next_id = 1
