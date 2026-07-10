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

            node = self.canvas.node_model.nodes[node_id]
            node.x = x
            node.y = y

            self.canvas.move_node_actor(node_id, x, y)
            self.canvas.render()

        elif getattr(self.canvas, "dragging_beam_id", None) is not None:
            beam_id  = self.canvas.dragging_beam_id

            beam = self.canvas.beam_model.beams[beam_id]
            node1 = self.canvas.node_model.nodes[beam.node_id1]
            node2 = self.canvas.node_model.nodes[beam.node_id2]

            dx = x - self.last_x
            dy = y - self.last_y

            node1.x += dx
            node1.y += dy
            self.canvas.move_node_actor(node1.id, node1.x, node1.y)

            node2.x += dx
            node2.y += dy
            self.canvas.move_node_actor(node2.id, node2.x, node2.y)

            self.last_x = x
            self.last_y = y

            self.canvas.render()

    def on_hover(self, actor, x, y):
        if actor is self.canvas.plane_actor or actor is None:
            self.canvas.set_hovered(None)
            return

        node_id = self.canvas.actor_to_node.get(actor)
        if node_id is not None:
            self.canvas.set_hovered("node", node_id)
            return

        beam_id = self.canvas.actor_to_beam.get(actor)
        if beam_id is not None:
            self.canvas.set_hovered("beam", beam_id)
            return