from .tool import Tool


class SelectTool(Tool):
    name = "Select"
    pickable_targets = {"plane", "node", "beam"}

    def __init__(self, canvas):
        super().__init__(canvas)
        self.last_x = None
        self.last_y = None

    def on_left_press(self, actor, x, y):
        if actor is self.canvas.plane_actor or actor is None:
            self.canvas.set_selected(None)
            self.canvas.dragging_node_id = None
            self.canvas.dragging_beam_id = None
            return

        node_id = self.canvas.actor_to_node.get(actor)
        if node_id is not None:
            self.canvas.set_selected("node", node_id)
            self.canvas.dragging_node_id = node_id
            return

        beam_id = self.canvas.actor_to_beam.get(actor)
        if beam_id is not None:
            self.canvas.set_selected("beam", beam_id)
            self.canvas.dragging_beam_id = beam_id
            return

    def on_left_release(self, obj, event):
        if self.canvas.dragging_node_id is not None or self.canvas.dragging_beam_id is not None:
            self.canvas.dragging_node_id = None
            self.canvas.dragging_beam_id = None
            if self.canvas.on_change:
                self.canvas.on_change()

        self.last_x = None
        self.last_y = None

    def on_drag(self, actor, x, y):
        if self.last_x is None or self.last_y is None:
            self.last_x = x
            self.last_y = y
            return

        if getattr(self.canvas, "dragging_node_id", None) is not None:
            node_id = self.canvas.dragging_node_id
            self.canvas.model.nodes[node_id] = (x, y)
            self.canvas.move_node_actor(node_id, x, y)

            self.canvas.render()
        elif getattr(self.canvas, "dragging_beam_id", None) is not None:
            node1_id, node2_id = self.canvas.dragging_beam_id

            dx = x - self.last_x
            dy = y - self.last_y

            # Flyt knude 1
            x1, y1 = self.canvas.model.nodes[node1_id]
            new_x1, new_y1 = x1 + dx, y1 + dy
            self.canvas.model.nodes[node1_id] = (new_x1, new_y1)
            self.canvas.move_node_actor(node1_id, new_x1, new_y1)

            # Flyt knude 2
            x2, y2 = self.canvas.model.nodes[node2_id]
            new_x2, new_y2 = x2 + dx, y2 + dy
            self.canvas.model.nodes[node2_id] = (new_x2, new_y2)
            self.canvas.move_node_actor(node2_id, new_x2, new_y2)

            self.last_x = x
            self.last_y = y

            self.canvas.render()