import pyvista as pv
import vtk
import numpy as np
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor

import math

from .tools import *
from .canvas_data import NodeActors, BeamActors, ConstraintActors, LoadActors
from model import BeamModel, NodeModel, DOF, LoadCase


NORMAL_COLOR = "black"
HIGHLIGHT_COLOR = "blue"
SELECTED_COLOR = "orange"

class DrawingCanvas(QtInteractor):
    def __init__(self, on_change=None):
        super().__init__()
        self.current_tool = SelectTool(self)
        self.beam_model = BeamModel()
        self.node_model = NodeModel()
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

        self.constraint_actors: dict[int, ConstraintActors] = {}
        self.load_actors: dict[int, LoadActors] = {}

        self.dragging_node_id: int | None = None
        self.dragging_beam_id: int | None = None
        self.selected_item: tuple[str, object] | None = None
        self.hovered_item: tuple[str, object] | None = None

        self._apply_pickable_state()

        self.camera.AddObserver(vtk.vtkCommand.ModifiedEvent, self._update_scale)

    def _update_scale(self, caller=None, event=None):
        scale = self.camera.GetParallelScale() * 0.08

        for ca in self.constraint_actors.values():
            ca.actor.SetScale(scale, scale, scale)

        for key, la in self.load_actors.items():
            if la.l_type == "point_load":
                la.actor.SetScale(scale, scale, scale)
            elif la.l_type == "line_load":
                beam_id = int(key.split("_")[1])
                beam = self.beam_model.beams[beam_id]
                n1 = self.node_model.nodes[beam.node_id1]
                n2 = self.node_model.nodes[beam.node_id2]

                L = math.sqrt((n2.x - n1.x) ** 2 + (n2.y - n1.y) ** 2)

                la.actor.SetScale(L, scale, 1.0)

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

    def draw_node(self, node_id: int, x: float, y: float) -> None:
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

    def draw_beam(self, beam_id: int) -> None:
        if beam_id in self.beam_actors:
            return

        beam = self.beam_model.beams[beam_id]
        node1 = self.node_model.nodes[beam.node_id1]
        node2 = self.node_model.nodes[beam.node_id2]

        beam_mesh = pv.Line([node1.x, node1.y, 0.04], [node2.x, node2.y, 0.04])
        beam_actor = self.add_mesh(
            beam_mesh, color=NORMAL_COLOR, line_width=4,
            pickable=("beam" in self.current_tool.pickable_targets)
        )

        self.beam_actors[beam_id] = BeamActors(beam_actor, beam_mesh)
        self.actor_to_beam[beam_actor] = beam_id

        self.hovered_item = None

    def draw_load(self, node_id: int | None = None, beam_id: int | None = None, l_type: str = "") -> None:
        load_key = f"node_{node_id}" if node_id is not None else f"beam_{beam_id}"

        if load_key in self.load_actors:
            return

        z = 0.08

        if l_type == "point_load" and node_id is not None:
            node = self.node_model.nodes[node_id]

            mesh = pv.Arrow(start=(0, 1, 0), direction=(0, -1, 0), scale=1.0)
            color = "green"

            actor = self.add_mesh(mesh, color=color, lighting=False, pickable=False, render=False)
            actor.SetPosition(node.x, node.y, z+0.005)

            self.load_actors[load_key] = LoadActors(actor, mesh, l_type)

        elif l_type == "line_load" and beam_id is not None:
            points = np.array([
                [0, 0, 0],  # Bund-venstre
                [1.0, 0, 0],  # Bund-højre
                [1.0, 1.0, 0],  # Top-højre
                [0, 1.0, 0]  # Top-venstre
            ])
            faces = np.array([4, 0, 1, 2, 3])
            mesh = pv.PolyData(points, faces)
            color = "orange"

            actor = self.add_mesh(mesh, color=color, opacity=0.4, lighting=False, pickable=False, render=False)

            self.load_actors[load_key] = LoadActors(actor, mesh, l_type)

            self.update_line_load_geometry(beam_id)

        self._update_scale()
        self.render()

    def draw_constraint(self, node_id: int, c_type: str) -> None:
        if node_id in self.constraint_actors:
            return

        node = self.node_model.nodes[node_id]
        z = 0.06

        if c_type == "fixed":
            mesh = pv.Plane(center=(0, -0.5, 0), i_size=1.0, j_size=1.0)
            color = "gray"

        elif c_type == "pinned":
            points = np.array([
                [0.0, 0.0, 0.0],
                [-0.5, -1.0, 0.0],
                [0.5, -1.0, 0.0]
            ])
            faces = np.array([3, 0, 1, 2])
            mesh = pv.PolyData(points, faces)
            color = "gray"

        elif c_type == "roller":
            mesh = pv.Polygon(center=(0, -0.5, 0), radius=0.5, n_sides=20)
            color = "gray"
        else:
            return

        actor = self.add_mesh(
            mesh, color=color, lighting=False, render=False, pickable=("constraint" in self.current_tool.pickable_targets)
        )

        actor.SetPosition(node.x, node.y, z)
        self.constraint_actors[node_id] = ConstraintActors(actor, mesh, c_type)
        self._update_scale()
        self.render()

    def move_node_actor(self, node_id: int, x: float, y: float):
        na = self.node_actors[node_id]
        if not na: return

        na.point_mesh.points[0] = [x, y, 0.1]
        na.point_mesh.Modified()

        na.label_mesh.points[0] = [x, y, 0.1]
        na.label_mesh.Modified()

        for beam in self.beam_model.beams.values():
            if node_id == beam.node_id1 or node_id == beam.node_id2:
                self.update_beam_geometry(beam.id)

                if f"beam_{beam.id}" in self.load_actors:
                    self.update_line_load_geometry(beam.id)

        if node_id in self.constraint_actors:
            ca = self.constraint_actors[node_id]
            ca.actor.SetPosition(x, y, 0.06)

        if f"node_{node_id}" in self.load_actors:
            self.load_actors[f"node_{node_id}"].actor.SetPosition(x, y, 0.085)

    def update_beam_geometry(self, beam_id: int):
        beam_actor_data = self.beam_actors.get(beam_id)
        if not beam_actor_data: return

        beam = self.beam_model.beams[beam_id]
        node1 = self.node_model.nodes[beam.node_id1]
        node2 = self.node_model.nodes[beam.node_id2]

        beam_actor_data.beam_mesh.points[0] = [node1.x, node1.y, 0.04]
        beam_actor_data.beam_mesh.points[1] = [node2.x, node2.y, 0.04]
        beam_actor_data.beam_mesh.Modified()

    def update_line_load_geometry(self, beam_id: int):
        load_key = f"beam_{beam_id}"
        if load_key not in self.load_actors:
            return

        la = self.load_actors[load_key]
        beam = self.beam_model.beams[beam_id]
        n1 = self.node_model.nodes[beam.node_id1]
        n2 = self.node_model.nodes[beam.node_id2]

        dx = n2.x - n1.x
        dy = n2.y - n1.y
        L = math.sqrt(dx ** 2 + dy ** 2)
        angle = math.degrees(math.atan2(dy, dx))

        la.actor.SetPosition(n1.x, n1.y, 0.08)
        la.actor.SetOrientation(0, 0, angle)

        current_y_scale = self.camera.GetParallelScale() * 0.08
        la.actor.SetScale(L, current_y_scale, 1.0)

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

        self.constraint_actors.clear()
        self.load_actors.clear()

        self.selected_item = None
        self.hovered_item = None

        for node in self.node_model.nodes.values():
            self.draw_node(node.id, node.x, node.y)
            if node.is_constrained:
                #TODO: Opdater så dette er mere robust ved brug af constraint model
                if DOF.UX in node.locked_dofs and DOF.UY in node.locked_dofs and DOF.RZ in node.locked_dofs:
                    self.draw_constraint(node.id, "fixed")
                elif DOF.UX in node.locked_dofs and DOF.UY in node.locked_dofs:
                    self.draw_constraint(node.id, "pinned")
                elif DOF.UY in node.locked_dofs:
                    self.draw_constraint(node.id, "roller")

        for beam in self.beam_model.beams.values():
            self.draw_beam(beam.id)

    def _set_interactor_style(self, style):
        self.iren.style = style
        self.iren.interactor.SetInteractorStyle(style)