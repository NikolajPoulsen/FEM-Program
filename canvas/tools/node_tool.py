from .tool import Tool


class NodeTool(Tool):
    name = "Node"
    pickable_targets = {"plane"}

    def on_left_press(self, actor, x, y):
        if actor is self.canvas.plane_actor:
            node_id = self.canvas.model.add_node(x, y)
            self.canvas.draw_node(node_id, x, y)
            if self.canvas.on_change:
                self.canvas.on_change()