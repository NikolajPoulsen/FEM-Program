from .tool import Tool


class BeamTool(Tool):
    name = "Beam"
    pickable_targets = {"plane", "node"}

    def __init__(self, canvas):
        super().__init__(canvas)
        self.pending_node = None

    def on_left_press(self, actor, x, y):
        #TODO: Funktionalitet så man kan oprette beam uden nodes
        node_id = self.canvas.actor_to_node.get(actor)
        if node_id is None:
            return

        if self.pending_node is None:
            self.pending_node = node_id
            self.canvas.set_selected("node", node_id)
        else:
            node_id1 = self.pending_node
            node_id2 = node_id

            if node_id1 != node_id2:
                self.canvas.model.add_beam(node_id1, node_id2)
                self.canvas.draw_beam(node_id1, node_id2)
                self.canvas.set_selected(None)
                if self.canvas.on_change:
                    self.canvas.on_change()

            self.pending_node = None

    def on_hover(self, actor, x, y):
        if actor is self.canvas.plane_actor or actor is None:
            self.canvas.set_hovered(None)
            return

        node_id = self.canvas.actor_to_node.get(actor)
        if node_id is not None:
            self.canvas.set_hovered("node", node_id)
            return