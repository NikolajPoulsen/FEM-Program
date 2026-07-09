import pyvista as pv
import vtk
import numpy as np
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor

from .tools import *
from .canvas_data import NodeActors, BeamActors


NORMAL_COLOR = "black"
HIGHLIGHT_COLOR = "blue"
SELECTED_COLOR = "orange"

class DrawingCanvas(QtInteractor):
    def __init__(self, model, on_change=None):
        super().__init__()
        self.current_tool = SelectTool(self)
        self.model = model
        self.on_change = on_change
        self.left_pressed = False

        self.enable_parallel_projection()
        self.set_background("white")
        self.view_xy()

        style = vtk.vtkInteractorStyleImage()
        self._set_interactor_style(style)

        plane = pv.Plane(center=(0, 0, 0), i_size=20, j_size=20,
                         i_resolution=20, j_resolution=20)
        self.plane_actor = self.add_mesh(
            plane, color="white", show_edges=True, edge_color="#dddddd",
        )

        self._picker = vtk.vtkCellPicker()
        self._picker.SetTolerance(0.01)

        #TODO: Husk at slette nodes, beams, osv herfra når den logik findes
        self.node_actors: dict[int, NodeActors] = {}
        self.actor_to_node: dict[object, int] = {}
        self.beam_actors: dict[tuple[int, int], BeamActors] = {}
        self.actor_to_beam: dict[object, tuple[int, int]] = {}

        self.dragging_node_id: int | None = None
        self.dragging_beam_id: int | None = None
        self.selected_item: tuple[str, object] | None = None
        self.hovered_item: tuple[str, object] | None = None

        self._apply_pickable_state()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.left_pressed = True
            result = self._pick()
            if result:
                actor, x, y = result
                self.current_tool.on_left_press(actor, x, y)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        result = self._pick()
        if result is None:
            return

        actor, x, y = result

        if self.left_pressed:
            self.current_tool.on_drag(actor, x, y)
        else:
            self.current_tool.on_hover(actor, x, y)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.left_pressed = False
            self.current_tool.on_left_release(event, None)

    def set_current_tool(self, tool):
        self.current_tool = tool(self)
        #print(f"Current tool: {tool.name}")
        self._apply_pickable_state()

    def _apply_pickable_state(self) -> None:
        targets = self.current_tool.pickable_targets

        self.plane_actor.SetPickable("plane" in targets)

        node_pickable = "node" in targets
        for na in self.node_actors.values():
            na.point_actor.SetPickable(node_pickable)

        beam_pickable = "beam" in targets
        for ba in self.beam_actors.values():
            ba.beam_actor.SetPickable(beam_pickable)

        self.dragging_node_id = None
        self.render()

    def _pick(self):
        x, y = self.iren.interactor.GetEventPosition()
        hit = self._picker.Pick(x, y, 0, self.renderer)

        if not hit:
            return None
        wx, wy, _ = self._picker.GetPickPosition()

        return self._picker.GetActor(), wx, wy

    def set_hovered(self, item_type: str | None, item_id: object = None):
        new_hover = (item_type, item_id) if item_type and item_id is not None else None

        if self.hovered_item == new_hover:
            return

        if self.hovered_item is not None:
            old_type, old_id = self.hovered_item
            if self.hovered_item == self.selected_item:
                self._set_item_color(old_type, old_id, SELECTED_COLOR)
            else:
                self._set_item_color(old_type, old_id, NORMAL_COLOR)

        self.hovered_item = new_hover

        if self.hovered_item is not None:
            new_type, new_id = self.hovered_item
            if self.hovered_item != self.selected_item:
                self._set_item_color(new_type, new_id, HIGHLIGHT_COLOR)

        self.render()

    def set_selected(self, item_type: str | None, item_id: object = None):
        if self.selected_item is not None:
            old_type, old_id = self.selected_item
            if self.selected_item == self.hovered_item:
                self._set_item_color(old_type, old_id, HIGHLIGHT_COLOR)
            else:
                self._set_item_color(old_type, old_id, NORMAL_COLOR)

        if item_type is None or item_id is None:
            self.selected_item = None
        else:
            self.selected_item = (item_type, item_id)

        if self.selected_item is not None:
            new_type, new_id = self.selected_item
            self._set_item_color(new_type, new_id, SELECTED_COLOR)

        if self.on_change:
            self.on_change()

        self.render()

    def _set_item_color(self, item_type: str, item_id: object, color: str):
        actor = None

        if item_type == "node" and item_id in self.node_actors:
            actor = self.node_actors[item_id].point_actor
        elif item_type == "beam" and item_id in self.beam_actors:
            actor = self.beam_actors[item_id].beam_actor

        if actor is not None:
            actor.GetProperty().SetColor(pv.Color(color).float_rgb)

    def draw_node(self, node_id: int, x: float, y: float):
        point_mesh = pv.PolyData(np.array([[x, y, 0.1]]))
        point_actor = self.add_mesh(
            point_mesh, color=NORMAL_COLOR, point_size=14,
            render_points_as_spheres=True, lighting=False,
            style="points", pickable=("node" in self.current_tool.pickable_targets),
        )

        label_mesh = pv.PolyData(np.array([[x, y, 0.0]]))
        label_actor = self.add_point_labels(
            label_mesh, [str(node_id)],
            font_size=14, text_color="blue", shape=None, always_visible=True,
        )

        self.node_actors[node_id] = NodeActors(point_actor, point_mesh, label_actor, label_mesh)
        self.actor_to_node[point_actor] = node_id

    def draw_beam(self, node_id1: int, node_id2: int):
        key = tuple(sorted((node_id1, node_id2)))
        if key in self.beam_actors:
            return

        x1, y1 = self.model.nodes[node_id1]
        x2, y2 = self.model.nodes[node_id2]

        beam_mesh = pv.Line([x1, y1, 0.04], [x2, y2, 0.04])
        beam_actor = self.add_mesh(
            beam_mesh, color=NORMAL_COLOR, line_width=4,
            pickable=("beam" in self.current_tool.pickable_targets)
        )

        self.beam_actors[key] = BeamActors(beam_actor, beam_mesh)
        self.actor_to_beam[beam_actor] = key

        self.hovered_item = None

    def move_node_actor(self, node_id: int, x: float, y: float):
        na = self.node_actors[node_id]

        na.point_mesh.points[0] = [x, y, 0.1]
        na.point_mesh.Modified()

        na.label_mesh.points[0] = [x, y, 0.1]
        na.label_mesh.Modified()

        for (n1, n2) in self.model.beams:
            if node_id == n1 or node_id == n2:
                self.update_beam_geometry(n1, n2)

    def update_beam_geometry(self, node_id1: int, node_id2: int):
        key = tuple(sorted((node_id1, node_id2)))
        beam = self.beam_actors.get(key)
        if not beam: return

        x1, y1 = self.model.nodes[node_id1]
        x2, y2 = self.model.nodes[node_id2]

        beam.beam_mesh.points[0] = [x1, y1, 0.04]
        beam.beam_mesh.points[1] = [x2, y2, 0.04]
        beam.beam_mesh.Modified()

    def redraw_all(self):
        for na in self.node_actors.values():
            self.remove_actor(na.point_actor)
            self.remove_actor(na.label_actor)

        for ba in self.beam_actors.values():
            self.remove_actor(ba.beam_actor)

        self.node_actors.clear()
        self.actor_to_node.clear()

        self.beam_actors.clear()
        self.actor_to_beam.clear()

        self.selected_item = None
        self.hovered_item = None

        for node_id, (x, y) in self.model.nodes.items():
            self.draw_node(node_id, x, y)

        for (n1, n2) in self.model.beams:
            self.draw_beam(n1, n2)

    def _set_interactor_style(self, style):
        self.iren.style = style
        self.iren.interactor.SetInteractorStyle(style)