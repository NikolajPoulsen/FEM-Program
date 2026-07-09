from .tool import Tool


class BeamTool(Tool):
    name = "Beam"
    pickable_targets = {"node"}

    def __init__(self, canvas):
        super().__init__(canvas)
        self.pending_node = None

    def on_left_press(self, actor, x, y):
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
        #TODO: Add highlight til knuden musen er over
        pass