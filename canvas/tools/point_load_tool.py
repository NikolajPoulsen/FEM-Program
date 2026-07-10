from .tool import Tool


class PointLoadTool(Tool):
    name = "PointLoad"
    pickable_targets = {"node", "plane"}

    def on_left_press(self, actor, x, y):
        node_id = self.canvas.actor_to_node.get(actor)

        if node_id is not None:
            self.canvas.draw_load(node_id=node_id, l_type="point_load")

            if self.canvas.on_change:
                self.canvas.on_change()

    def on_hover(self, actor, x, y):
        if actor is self.canvas.plane_actor or actor is None:
            self.canvas.set_hovered(None)
            return

        node_id = self.canvas.actor_to_node.get(actor)
        if node_id is not None:
            self.canvas.set_hovered("node", node_id)
            return