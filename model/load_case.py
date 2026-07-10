from dataclasses import dataclass


@dataclass
class PointLoad:
    id: int
    node_id: int
    fx: float
    fy: float
    mz: float

@dataclass
class LineLoad:
    id: int
    beam_id: int
    qx: float
    qy: float

class LoadCase:
    def __init__(self):
        self.point_load: dict[int, PointLoad] = {}
        self.line_load: dict[int, LineLoad] = {}
        self._next_id = 1

    def add_point_load(self, node_id: int, fx: int, fy: int, mz: int) -> None:
        if node_id is None: return

        load_id = self._next_id
        self.point_load[load_id] = PointLoad(id=load_id, node_id=node_id, fx=fx, fy=fy, mz=mz)
        self._next_id += 1

    def add_line_load(self, beam_id: int, qx: int, qy: int) -> None:
        if beam_id is None: return

        load_id = self._next_id
        self.line_load[load_id] = LineLoad(id=load_id, beam_id=beam_id, qx=qx, qy=qy)
        self._next_id += 1

    def clear(self):
        self.point_load.clear()
        self.line_load.clear()
        self._next_id = 1